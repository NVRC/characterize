"""Provide an interface to describe a dataset and its properties."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence

from pint.facets.plain import UnitT

from characterize import ureg


SEMANTIC_UNIT_REGEX = re.compile(r"(.*?)[\s-]+\(+(.*?)\)")
UNIT_REGEX = re.compile(r"\(+(.*?)\)")
WORDS_REGEX = "[^a-zA-Z0-9]"


@dataclass
class Kind:
    unit: UnitT
    semantic: Optional[str]


@dataclass
class ColumnarDescriptor:
    name: str
    path: Path
    columns: Dict[str, Kind]


def kindify(label: str) -> Kind:
    """Parse common label notations to infer a Pint.UnitT based on a column name.

    Parameters
    ----------
    label : str
        Common label formats include:
            [semantic label] [(<unit>)] e.g.
                Temp (degC),
                (degC),
                Temp degC,
                Temp of foobar degC,
                degC,

    Examples
    --------
        >>> kindify("Temp (degC)")
        Kind(unit=<Unit("degree_Celsius")>, semantic="Temp")
        >>> kindify("Temp of foobar degC")
        Kind(unit=<Unit("degree_Celsius")>, semantic="Temp of foobar")
        >>> kindify("degC")
        Kind(unit=<Unit("degree_Celsius")>, semantic=None)

    """
    # NOTE: semantic label could optionally be matched
    semantic_unit_match = SEMANTIC_UNIT_REGEX.match(label)
    # Clean REGEX matches, otherwise greedily parse
    if semantic_unit_match is not None:
        semantic_label, unit_label = semantic_unit_match.groups()
        unit = ureg.parse_units(unit_label)
        return Kind(
            unit=unit,
            semantic=semantic_label,
        )

    unit_match = UNIT_REGEX.match(label)
    if unit_match is not None:
        # Remove and parse as unit
        unit_label = unit_match.group()
        unit = ureg.parse_units(unit_label)
        return Kind(
            unit=unit,
            semantic=None,
        )

    # Assuming two or more words
    splits = re.split(WORDS_REGEX, label)
    number_of_components = len(splits)
    default_semantic_label: Optional[str] = None
    if number_of_components >= 1:
        unit = ureg.parse_units(splits[-1])
        if number_of_components > 1:
            default_semantic_label = "_".join(splits[:-1])
        return Kind(
            unit=unit,
            semantic=default_semantic_label,
        )

    raise ValueError(
        "Unable to quantify label {}. Consider revising column name.".format(label)
    )


def describe(path: Path, column_names: Sequence[str]) -> ColumnarDescriptor:
    name = path.stem
    return ColumnarDescriptor(
        name=name,
        path=path,
        columns={col_name: kindify(col_name) for col_name in column_names},
    )
