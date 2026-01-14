"""Bundled Atlas documents for context assembly."""

from __future__ import annotations

from importlib import resources
from importlib.abc import Traversable


def atlas_docs_root() -> Traversable:
    return resources.files(__name__).joinpath("atlas")
