import math

from hypothesis import given, example, settings, strategies as st

from loan_eligibility import parse_income, monthly_emi, pan_category


# ---------------------------------------------------------------------------
# Helper strategies
# ---------------------------------------------------------------------------
# Anything that is NOT a string: ints, floats, bools, bytes, lists, dicts ...
non_strings = st.one_of(
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
    st.booleans(),
    st.binary(),
    st.lists(st.integers(), max_size=3),
    st.dictionaries(st.text(max_size=3), st.integers(), max_size=2),
)

VALID_TYPES = {"P": "Individual", "C": "Company", "H": "HUF", "F": "Firm"}


# ---------------------------------------------------------------------------
# 1. parse_income
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
@example(None)
@example("")
@example("abc")
@example("5,0,0.0")
@example("-50,000")
def test_parse_income_no_crash(s):
    """parse_income must never raise, whatever it is given."""
    try:
        parse_income(s)
    except Exception as e:
        assert False, f"parse_income crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none() | non_strings)
def test_parse_income_returns_none_or_non_negative_int(s):
    result = parse_income(s)
    assert result is None or (isinstance(result, int) and result >= 0)


@given(st.integers(min_value=0, max_value=10**12))
def test_parse_income_valid_roundtrip(n):
    """Valid incomes (plain, comma-grouped, Indian-grouped) parse back exactly."""
    assert parse_income(str(n)) == n
    assert parse_income(f"{n:,}") == n
    assert parse_income(f"  {n:,}  ") == n


@given(st.integers(min_value=1, max_value=10**12))
def test_parse_income_rejects_negative(n):
    assert parse_income(f"-{n}") is None
    assert parse_income(f"-{n:,}") is None


@given(non_strings)
def test_parse_income_rejects_non_strings(x):
    assert parse_income(x) is None


# ---------------------------------------------------------------------------
# 2. monthly_emi
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
@example(None)
@example("")
@example("500000,10")
@example("500000,0,5")
@example("500000,10,0")
@example("500000,10.5,5")
@example("500000,1000000,1000000")
def test_monthly_emi_no_crash(s):
    """monthly_emi must never raise, whatever it is given."""
    try:
        monthly_emi(s)
    except Exception as e:
        assert False, f"monthly_emi crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none() | non_strings)
def test_monthly_emi_returns_none_or_positive_finite_float(s):
    result = monthly_emi(s)
    assert result is None or (
        isinstance(result, float) and math.isfinite(result) and result >= 0
    )


@given(
    principal=st.integers(min_value=1, max_value=10**9),
    rate=st.floats(min_value=0.01, max_value=40, allow_nan=False),
    years=st.integers(min_value=1, max_value=40),
)
def test_monthly_emi_valid_inputs(principal, rate, years):
    """Total repaid (EMI x months) can never be less than the principal."""
    result = monthly_emi(f"{principal},{rate:.2f},{years}")
    assert result is not None
    months = years * 12
    assert result * months >= principal - 0.01 * months


@given(
    principal=st.integers(min_value=1, max_value=10**9),
    years=st.integers(min_value=1, max_value=40),
)
def test_monthly_emi_zero_interest(principal, years):
    """0% interest must not divide by zero: EMI is simply principal / months."""
    assert monthly_emi(f"{principal},0,{years}") == round(principal / (years * 12), 2)


@given(
    principal=st.integers(max_value=0),
    rate=st.integers(min_value=-1000, max_value=1000),
    years=st.integers(max_value=0),
)
def test_monthly_emi_rejects_non_positive(principal, rate, years):
    assert monthly_emi(f"{principal},{rate},{years}") is None


@given(st.lists(st.integers(min_value=0, max_value=1000), max_size=6))
def test_monthly_emi_wrong_field_count(parts):
    if len(parts) != 3:
        assert monthly_emi(",".join(map(str, parts))) is None


@given(non_strings)
def test_monthly_emi_rejects_non_strings(x):
    assert monthly_emi(x) is None


# ---------------------------------------------------------------------------
# 3. pan_category
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
@example(None)
@example("")
@example("ABC")
@example("ABCXE1234F")
def test_pan_category_no_crash(s):
    """pan_category must never raise, whatever it is given."""
    try:
        pan_category(s)
    except Exception as e:
        assert False, f"pan_category crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none() | non_strings)
def test_pan_category_returns_none_or_known_category(s):
    result = pan_category(s)
    assert result is None or result in VALID_TYPES.values()


@given(
    first=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=3, max_size=3),
    kind=st.sampled_from(sorted(VALID_TYPES)),
    fifth=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=1),
    digits=st.text(alphabet="0123456789", min_size=4, max_size=4),
    last=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=1),
    lower=st.booleans(),
)
def test_pan_category_valid_pan(first, kind, fifth, digits, last, lower):
    """Every well-formed PAN maps to the right holder category (case-insensitive)."""
    pan = f"{first}{kind}{fifth}{digits}{last}"
    if lower:
        pan = pan.lower()
    assert pan_category(pan) == VALID_TYPES[kind]


@given(
    first=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=3, max_size=3),
    kind=st.sampled_from(list("ABDEGIJKLMNOQRSTUVWXYZ")),  # not P/C/H/F
    fifth=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=1),
    digits=st.text(alphabet="0123456789", min_size=4, max_size=4),
    last=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=1),
)
def test_pan_category_unknown_holder_type(first, kind, fifth, digits, last):
    assert pan_category(f"{first}{kind}{fifth}{digits}{last}") is None


@given(st.text(max_size=3))
def test_pan_category_too_short(s):
    assert pan_category(s) is None


@given(non_strings)
def test_pan_category_rejects_non_strings(x):
    assert pan_category(x) is None
