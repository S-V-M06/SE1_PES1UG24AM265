# Reflection

*(The handout PDF provided does not list the four reflection questions, so these are the standard Lab 5 questions. Replace the headings if your handout words them differently.)*

**1. Which issues were the easiest to fix and which were the hardest?**
The easiest were the Flake8 style items (unused import, `is None`, renaming `l`, wrapping long lines) because the tool names the exact line and the fix is mechanical. The hardest were the security findings: removing `os.system` and building SQL safely required understanding *why* the pattern is dangerous (user data reaching a shell or the SQL parser) and choosing a replacement that kept behaviour identical. The Pylint `redefined-outer-name` warning was also harder, as it meant restructuring the global `conn` into a `create_connection()` function.

**2. Did the tools report any false positives, or miss anything?**
There were no outright false positives. Bandit's B324 on MD5 is arguably context-dependent (MD5 is acceptable for non-security checksums), but here the value identifies a farmer, so changing to SHA-256 was justified. The tools also missed a logic bug: `top_farmer` crashes with `ValueError` on an empty table. Static analysis cannot find every defect, so tests are still needed. Also, treating a missing fat reading as "low fat" is a business decision no tool could judge.

**3. How could static analysis be integrated into a real workflow?**
Run Flake8, Pylint and Bandit as pre-commit hooks locally and again in CI (e.g. GitHub Actions) on every pull request, failing the build if Bandit finds Medium/High issues or the Pylint score drops below a threshold (e.g. 9.5). Configuration files (`.flake8`, `.pylintrc`, `bandit.yaml`) keep rules consistent across the team.

**4. What tangible improvements did you see in code quality, security and readability?**
Pylint rose from 2.00/10 to 10.00/10, Bandit went from 3 findings (2 High, 1 Medium) to zero, and Flake8 from 7 warnings to zero. The program's output is unchanged, but the code is now safe from SQL and shell injection, uses a modern hash, is documented, follows PEP 8 naming, can be imported without side effects, and is easier to test because the database connection is no longer global.
