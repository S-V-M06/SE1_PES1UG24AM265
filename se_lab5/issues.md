# Issues Table – `dairy_collection.py`

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
