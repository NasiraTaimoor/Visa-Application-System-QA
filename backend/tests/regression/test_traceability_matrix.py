"""Validates full FR-001-FR-042 to TS-FR/TC-FR regression traceability
matrix (T173).

Checks two things: (1) the QA artifacts define exactly one TS-FR and one
TC-FR entry per functional requirement, and (2) every TS-FR/TC-FR id is
referenced by at least one test docstring/comment somewhere in this test
suite, so the traceability recorded throughout Phases 3-9 stays honest.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SPEC_DIR = REPO_ROOT / "specs" / "001-visa-application-lifecycle"
BACKEND_TESTS_DIR = Path(__file__).resolve().parent.parent

TOTAL_REQUIREMENTS = 42


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_scenarios_and_cases_cover_all_functional_requirements():
    scenarios = _read(SPEC_DIR / "qa-test-scenarios.md")
    cases = _read(SPEC_DIR / "qa-test-cases.md")

    ts_ids = sorted(set(re.findall(r"TS-FR-(\d{3})", scenarios)))
    tc_ids = sorted(set(re.findall(r"TC-FR-(\d{3})", cases)))

    expected = [f"{n:03d}" for n in range(1, TOTAL_REQUIREMENTS + 1)]
    assert ts_ids == expected, "qa-test-scenarios.md is missing or has extra TS-FR entries"
    assert tc_ids == expected, "qa-test-cases.md is missing or has extra TC-FR entries"


def _expand_ids(text: str, prefix: str) -> set[str]:
    """Docstrings cite requirement coverage either as a single id
    (`TS-FR-042`) or an inclusive range (`TS-FR-017-019` or the repeated-
    prefix form `TS-FR-005-TS-FR-011`); expand both to individual ids."""
    pattern = rf"{prefix}-(\d{{3}})(?:-(?:{prefix}-)?(\d{{3}}))?"
    found: set[str] = set()
    for start, end in re.findall(pattern, text):
        lo, hi = int(start), int(end) if end else int(start)
        for n in range(lo, hi + 1):
            found.add(f"{n:03d}")
    return found


def test_every_ts_fr_and_tc_fr_id_is_referenced_by_the_test_suite():
    all_test_text = ""
    for path in BACKEND_TESTS_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        all_test_text += _read(path)

    referenced_ts = _expand_ids(all_test_text, "TS-FR")
    referenced_tc = _expand_ids(all_test_text, "TC-FR")

    expected = {f"{n:03d}" for n in range(1, TOTAL_REQUIREMENTS + 1)}
    missing_ts = expected - referenced_ts
    missing_tc = expected - referenced_tc

    assert not missing_ts, f"no test references TS-FR-{sorted(missing_ts)}"
    assert not missing_tc, f"no test references TC-FR-{sorted(missing_tc)}"
