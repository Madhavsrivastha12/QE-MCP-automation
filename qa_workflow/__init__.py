"""
qa_workflow — shared, non-business-logic infrastructure for the QA agent workflow.

This package deliberately contains NO QA business logic, no test content, and no
document formatting. It exists so that agents stop inventing their own output
locations.

Import from the repository root:

    from qa_workflow.paths import OutputPaths
"""

from qa_workflow.paths import OutputPaths, SUPPORTED_TYPES  # noqa: F401

__all__ = ["OutputPaths", "SUPPORTED_TYPES"]
