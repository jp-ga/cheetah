import pytest

from cheetah.converters.utils.fortran_namelist import evaluate_expression, parse_lines


def test_evaluate_expression():
    """
    Test evaluating expressions in the Fortran namelist parser, including variables,
    scientific notation, unary signs, and quoted string literals.
    """
    context = {"mc2": 0.511750}

    value = evaluate_expression("mc2+0.750e-3", context)
    assert value == pytest.approx(context["mc2"] + 0.750e-3)

    value = evaluate_expression("+mc2", context)
    assert value == pytest.approx(context["mc2"])

    value = evaluate_expression("-mc2", context)
    assert value == pytest.approx(-context["mc2"])

    value = evaluate_expression('"test_string"', context)
    assert value == "test_string"

    value = evaluate_expression("'single_quoted'", context)
    assert value == "single_quoted"


def test_define_element_string_attributes():
    """
    Test that element string attributes such as alias and type are correctly parsed
    and stored in the element dictionary without spurious quotes.
    """
    lines = [
        'q1: quadrupole, l = 0.2, alias = "q1_alias", type = "control_label", k1 = 1.0'
    ]

    context = parse_lines(lines)

    q1 = context["q1"]

    assert q1["alias"] == "q1_alias"
    assert q1["type"] == "control_label"
    assert q1["k1"] == pytest.approx(1.0)


def test_typed_property_assignment():
    """
    Test that typed property assignments targeting specific elements (e.g.
    `lcavity::l0a[voltage] = ...`) resolve and update the correct element in context.
    """
    lines = [
        "l0a: lcavity, l = 3.0, voltage = 0.0, rf_frequency = 2.856e9",
        "lcavity::l0a[voltage] = 4.0e7",
    ]

    context = parse_lines(lines)

    assert "lcavity::l0a" not in context
    assert context["l0a"]["voltage"] == pytest.approx(4.0e7)


def test_skip_control_definitions():
    """
    Test that overlay and group control definitions are skipped without causing
    parsing errors or creating rogue elements.
    """
    lines = [
        "q1: quadrupole, l = 0.2, k1 = 1.0",
        "o_q1: overlay = {q1[k1]: scale * q1[k1]}, var = {scale}, scale = 1.0",
        "g_all: group = {q1[k1]: 2.0}, var = {k1}",
    ]

    context = parse_lines(lines)

    assert "q1" in context
    assert "o_q1" not in context
    assert "g_all" not in context
