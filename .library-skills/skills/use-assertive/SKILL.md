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

## Match mock interactions

Continue to create test doubles with `unittest.mock.Mock` and `AsyncMock`, but replace its
`assert_called*`, `assert_not_called`, `assert_awaited*`, and `assert_not_awaited` assertion
methods completely with Assertive criteria. Put the mock method on the left and the
interaction criterion on the right:

```python
from unittest.mock import Mock

from assertive import is_gt, starts_with, was_called_with

gateway = Mock()
gateway.charge("cus_001", amount=2500, currency="USD")

assert gateway.charge == was_called_with(
    starts_with("cus_"),
    amount=is_gt(0),
).once()
```

Choose the argument-matching behavior deliberately:

- Use `was_called_with` when expected keyword arguments may be a subset of the actual
  keyword arguments. Positional arguments still match exactly by count and order.
- Use `was_called_exactly_with` when the complete positional and keyword argument set must
  match.
- Use `was_called` when only the total call count matters.

The default count is at least once. Refine it with `.once()`, `.twice()`, `.never()`,
`.times(n)`, or `.at_least_times(n)`. On `was_called_with` and
`was_called_exactly_with`, these modifiers count only calls whose arguments match. Use the
`was_called_once*` and `was_not_called*` convenience criteria when they read more clearly.

Do not confuse one matching call with one total call. For the full semantics of
`Mock.assert_called_once_with`, compose a total-count criterion with an argument criterion:

```python
from assertive import was_called, was_called_exactly_with

assert gateway.charge == (
    was_called().once()
    & was_called_exactly_with("cus_001", amount=2500, currency="USD").once()
)
```

Use `was_called()`, `was_called_once()`, and `was_not_called()` for total call history. Use
`was_called_with(...)` when any matching call is sufficient; unlike
`Mock.assert_called_with(...)`, it is not restricted to the most recent call.

Use the corresponding `was_awaited*` criteria for `AsyncMock` await history:

```python
from unittest.mock import AsyncMock

from assertive import has_key_values, is_gt, was_awaited_once_with

publisher = AsyncMock()
await publisher.send("/events", payload={"type": "purchase", "amount": 2500})

assert publisher.send == was_awaited_once_with(
    "/events",
    payload=has_key_values({"type": "purchase", "amount": is_gt(0)}),
)
```

Do not confuse calling an `AsyncMock` with awaiting it; use `was_awaited`,
`was_awaited_with`, and their exact/convenience variants when the await is the behavior under
test. Combine `was_awaited().once()` with `was_awaited_exactly_with(...).once()` when both
one total await and exact arguments are required. Do not call the mock library's assertion
methods; keep all mock verification in the same `assert mock == criteria` model.

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

## Skip serialization for most use cases

Most users do not need serialization. Normal assertions, composition, nesting, mocks, and
custom criteria used in the same Python process require no serialization. Skip it unless
criteria must cross a process, network, persistence, or other data boundary.

Serialization exists mainly for frameworks that need to transport or store criteria, such
as `assertive-mock-api`. Its Python client accepts criteria directly, serializes them into
JSON-safe HTTP payloads, and the server deserializes them before matching:

```python
from assertive import has_key_values, is_gte
from assertive_mock_api_client import MockApiClient

client = MockApiClient("http://localhost:8910")

assert client.confirm_request(
    path="/orders",
    query=has_key_values({"limit": is_gte(1)}),
    times=is_gte(2),
) is True
```

Even when using such a framework, prefer its integration and pass criteria directly. Do not
call `serialize` or `deserialize` in ordinary application tests. Use those functions yourself
only when building a framework, persistence layer, or raw protocol integration that must
move criteria across a data boundary.

When adding custom criteria to such an integration, the default `to_serialized` stores
`__dict__`, and the default `from_serialized` calls the constructor with that mapping.
Override either method when constructor arguments and stored state differ. Register the
custom class with a stable, unique tag in every process that serializes or deserializes it:

```python
from assertive.serialize import SERIALIZABLE_CRITERIA

SERIALIZABLE_CRITERIA["$divisible_by"] = is_divisible_by
```

Registration is process-local. Test a JSON-compatible round trip and ensure both sides of
the framework boundary share the same tag and implementation.

## Verify the expectation

Test matching and non-matching subjects, composition, nesting, unsupported types, and reuse
of the same criteria instance. For a custom nestable criterion, test both a literal argument
and another criteria object. Run the project’s focused tests after writing the assertion.
