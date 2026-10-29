"""Lab 6 - Branch coverage tests for loan_eligibility.py
Student : Shree Verdhan M
SRN     : PES1UG24AM265
Run     : coverage run --branch -m pytest BranchCoverageTest_loan_eligibility.py
          coverage report -m
Every decision is exercised on BOTH its True and False side, including
boundary values (300/900, 750, 650, 550, ages 21/60, minimum incomes).
"""
import pytest
from loan_eligibility import credit_band, is_eligible, interest_rate


# ---------- credit_band: validation branch ----------
@pytest.mark.parametrize("score", [299, 901, 0, -5, 1000])
def test_credit_band_invalid_scores(score):
    with pytest.raises(ValueError):
        credit_band(score)


@pytest.mark.parametrize("score", [300, 900])
def test_credit_band_valid_extremes_do_not_raise(score):
    assert credit_band(score) in {"excellent", "good", "fair", "poor"}


# ---------- credit_band: each elif True / False side + boundaries ----------
@pytest.mark.parametrize(
    "score, expected",
    [
        (900, "excellent"),
        (800, "excellent"),
        (750, "excellent"),   # boundary: >= 750 True
        (749, "good"),        # boundary: >= 750 False
        (700, "good"),
        (650, "good"),        # boundary: >= 650 True
        (649, "fair"),        # boundary: >= 650 False
        (600, "fair"),
        (550, "fair"),        # boundary: >= 550 True
        (549, "poor"),        # boundary: >= 550 False
        (400, "poor"),
        (300, "poor"),
    ],
)
def test_credit_band_all_branches(score, expected):
    assert credit_band(score) == expected


# ---------- is_eligible ----------
def test_eligible_salaried():
    assert is_eligible(30, 50000, "salaried", 800) is True


def test_eligible_self_employed():
    assert is_eligible(45, 60000, "self_employed", 700) is True


@pytest.mark.parametrize("employment", ["student", "", "SALARIED", None])
def test_unknown_employment_raises(employment):
    with pytest.raises(ValueError):
        is_eligible(30, 50000, employment, 800)


@pytest.mark.parametrize(
    "age, expected",
    [
        (20, False),   # just below lower bound (age < 21 True)
        (21, True),    # lower boundary, allowed
        (60, True),    # upper boundary, allowed
        (61, False),   # just above upper bound (age > 60 True)
        (18, False),
        (75, False),
    ],
)
def test_age_limits(age, expected):
    assert is_eligible(age, 50000, "salaried", 800) is expected


@pytest.mark.parametrize(
    "employment, income, expected",
    [
        ("salaried", 24999, False),
        ("salaried", 25000, True),         # exact minimum
        ("self_employed", 39999, False),
        ("self_employed", 40000, True),    # exact minimum
        ("self_employed", 25000, False),   # salaried minimum is not enough
    ],
)
def test_income_thresholds(employment, income, expected):
    assert is_eligible(30, income, employment, 800) is expected


@pytest.mark.parametrize(
    "score, expected",
    [(549, False), (400, False), (550, True), (700, True)],
)
def test_poor_credit_band_rejected(score, expected):
    assert is_eligible(30, 50000, "salaried", score) is expected


def test_invalid_score_propagates_from_is_eligible():
    with pytest.raises(ValueError):
        is_eligible(30, 50000, "salaried", 950)


# ---------- interest_rate: all band / employment / collateral combinations ----------
@pytest.mark.parametrize(
    "score, employment, collateral, expected",
    [
        (800, "salaried", False, 8),
        (800, "salaried", True, 6),
        (800, "self_employed", False, 9),
        (800, "self_employed", True, 7),
        (700, "salaried", False, 10),
        (700, "salaried", True, 8),
        (700, "self_employed", False, 11),
        (700, "self_employed", True, 9),
        (600, "salaried", False, 13),
        (600, "salaried", True, 11),
        (600, "self_employed", False, 14),
        (600, "self_employed", True, 12),
        (400, "salaried", False, 13),      # poor falls into the else branch
        (400, "self_employed", True, 12),
    ],
)
def test_interest_rate_combinations(score, employment, collateral, expected):
    assert interest_rate(score, employment, collateral) == expected


def test_interest_rate_invalid_score_raises():
    with pytest.raises(ValueError):
        interest_rate(1000, "salaried", False)
