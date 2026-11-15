import math
import re

CATEGORIES = {"P": "Individual", "C": "Company", "H": "HUF", "F": "Firm"}

# ---------------------------------------------------------------------------
# Validation limits (keep arithmetic finite and inputs realistic)
# ---------------------------------------------------------------------------
MAX_INPUT_LEN = 100          # reject absurdly long strings (also avoids int-digit limit errors)
MAX_INCOME = 10 ** 12
MAX_PRINCIPAL = 10 ** 12
MAX_RATE = 100.0             # annual interest rate, percent
MAX_YEARS = 100

# ASCII-only patterns: str.isdigit()/int() also accept Unicode digits such as '٣' or '²'.
_INCOME_RE = re.compile(r"[0-9][0-9,]*", re.ASCII)
_INT_RE = re.compile(r"[0-9]+", re.ASCII)
_RATE_RE = re.compile(r"[0-9]+(\.[0-9]+)?", re.ASCII)
_PAN_RE = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]", re.ASCII | re.IGNORECASE)


def parse_income(income):
    """Parse an income string such as '50,000' or '5,00,000' into an int.

    Returns None for anything that is not a valid, non-negative income
    (None, non-strings, empty, negative, letters, decimals, too large ...).
    """
    if not isinstance(income, str):
        return None
    income = income.strip()
    if not income or len(income) > MAX_INPUT_LEN:
        return None
    if not _INCOME_RE.fullmatch(income):          # digits and commas only, must start with a digit
        return None
    value = int(income.replace(",", ""))
    if value > MAX_INCOME:
        return None
    return value


def monthly_emi(details):
    """Compute the monthly EMI from a 'principal,rate,years' string.

    principal : positive integer (rupees)
    rate      : annual interest rate in percent, 0 <= rate <= 100 (decimals allowed)
    years     : positive integer tenure

    Returns the EMI rounded to 2 decimals, or None for invalid input.
    """
    if not isinstance(details, str) or len(details) > MAX_INPUT_LEN:
        return None
    parts = [p.strip() for p in details.split(",")]
    if len(parts) != 3:                            # wrong number of fields
        return None
    principal_s, rate_s, years_s = parts
    if not (_INT_RE.fullmatch(principal_s) and _RATE_RE.fullmatch(rate_s)
            and _INT_RE.fullmatch(years_s)):
        return None

    principal = int(principal_s)
    rate = float(rate_s)
    years = int(years_s)
    if not (0 < principal <= MAX_PRINCIPAL and 0 <= rate <= MAX_RATE
            and 0 < years <= MAX_YEARS):
        return None

    r = rate / 1200                                # monthly interest rate
    n = years * 12                                 # number of monthly instalments
    # growth - 1 = (1 + r)**n - 1, computed in a numerically stable way so
    # that tiny rates never collapse to 0 and cause a ZeroDivisionError.
    growth_minus_1 = math.expm1(n * math.log1p(r))
    if r == 0 or growth_minus_1 == 0:
        emi = principal / n                        # interest-free loan
    else:
        emi = principal * r * (1 + growth_minus_1) / growth_minus_1
    if not math.isfinite(emi):
        return None
    return round(emi, 2)


def pan_category(pan):
    """Return the holder category encoded in the 4th character of a PAN.

    A valid PAN is 5 letters + 4 digits + 1 letter (e.g. ABCPE1234F).
    Returns None if the PAN is malformed or the category is unknown.
    """
    if not isinstance(pan, str):
        return None
    pan = pan.strip()
    if not _PAN_RE.fullmatch(pan):
        return None
    return CATEGORIES.get(pan[3].upper())


def main():
    print("==== Running parse_income ====")
    user_input = input("Enter monthly income (e.g. 50,000): ")
    result = parse_income(user_input)
    print("Income:", result if result is not None else "Invalid input")

    print("\n==== Running monthly_emi ====")
    user_input = input("Enter principal,rate,years (e.g. 500000,10,5): ")
    result = monthly_emi(user_input)
    print("Monthly EMI:", result if result is not None else "Invalid input")

    print("\n==== Running pan_category ====")
    user_input = input("Enter a PAN number (e.g. ABCPE1234F): ")
    result = pan_category(user_input)
    print("PAN Category:", result if result is not None else "Invalid input")


if __name__ == "__main__":
    main()
