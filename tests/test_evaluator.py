import pytest
from kalc_engine.evaluator import Evaluator, EvalError


def test_basic_add():
    ev = Evaluator()
    assert ev.evaluate('2+3', mode='basic') == 5


def test_scientific_sin():
    ev = Evaluator()
    res = ev.evaluate('sin(3.1415926535/2)', mode='scientific')
    assert abs(res - 1.0) < 1e-6


def test_power_caret_in_scientific():
    ev = Evaluator()
    assert ev.evaluate('2 ^ 3', mode='scientific') == 8


def test_programmer_bitwise():
    ev = Evaluator()
    assert ev.evaluate('0b1010 & 0b1100', mode='programmer') == 8
    assert ev.evaluate('5 ^ 2', mode='programmer') == 7


def test_unary_minus():
    ev = Evaluator()
    assert ev.evaluate('-3 + 5', mode='basic') == 2


def test_malformed():
    ev = Evaluator()
    with pytest.raises(EvalError):
        ev.evaluate('2 + * 3', mode='basic')
