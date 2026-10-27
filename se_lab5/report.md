---
title: "Lab 5: Static Code Analysis"
author: "Shree Verdhan M (PES1UG24AM265)"
---

# 1. Objective and setup
Analyse and clean the assigned script `dairy_collection.py` (repo `SETAPESU26/L5_26_dairy_collection`) using Pylint, Bandit and Flake8, working in a Python virtual environment. The program (a dairy milk collection ledger) was run first and produced:

```
Total: 32.5 litres Lata ['Lata']
printing slip for Gopal
1d5830f86ae88c129b8d5793df204a0e
```

# 2. Results summary

| Tool | Before | After |
|------|--------|-------|
| Pylint | 2.00/10 (24 messages) | **10.00/10** |
| Bandit | 3 issues (2 High, 1 Medium) | **0 issues** |
| Flake8 | 7 warnings | **0 warnings** |

# 3. Commits

| # | Commit | Tool | What changed |
|---|--------|------|--------------|
| 1 | 88bc652 | Bandit | Parameterised SQL, MD5 to SHA-256, removed `os.system` |
| 2 | 8081cf1 | Flake8 | Removed unused import, wrapped long lines, renamed `l`, `is None` |
| 3 | 0d56e58 | Pylint | Docstrings, snake_case, no global connection, `__main__` guard, f-strings, empty-table fix |

# 4. Issue table
| Issue | Type | Line(s) (original) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| SQL injection (Bandit B608, **Medium**) | Security | 11 | `INSERT` built with `str.format()`; a farmer name like `x'); DROP TABLE milk;--` becomes SQL | Parameterised query with `?` placeholders |
| Weak MD5 hash (Bandit B324, **High**) | Security | 16 | `hashlib.md5` is broken and unsuitable for identifying/tokenising people | Switched to `hashlib.sha256` |
| Shell command injection (Bandit B605, **High**) | Security | 31 | `os.system("echo ..." + farmer)` passes user input to a shell | Removed shell call; use `print()` (no `os` import needed) |
| Unused import (Flake8 F401 / Pylint W0611) | Style | 2 | `json` imported but never used | Removed import |
| Lines too long (Flake8 E501 / Pylint C0301) | Style | 7, 11, 20, 25 | Lines of 83–124 chars exceed 79 | Wrapped SQL strings and calls across lines |
| Ambiguous name `l` (Flake8 E741) | Style | 26 | Single letter `l` looks like `1`/`I` | Renamed to `top` |
| `== None` (Flake8 E711 / Pylint C0121) | Bug-risk | 36 | Equality comparison with `None` | Changed to `is None` |
| Missing docstrings (Pylint C0114, C0116) | Quality | 1, all functions | No module or function docstrings | Added docstrings |
| Non-snake_case names (Pylint C0103) | Quality | 10, 15, 19, 24, 30, 34 | `recordMilk`, `farmerToken`, ... break PEP 8 | Renamed to `record_milk`, `farmer_token`, `daily_total`, `top_farmer`, `print_slip`, `low_fat` |
| Redefined outer name `conn` (Pylint W0621) | Design | 6, 10, 19, 24, 34 | Global `conn` shadowed by parameters; global DB created at import | Added `create_connection()`; `conn` is now local to `main()` |
| Old-style formatting (Pylint C0209) | Quality | 11, 21 | `%` / `.format()` instead of f-strings | Used f-string |
| Crash on empty table (logic bug) | Bug | 25-27 | `max()` on empty list raises `ValueError` in `topFarmer` | Return `None` when there are no rows |
| Code runs on import | Design | 47 | `main()` called at module level | Added `if __name__ == "__main__":` guard |
| Magic number | Quality | 36 | `3.5` hard-coded | Named constant `LOW_FAT_THRESHOLD` |

# 5. Verification
After each commit the relevant tool was re-run and the program output re-checked: it prints the same total, top farmer, low-fat list, slip line (the token differs only because SHA-256 replaced MD5). A test with a malicious farmer name was stored as plain data (no SQL executed), and `top_farmer` on an empty table now returns `None` instead of crashing.

# 6. Reflection


**1. Which issues were the easiest to fix and which were the hardest?**
The easiest were the Flake8 style items (unused import, `is None`, renaming `l`, wrapping long lines) because the tool names the exact line and the fix is mechanical. The hardest were the security findings: removing `os.system` and building SQL safely required understanding *why* the pattern is dangerous (user data reaching a shell or the SQL parser) and choosing a replacement that kept behaviour identical. The Pylint `redefined-outer-name` warning was also harder, as it meant restructuring the global `conn` into a `create_connection()` function.


**2. Did the tools report any false positives, or miss anything?**
There were no outright false positives. Bandit's B324 on MD5 is arguably context-dependent (MD5 is acceptable for non-security checksums), but here the value identifies a farmer, so changing to SHA-256 was justified. The tools also missed a logic bug: `top_farmer` crashes with `ValueError` on an empty table. Static analysis cannot find every defect, so tests are still needed. Also, treating a missing fat reading as "low fat" is a business decision no tool could judge.


**3. How could static analysis be integrated into a real workflow?**
Run Flake8, Pylint and Bandit as pre-commit hooks locally and again in CI (e.g. GitHub Actions) on every pull request, failing the build if Bandit finds Medium/High issues or the Pylint score drops below a threshold (e.g. 9.5). Configuration files (`.flake8`, `.pylintrc`, `bandit.yaml`) keep rules consistent across the team.


**4. What tangible improvements did you see in code quality, security and readability?**
Pylint rose from 2.00/10 to 10.00/10, Bandit went from 3 findings (2 High, 1 Medium) to zero, and Flake8 from 7 warnings to zero. The program's output is unchanged, but the code is now safe from SQL and shell injection, uses a modern hash, is documented, follows PEP 8 naming, can be imported without side effects, and is easier to test because the database connection is no longer global.
