import abc
import collections
from itertools import chain

from schema import Schema

from experta.conditionalelement import ConditionalElement
from experta.conditionalelement import OperableCE
from experta.pattern import Bindable
from experta.utils import freeze, unfreeze


class BaseField(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def validate(self, data):
        """Raise an exception on invalid data."""
        pass


class Field(BaseField):
    NODEFAULT = object()

    def __init__(self, schema_definition, mandatory=False, default=NODEFAULT):
        self.validator = Schema(schema_definition)
        self.mandatory = mandatory
        self.default = default

    def validate(self, data):
        self.validator.validate(unfreeze(data))


class Validable(type):
    def __new__(mcl, name, bases, nmspc):

        # Register fields
        newnamespace = {"__fields__": dict()}
        for base in bases:
            if isinstance(base, Validable):
                for key, value in base.__fields__.items():
                    if key.startswith('_') and key[1:].isdigit():
                        key = int(key[1:])
                    newnamespace["__fields__"][key] = value

        for key, value in nmspc.items():
            if key.startswith('_') and key[1:].isdigit():
                key = int(key[1:])
            if isinstance(value, BaseField):
                newnamespace["__fields__"][key] = value
            else:
                newnamespace[key] = value

        return super(Validable, mcl).__new__(mcl, name, bases, newnamespace)


class Fact(OperableCE, Bindable, dict, metaclass=Validable):
    """Base Fact class"""

    def __new__(cls, *args, **kwargs):
        if '__class__' in kwargs:
            cls = kwargs['__class__']
            del kwargs['__class__']
            assert issubclass(cls, Fact)

        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.__source__ = None
        self.__children__ = []
        factid = None
        if '__factid__' in kwargs:
            factid = kwargs['__factid__']
            del kwargs['__factid__']

        self.update(dict(chain(enumerate(args), kwargs.items())))
        self.__defaults = dict()

        if factid is not None:
            self.__factid__ = factid

    def __missing__(self, key):
        if key not in self.__fields__:
            raise KeyError(key)
        else:
            default = self.__fields__[key].default
            if default is Field.NODEFAULT:
                raise KeyError(key)
            elif key in self.__defaults:
                return self.__defaults[key]
            elif isinstance(default, collections.abc.Callable):
                return self.__defaults.setdefault(key, default())
            else:
                return self.__defaults.setdefault(key, default)

    def __setitem__(self, key, value):
        if self.__factid__ is None:
            super().__setitem__(key, freeze(value))
        else:
            raise RuntimeError("A fact can't be modified after declaration.")

    def validate(self):
        for name, field in self.__fields__.items():
            if name in self:
                try:
                    field.validate(self[name])
                except Exception as exc:
                    raise ValueError(
                        "Invalid value on field %r for fact %r"
                        % (name, self))
            elif field.mandatory:
                raise ValueError(
                    "Mandatory field %r is not defined for fact %r"
                    % (name, self))
            else:
                pass

    def update(self, mapping):
        for k, v in mapping.items():
            self[k] = v

    def as_dict(self):
        """Return a dictionary containing this `Fact` data."""
        d = {k: unfreeze(v)
             for k, v in self.items()
             if not self.is_special(k)}
        if self.__factid__ is not None:
            d['__factid__'] = self.__factid__
        if type(self) is not Fact:
            d['__class__'] = type(self)
        return d

    def copy(self, sub=None, bind=False):
        """Return a copy of this `Fact`."""
        content = [(k, v) for k, v in self.items()]

        if sub is not None:
            for i, tup in enumerate(content):
                while tup[1] in sub.keys():
                    tup = (tup[0], sub[tup[1]])
                content[i] = tup

        intidx = [(k, v) for k, v in content if isinstance(k, int)]
        args = [v for k, v in sorted(intidx)]

        kwargs = {k: v
                  for k, v in content
                  if not isinstance(k, int) and not self.is_special(k, bind)}

        return self.__class__(*args, **kwargs)

    def has_field_constraints(self):
        return any(isinstance(v, ConditionalElement) for v in self.values())

    def has_nested_accessor(self):
        return any(("__" in str(k).strip('__') for k in self.keys()))

    @staticmethod
    def is_special(key, bind=False):
        return (isinstance(key, str)
                and key.startswith('__')
                and key.endswith('__')) and not (bind and key == "__bind__")

    @property
    def __bind__(self):
        return self.get('__bind__', None)

    @__bind__.setter
    def __bind__(self, value):
        super().__setitem__('__bind__', value)

    @property
    def __factid__(self):
        return self.get('__factid__', None)

    @__factid__.setter
    def __factid__(self, value):
        super().__setitem__('__factid__', value)

    @classmethod
    def from_iter(cls, pairs):
        obj = cls()
        obj.update(dict(pairs))
        return obj

    def __str__(self):  # pragma: no cover
        if self.__factid__ is None:
            return "<Undeclared Fact> %r" % self
        else:
            return "<f-%d>" % self.__factid__

    def __repr__(self):  # pragma: no cover
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                (repr(v) if isinstance(k, int) else "{}={!r}".format(k, v)
                 for k, v in self.items()
                 if not self.is_special(k))))

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(frozenset(self.items()))
            return self._hash

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and super().__eq__(other))


class InitialFact(Fact):
    """
    InitialFact
    """
    pass
