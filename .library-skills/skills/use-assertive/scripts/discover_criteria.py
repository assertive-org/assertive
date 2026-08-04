#!/usr/bin/env python3
"""Discover public Assertive criteria from the installed package."""

from __future__ import annotations

import argparse
import inspect
import sys
from dataclasses import dataclass

try:
    import assertive.criteria as criteria_module
    from assertive import Criteria
except ImportError as error:
    print(
        "Unable to import Assertive. Run this helper with the Python environment "
        "where assertive is installed.",
        file=sys.stderr,
    )
    raise SystemExit(2) from error


@dataclass(frozen=True)
class CriteriaExport:
    name: str
    signature: str
    documentation: str
    kind: str

    @property
    def searchable_text(self) -> str:
        return " ".join((self.name, self.signature, self.documentation)).casefold()


def _signature(value: type[Criteria]) -> str:
    try:
        return str(inspect.signature(value))
    except (TypeError, ValueError):
        return "(signature unavailable)"


def discover_exports() -> list[CriteriaExport]:
    """Return public, concrete criteria classes and exported instances."""
    exports: list[CriteriaExport] = []

    for name, value in inspect.getmembers(criteria_module):
        if name.startswith("_"):
            continue

        if inspect.isclass(value):
            if (
                value is Criteria
                or not issubclass(value, Criteria)
                or inspect.isabstract(value)
            ):
                continue
            exports.append(
                CriteriaExport(
                    name=name,
                    signature=_signature(value),
                    documentation=inspect.getdoc(value) or "",
                    kind="class",
                )
            )
            continue

        if isinstance(value, Criteria):
            exports.append(
                CriteriaExport(
                    name=name,
                    signature=f"<{type(value).__name__} instance>",
                    documentation=inspect.getdoc(value) or "",
                    kind="instance",
                )
            )

    return exports


def select_exports(
    exports: list[CriteriaExport], terms: list[str]
) -> list[CriteriaExport]:
    """Filter exports using case-insensitive AND matching."""
    normalized_terms = [term.casefold() for term in terms]
    return [
        export
        for export in exports
        if all(term in export.searchable_text for term in normalized_terms)
    ]


def _summary(documentation: str) -> str:
    if not documentation:
        return "No docstring available."
    return documentation.splitlines()[0]


def render_export(export: CriteriaExport, full: bool) -> str:
    """Render one discovered export for terminal output."""
    header = f"{export.name}{export.signature} [{export.kind}]"
    body = export.documentation if full else _summary(export.documentation)
    return f"{header}\n{body}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect public concrete criteria exported by assertive.criteria and "
            "search their names, signatures, and docstrings."
        )
    )
    parser.add_argument(
        "terms",
        nargs="*",
        help="Case-insensitive search terms; every term must match.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print complete docstrings instead of their first line.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    matches = select_exports(discover_exports(), args.terms)

    if not matches:
        query = " ".join(args.terms) or "<all exports>"
        print(f"No Assertive criteria matched: {query}", file=sys.stderr)
        return 1

    print("\n\n".join(render_export(export, args.full) for export in matches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
