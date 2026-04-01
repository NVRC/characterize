"""Provide an interface to describe a dataset and its properties."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


@dataclass
class ColumnarDescriptor:
    name: str
    path: Path
    columns: List[str]


def describe(path: Path, column_names: Sequence[str]) -> ColumnarDescriptor:
    name = path.stem
    return ColumnarDescriptor(name=name, path=path, columns=list(column_names))
