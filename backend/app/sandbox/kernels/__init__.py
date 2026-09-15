"""
sandbox.kernels
================

Execution kernels supported by the sandbox.

Each kernel provides a common interface:

    initialize()
    execute()
    shutdown()

Available Kernels
-----------------
- PythonKernel
- BashKernel
- SQLKernel
- NotebookKernel
"""

from .python import PythonKernel
from .bash import BashKernel
from .sql import SQLKernel
from .notebook import NotebookKernel

__all__ = [
    "PythonKernel",
    "BashKernel",
    "SQLKernel",
    "NotebookKernel",
]


def available_kernels() -> dict:
    """
    Returns all available execution kernels.

    Example
    -------
    >>> available_kernels()["python"]
    <class 'PythonKernel'>
    """
    return {
        "python": PythonKernel,
        "bash": BashKernel,
        "sql": SQLKernel,
        "notebook": NotebookKernel,
    }


def get_kernel(name: str):
    """
    Return the kernel class for a given name.

    Raises
    ------
    ValueError
        If the kernel does not exist.
    """
    kernels = available_kernels()

    key = name.lower()

    if key not in kernels:
        raise ValueError(
            f"Unknown kernel '{name}'. "
            f"Available kernels: {', '.join(kernels.keys())}"
        )

    return kernels[key]