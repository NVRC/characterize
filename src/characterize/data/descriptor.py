"""Provide an interface to describe a dataset and its properties."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence

from pint import UndefinedUnitError
from pint.facets.plain import UnitT

from characterize import ureg


SEMANTIC_UNIT_REGEX = re.compile(r"(.*?)[\s-]+\(+(.*?)\)")
UNIT_REGEX = re.compile(r"\(+(.*?)\)")
WORDS_REGEX = "[^a-zA-Z0-9]"

MAX_UNIT_SUFFIX_LENGTH = 2


@dataclass
class Kind:
    unit: Optional[UnitT]
    semantic: str


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
        Kind(unit=<Unit("degree_Celsius")>, semantic="degree_Celsius")
        >>> kindify("foobar_fizz_buzz_degrees_Celsius")
        Kind(unit=<UNit("degree_Celsius")>, semantic="foobar_fizz_buzz")
        >>> kindify("UNKNOWN")
        Kind(unit=None, semantic="UNKNOWN")

    """
    # NOTE: semantic label could optionally be matched
    semantic_unit_match = SEMANTIC_UNIT_REGEX.match(label)
    # Clean REGEX matches, otherwise greedily parse
    try:
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
                semantic=str(unit),
            )

        # Assuming two or more words
        # Attempt to parse compound units suffixes up to MAX_UNIT_SUFFIX_LENGTH splits
        splits = re.split(WORDS_REGEX, label)
        number_of_components = len(splits)
        if number_of_components >= 1:
            for irange in range(-1, -(MAX_UNIT_SUFFIX_LENGTH + 1), -1):
                unit_label = "_".join(splits[irange:])
                if unit_label not in ureg:
                    continue
                unit = ureg.parse_units(unit_label)
                compound_semantic_label: str = str(unit)
                if number_of_components > abs(irange):
                    compound_semantic_label = "_".join(splits[:irange])
                return Kind(
                    unit=unit,
                    semantic=compound_semantic_label,
                )
    except UndefinedUnitError:
        logging.warning(
            "Unable to derive unit from label %s. Continuing without a unit.", label
        )

    # Base case with no unit, return transparent semantics
    return Kind(unit=None, semantic=label)


def describe(path: Path, column_names: Sequence[str]) -> ColumnarDescriptor:
    name = path.stem
    return ColumnarDescriptor(
        name=name,
        path=path,
        columns={col_name: kindify(col_name) for col_name in column_names},
    )
