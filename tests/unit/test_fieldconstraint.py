import pytest


def test_fieldconstraint_exist():
    try:
        from experta import fieldconstraint
    except ImportError as exc:
        assert False, exc


@pytest.mark.parametrize("name", ["L",
                                  "W",
                                  "P",
                                  "ANDFC",
                                  "ORFC",
                                  "NOTFC"])
def test_existence_of_field_constraints(name):
    from experta import fieldconstraint

    assert hasattr(fieldconstraint, name)
