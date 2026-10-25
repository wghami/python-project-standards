"""Untyped data is narrowed or refused with a message naming what was wrong."""

from collections.abc import Callable

import pytest

from project_standards._typed import mapping, sequence, strings, text


def test_valid_values_pass_through() -> None:
    assert mapping({"a": 1}, "x") == {"a": 1}
    assert sequence([1], "x") == [1]
    assert strings(["a"], "x") == ["a"]
    assert text("a", "x") == "a"


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda: mapping([], "cfg"), "cfg must be a mapping"),
        (lambda: sequence({}, "cfg"), "cfg must be a list"),
        (lambda: strings([1], "cfg"), "cfg must be a list of strings"),
        (lambda: text(1, "cfg"), "cfg must be a string"),
    ],
)
def test_wrong_shapes_name_the_culprit(call: Callable[[], object], message: str) -> None:
    with pytest.raises(TypeError) as error:
        call()
    assert str(error.value) == message
