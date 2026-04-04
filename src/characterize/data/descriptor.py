"""Provide an interface to describe a dataset and its properties."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence

from pint.facets.plain import UnitT

from characterize import ureg


SEMANTIC_UNIT_REGEX = re.compile(r"(.*?)[\s-]+\(+(.*?)\)")


@dataclass
class Kind:
    unit: UnitT
    semantic: Optional[str]


@dataclass
class ColumnarDescriptor:
    name: str
    path: Path
    columns: Dict[str, Kind]


def quantify(label: str) -> Kind:
    """Parse common label notations to infer a reduced Quantity set.

    Parameters
    ----------
    label : str
        Common label formats include:
            [semantic label] [(<unit>)] e.g.
                Temp (degC),
                (degC),
                Temp degC,
                degC

    Examples
    --------
        >>> quantify("T (degC)")
        <Unit('degree_Celsius')>

    """
    label_unit_match = SEMANTIC_UNIT_REGEX.match(label)
    # Clean REGEX matches, otherwise greedily parse
    if label_unit_match is not None:
        semantic_label, unit_label = label_unit_match.groups()
        unit = ureg.parse_units(unit_label)
        return Kind(
            unit=unit,
            semantic=semantic_label,
        )

    raise NotImplementedError("BASE ERROR")


def describe(path: Path, column_names: Sequence[str]) -> ColumnarDescriptor:
    name = path.stem
    return ColumnarDescriptor(name=name, path=path, columns={col_name: quantify(col_name) for col_name in column_names})
