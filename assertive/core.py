from abc import ABC, abstractmethod
from typing import Any, final


def ensure_criteria(value: Any) -> "Criteria":
    if isinstance(value, Criteria):
        return value
    return is_eq(value)


class Criteria(ABC):
    """
    Base class for defining criteria used in assertions.

    Subclasses of `Criteria` should override the `_match` method to determine if the subject matches the criteria.
    """

    def to_serialized(self) -> dict:
        """
        Serializes the criteria into a dictionary representation.
        This method should be overridden by subclasses to provide custom serialization.
        """
        return self.__dict__  # pyright: ignore[reportReturnType]

    @classmethod
    def from_serialized(cls, serialized: dict) -> "Criteria":
        """
        Deserializes the criteria from a dictionary representation.
        This method should be overridden by subclasses to provide custom deserialization.
        """
        return cls(**serialized)

    def _before_run(self, subject):
        pass

    @final
    def run_match(self, subject) -> bool:
        self._before_run(subject)
        return self._match(subject)

    @final
    def run_negated_match(self, subject) -> bool:
        self._before_run(subject)
        return self._negated_match(subject)

    @abstractmethod
    def _match(self, subject) -> bool:
        """
        Determine if the subject matches this criteria.
        Should be overridden by child classes.

        Args:
            subject: The object to match against this criteria.

        Returns:
            bool: True if the subject matches, False otherwise.
        """
        ...

    def _negated_match(self, subject) -> bool:
        """
        Determine if the subject matches this criteria (negated).
        Should be overridden by child classes.

        Args:
            subject: The object to match against this criteria.

        Returns:
            bool: True if the subject does not match, False otherwise.
        """
        return not self.run_match(subject)

    def __and__(self, other):
        return AndCriteria([self, ensure_criteria(other)])

    def __or__(self, other):
        return OrCriteria([self, ensure_criteria(other)])

    def __xor__(self, other):
        return XorCriteria(self, ensure_criteria(other))

    def __invert__(self):
        return InvertedCriteria(self)

    def __eq__(self, other):
        return self.run_match(other)

    def __neq__(self, other):
        return self.run_negated_match(other)


class AndCriteria(Criteria):
    def __init__(self, items: list[Criteria]):
        self.items = items

    def _match(self, subject) -> bool:
        return all(criteria.run_match(subject) for criteria in self.items)


class OrCriteria(Criteria):
    def __init__(self, items: list[Criteria]):
        self.items = items

    def _match(self, subject) -> bool:
        return any(items.run_match(subject) for items in self.items)


class XorCriteria(Criteria):
    def __init__(self, left: Criteria, right: Criteria):
        self.left = left
        self.right = right

    def _match(self, subject) -> bool:
        return self.left.run_match(subject) ^ self.right.run_match(subject)


class InvertedCriteria(Criteria):
    def __init__(self, value: Criteria):
        self.value = value

    def _match(self, subject) -> bool:
        return self.value.run_negated_match(subject)

    def _negated_match(self, subject) -> bool:
        return self.value.run_match(subject)


class is_eq(Criteria):
    """
    Match values that are equal to ``value``.

    Equality uses normal Python ``==`` semantics, so custom ``__eq__``
    implementations on the subject are respected.

    Args:
        value: Value that the subject must equal.

    Example:
        ```python
        assert 2 == is_eq(2)       # passes
        assert "abc" == is_eq("x") # fails
        ```
    """

    def __init__(self, value):
        self.value = value

    def _match(self, subject) -> bool:
        return subject == self.value
