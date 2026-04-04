from pathlib import Path

import pytest

from characterize import U_
from characterize.data import descriptor


def test_describe(tmp_path: Path) -> None:
    tmp_name = Path(tmp_path, __name__)
    data_descriptor = descriptor.describe(tmp_name, column_names=["test (degC)"])
    assert data_descriptor
    assert data_descriptor.name == __name__
    assert data_descriptor.columns == {"test (degC)": descriptor.Kind(U_("degree_Celsius"), "test")}


@pytest.mark.parametrize(
    argnames=("substring", "expected"),
    argvalues=[
        ("T (degC)", descriptor.Kind(U_("degree_Celsius"), "T")),
        ("Temp (degC)", descriptor.Kind(U_("degree_Celsius"), "Temp")),
    ],
)
def test_quantify_quantity_parsing(substring: str, expected: descriptor.Kind) -> None:
    t_kind = descriptor.quantify(substring)
    assert t_kind == expected


@pytest.mark.parametrize(
    argnames=("substring", "semantic_label", "unit_label"),
    argvalues=[
        ("T (degC)", "T", "degC"),
        ("Temp (degC)", "Temp", "degC"),
    ],
)
def test_quantify_regex(substring: str, semantic_label: str, unit_label: str) -> None:
    t_matcher = descriptor.SEMANTIC_UNIT_REGEX.match(substring)
    assert t_matcher is not None
    t_semantic_label, t_unit_label = t_matcher.groups()
    assert t_semantic_label == semantic_label
    assert t_unit_label == unit_label


@pytest.mark.parametrize(argnames=("substring"), argvalues=[("T degC"), ("Temp degC"), ("(degC)"), ("Temp")])
def test_quantify_regex_not_matching(substring: str) -> None:
    matcher = descriptor.SEMANTIC_UNIT_REGEX.match(substring)
    assert matcher is None
