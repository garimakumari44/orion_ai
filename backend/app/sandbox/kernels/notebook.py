"""
Jupyter notebook execution kernel.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError


class NotebookKernel:
    """
    Executes Jupyter notebooks.

    Example:
        kernel = NotebookKernel()

        result = kernel.execute(
            "analysis.ipynb"
        )
    """

    language = "notebook"

    def execute(
        self,
        notebook_path: str,
        timeout: int = 300,
        kernel_name: str = "python3",
        output_path: Optional[str] = None,
    ) -> Dict:

        notebook_path = Path(notebook_path)

        try:
            notebook = nbformat.read(
                notebook_path,
                as_version=4,
            )

            client = NotebookClient(
                notebook,
                timeout=timeout,
                kernel_name=kernel_name,
            )

            client.execute()

            if output_path:
                nbformat.write(notebook, output_path)

            outputs = []

            for cell in notebook.cells:
                if cell.cell_type != "code":
                    continue

                for output in cell.get("outputs", []):

                    if "text" in output:
                        outputs.append(output["text"])

                    elif "data" in output:
                        outputs.append(output["data"])

            return {
                "success": True,
                "language": self.language,
                "outputs": outputs,
            }

        except CellExecutionError as exc:
            return {
                "success": False,
                "language": self.language,
                "error": str(exc),
            }

        except Exception as exc:
            return {
                "success": False,
                "language": self.language,
                "error": str(exc),
            }