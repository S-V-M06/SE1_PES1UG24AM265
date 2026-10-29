"""Lab 6 - Code (line) coverage tests for loan_eligibility.py
Student : Shree Verdhan M
SRN     : PES1UG24AM265
Run     : coverage run -m pytest CodeCoverageTest_loan_eligibility.py
          coverage report -m
"""
import pytest
from loan_eligibility import credit_band, is_eligible, interest_rate


# ---------- credit_band ----------
def test_excellent_band():
    assert credit_band(800) == "excellent"


def test_good_band():
    assert credit_band(700) == "good"


def test_fair_band():
    assert credit_band(600) == "fair"


def test_poor_band():
    assert credit_band(400) == "poor"


def test_invalid_score_raises():
    with pytest.raises(ValueError):
        credit_band(100)


# ---------- is_eligible ----------
def test_eligible():
    assert is_eligible(30, 50000, "salaried", 800) is True


def test_unknown_employment_raises():
    with pytest.raises(ValueError):
        is_eligible(30, 50000, "student", 800)


def test_underage_not_eligible():
    assert is_eligible(18, 50000, "salaried", 800) is False


def test_low_income_not_eligible():
    assert is_eligible(30, 10000, "salaried", 800) is False


def test_poor_score_not_eligible():
    assert is_eligible(30, 50000, "salaried", 400) is False


# ---------- interest_rate ----------
def test_rate_excellent_salaried_no_collateral():
    assert interest_rate(800, "salaried", False) == 8


def test_rate_good_salaried_no_collateral():
    assert interest_rate(700, "salaried", False) == 10


def test_rate_fair_self_employed_with_collateral():
    # 13 (fair) + 1 (self employed) - 2 (collateral) = 12
    assert interest_rate(600, "self_employed", True) == 12
