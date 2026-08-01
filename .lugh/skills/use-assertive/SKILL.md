---
name: use-assertive
description: Use Assertive to write declarative Python test assertions. Use when selecting or discovering built-in criteria, composing or nesting expectations, matching mappings, lists, objects, mocks, or exceptions, or implementing and serializing custom criteria.
---

# Use Assertive

## Start with the matching model

When using Assertive, put the subject on the left and an instantiated criteria object on
the right:

```python
from assertive import is_gt

age = 21

assert age == is_gt(18)
```

Read this as “assert that `age` satisfies `is_gt(18)`.” Import public criteria from
`assertive`. Keep the value on the left so Python dispatches the comparison through
Assertive correctly. `ANY` is already an instance; classes such as `is_gt` must be
instantiated.

## Prefer the simplest assertion

Do not introduce a criterion when an ordinary Python assertion already states the intent
clearly:

```python
# Prefer this for exact equality.
assert x == 42

# Avoid this unless a criteria object is specifically needed.
from assertive import is_eq

assert x == is_eq(42)
```

Use criteria when they add meaning: ranges, patterns, approximate matching, composition,
nested matching, or a reusable/dynamically selected expectation. Likewise, when a nestable
criterion accepts literals, pass a literal for exact matching instead of wrapping it in
`is_eq`. Reach for `is_eq` only when exact equality must itself be represented as a criteria
object, such as one branch of a composed expectation.

## Discover criteria from the installed version

Treat `assertive.criteria` exports and their docstrings as the source of truth. Do not
rely on a memorized catalog: the installed version may contain newer criteria.

Run the bundled helper with the active project Python:

```bash
python <path-to-this-skill>/scripts/discover_criteria.py mapping
python <path-to-this-skill>/scripts/discover_criteria.py length criteria --full
```

With no search terms, the helper lists every public concrete criteria class and exported
criteria instance. Search terms are case-insensitive and all must occur across the name,
signature, or docstring. Use `--full` to read complete matching docstrings.

Inspect a likely export directly when more detail is needed:

```python
import inspect
import assertive.criteria as criteria

print(inspect.signature(criteria.has_length))
print(inspect.getdoc(criteria.has_length))
```

Use signatures and docstrings to confirm accepted argument types, fluent modifiers, type
constraints, and whether arguments support nested criteria.

## Nest criteria where supported

Many criteria accept other criteria as arguments. Mix literal expectations with nested
criteria to describe structured values declaratively:

```python
from assertive import (
    contains_exactly,
    has_key_values,
    has_length,
    is_between,
    is_gte,
    is_positive,
    starts_with,
)

assert user == has_key_values({
    "name": starts_with("A"),
    "age": is_gte(18),
    "active": True,
})

assert record == contains_exactly(
    starts_with("user_"),
    is_positive(),
    "active",
)

assert values == has_length(is_between(2, 5))
```

Look for the same pattern in mapping values, list positions or members, object attributes,
mock call arguments, exception messages, and criteria that transform a subject before
matching it. Do not assume every constructor argument is nestable; confirm it from the
installed signature and docstring.

## Compose whole expectations

Use operators to combine criteria applied to the same subject:

```python
from assertive import is_even, is_gte, is_lt

working_age = is_gte(18) & is_lt(65)  # both
special = is_even() | is_lt(0)        # either
exactly_one = is_even() ^ is_lt(0)    # one, but not both
not_negative = ~is_lt(0)              # negate

assert 42 == working_age
```

Distinguish composition from nesting: composition combines whole expectations, while
nesting passes a criteria object into another criterion to match part or a derived property
of the subject. Parenthesize mixed expressions when operator precedence could be unclear.

## Write custom criteria

Choose the smallest suitable approach:

1. Use `PredicateCriteria` for a local one-off rule.
2. Subclass `WrappedCriteria` to give a reusable name to composed built-ins.
3. Subclass `Criteria` when the rule needs domain logic or custom state.

```python
from assertive import (
    Criteria,
    PredicateCriteria,
    WrappedCriteria,
    is_gte,
    is_lte,
)

is_slug = PredicateCriteria(
    lambda subject: isinstance(subject, str) and subject.replace("-", "").isalnum(),
    "a slug-like string",
)


class is_percentage(WrappedCriteria):
    def __init__(self):
        super().__init__(is_gte(0) & is_lte(100))


class is_divisible_by(Criteria):
    def __init__(self, divisor: int):
        self.divisor = divisor

    def _match(self, subject) -> bool:
        return isinstance(subject, int) and subject % self.divisor == 0
```

Implement only `_match(subject) -> bool` for ordinary criteria. Let the base class handle
comparison, composition, and default negation. Override `_negated_match` only when negation
has genuinely different semantics.

When a custom criterion accepts either a literal or another criterion, normalize it with
`ensure_criteria` and evaluate it with `run_match`:

```python
from assertive import Criteria, ensure_criteria


class attribute_matches(Criteria):
    def __init__(self, name, expected):
        self.name = name
        self.expected = ensure_criteria(expected)

    def _match(self, subject) -> bool:
        return self.expected.run_match(getattr(subject, self.name))
```

Decide deliberately whether an unsupported subject type should return `False` or raise
`TypeError`, and apply that contract consistently. Keep matching stateless so reuse does not
change results.

## Add serialization only when needed

The default `to_serialized` stores `__dict__`, and the default `from_serialized` calls the
constructor with that mapping. Override either method when constructor arguments and stored
state differ. Register downstream custom criteria explicitly with a stable, unique tag:

```python
from assertive.serialize import SERIALIZABLE_CRITERIA

SERIALIZABLE_CRITERIA["$divisible_by"] = is_divisible_by
```

Registration is process-local and required before both serialization and deserialization.
Test a round trip when supporting this feature.

## Verify the expectation

Test matching and non-matching subjects, composition, nesting, unsupported types, and reuse
of the same criteria instance. For a custom nestable criterion, test both a literal argument
and another criteria object. Run the project’s focused tests after writing the assertion.
