import inspect

import assertive.criteria as criteria_module
from assertive import Criteria


def test_exported_concrete_criteria_define_docstrings():
    undocumented = []

    for name, value in inspect.getmembers(criteria_module, inspect.isclass):
        if (
            name.startswith("_")
            or value is Criteria
            or not issubclass(value, Criteria)
            or inspect.isabstract(value)
        ):
            continue

        if not value.__doc__ or not value.__doc__.strip():
            undocumented.append(name)

    assert undocumented == []
