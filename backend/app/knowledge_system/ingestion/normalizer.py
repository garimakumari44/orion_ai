from __future__ import annotations

import re

from .models import ProcessingDocument


class TextNormalizer:
    """
    Cleans and normalizes document text.
    """

    def normalize(
        self,
        document: ProcessingDocument,
    ) -> ProcessingDocument:

        text = document.text

        text = text.replace("\r\n", "\n")

        text = re.sub(r"\t+", " ", text)

        text = re.sub(r" +", " ", text)

        text = re.sub(r"\n{3,}", "\n\n", text)

        document.text = text.strip()

        return document