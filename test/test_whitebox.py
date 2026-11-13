"""Part B4: structural tests for ``registration_decision``.

Traceability: docs/White-Box-Testing.docx, Part B3, cases WB-CC-01..11.
Expected outcomes follow REQUIREMENTS.md (FR-04, FR-05, FR-06, FR-07,
FR-08, FR-10 and FR-15). They must not be weakened to match defective code.

Structural condition IDs from the report:
    D1  : negative outstanding dues
    D2a : enrolled < 0                (A in the MC/DC table)
    D2b : enrolled > capacity         (B in the MC/DC table)
    D2c : capacity < 1                (C in the MC/DC table)
    D3  : supplied-code dues threshold (> 1000)
    D4  : duplicate registration
    D5  : missing prerequisites
    D6  : credit ineligibility
    D7  : later availability check; True is unreachable in supplied code

MC/DC independent-effect pairs for D2 = A or B or C:
    A: WB-CC-03 (True) vs WB-CC-02 (False)
    B: WB-CC-04 (True) vs WB-CC-02 (False)
    C: WB-CC-05 (True) vs WB-CC-02 (False)

The MC/DC pairs intentionally share one baseline instead of rerunning it
three times. ``pytest-cov`` does not directly measure MC/DC; document the
manual 3/3 result separately. Run this file WITHOUT editing registration.py.
"""

from copy import deepcopy

import pytest

from registration import Course, Student, registration_decision


def _baseline_objects():
    """Create fresh valid objects so one test cannot affect another."""
    student = Student(
        student_id="WB001",
        completed_courses=set(),
        current_credits=6,
        outstanding_dues=0,
        registered_courses=set(),
    )
    course = Course(
        code="CS201",
        credit_hours=3,
        capacity=10,
        enrolled=0,
        prerequisites=set(),
        waitlist=[],
    )
    return student, course


def _configure_objects(student_changes, course_changes):
    student, course = _baseline_objects()
    for key, value in student_changes.items():
        setattr(student, key, value)
    for key, value in course_changes.items():
        setattr(course, key, value)
    return student, course


@pytest.mark.parametrize(
    "student_changes,course_changes,error_message",
    [
        # WB-CC-01: D1 True: negative dues raises before all other predicates.
        pytest.param(
            {"outstanding_dues": -1}, {}, "Invalid dues", id="WB-CC-01"
        ),
        # WB-CC-03: D2a/A True, D2b/B and D2c/C not evaluated.
        pytest.param(
            {}, {"enrolled": -1}, "Invalid capacity or enrollment", id="WB-CC-03"
        ),
        # WB-CC-04: D2a/A False, D2b/B True, D2c/C not evaluated.
        pytest.param(
            {}, {"enrolled": 11}, "Invalid capacity or enrollment", id="WB-CC-04"
        ),
        # WB-CC-05: D2a/A False, D2b/B False, D2c/C True.
        pytest.param(
            {}, {"capacity": 0}, "Invalid capacity or enrollment", id="WB-CC-05"
        ),
    ],
)
def test_whitebox_validation_and_short_circuit(
    student_changes, course_changes, error_message
):
    """FR-15: cover early raise paths and the three D2 MC/DC True cases."""
    student, course = _configure_objects(student_changes, course_changes)
    before = deepcopy((student, course))

    with pytest.raises(ValueError, match=f"^{error_message}$"):
        registration_decision(student, course)

    # FR-10: even failing decisions must not mutate the inputs.
    assert (student, course) == before


@pytest.mark.parametrize(
    "student_changes,course_changes,expected_status",
    [
        # WB-CC-02: all D1..D7 evaluated False, REGISTERED; MC/DC baseline.
        pytest.param({}, {}, "REGISTERED", id="WB-CC-02"),
        # WB-CC-06: D3 True (dues > 1000) reaches previously missed line 51.
        pytest.param(
            {"outstanding_dues": 1500}, {}, "DUES_BLOCK", id="WB-CC-06"
        ),
        # WB-CC-07: D4 True; earlier validation and D3 are False.
        pytest.param(
            {"registered_courses": {"CS201"}},
            {},
            "ALREADY_REGISTERED",
            id="WB-CC-07",
        ),
        # WB-CC-08: D5 True; prerequisite is absent from completed courses.
        pytest.param(
            {},
            {"prerequisites": {"CS101"}},
            "PREREQUISITES_MISSING",
            id="WB-CC-08",
        ),
        # WB-CC-09: D6 True, 17 + 3 exceeds FR-07's 18-credit maximum.
        pytest.param(
            {"current_credits": 17}, {}, "CREDIT_LIMIT", id="WB-CC-09"
        ),
        # WB-CC-10: D7 remains False at exact capacity (FR-08 DEFECT).
        # The correct expected status is WAITLISTED; the original code returns
        # REGISTERED. Preserve this legitimate failure for GitHub Issue evidence.
        pytest.param({}, {"enrolled": 10}, "WAITLISTED", id="WB-CC-10"),
        # WB-CC-11: D3 is False at dues=1 although FR-04 requires blocking.
        # The correct expected status is DUES_BLOCK; do not change it to pass.
        pytest.param(
            {"outstanding_dues": 1}, {}, "DUES_BLOCK", id="WB-CC-11"
        ),
    ],
)
def test_whitebox_registration_decision_priority(
    student_changes, course_changes, expected_status
):
    """FR-04..FR-10: cover each return path and expose two known defects."""
    student, course = _configure_objects(student_changes, course_changes)
    before = deepcopy((student, course))

    actual_status = registration_decision(student, course)
    assert (student, course) == before
    assert actual_status == expected_status
