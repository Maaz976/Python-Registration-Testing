"""Black-box tests for the Student Course Registration System.

Expected results are derived from REQUIREMENTS.md (FR-01 to FR-15), not
from the implementation.  Keep registration.py unchanged during the
initial black-box test run.

Traceability:
- ECP-01 .. ECP-20: docs/blackbox_test_design.xlsx (ECP sheet)
- BVA-01 .. BVA-25: docs/blackbox_test_design.xlsx (BVA sheet)
- DT-01 .. DT-10: docs/decision_table.xlsx (Test Cases sheet)
- STATE-01 .. STATE-08: FR-10 to FR-14 registration/withdrawal state checks
"""

import pytest

from registration import (
    Course,
    Student,
    check_credit_limit,
    prerequisites_satisfied,
    register_course,
    registration_decision,
    withdraw_course,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_student(
    *,
    student_id="S001",
    completed_courses=None,
    current_credits=0,
    outstanding_dues=0,
    registered_courses=None,
):
    """Create a student with independent collection objects."""
    return Student(
        student_id=student_id,
        completed_courses=set(completed_courses or set()),
        current_credits=current_credits,
        outstanding_dues=outstanding_dues,
        registered_courses=set(registered_courses or set()),
    )


def make_course(
    *,
    code="CS201",
    credit_hours=3,
    capacity=30,
    enrolled=0,
    prerequisites=None,
    waitlist=None,
):
    """Create a course with independent collection objects."""
    return Course(
        code=code,
        credit_hours=credit_hours,
        capacity=capacity,
        enrolled=enrolled,
        prerequisites=set(prerequisites or set()),
        waitlist=list(waitlist or []),
    )


def snapshot(student, course):
    """Return immutable copies of all state relevant to the SRS."""
    student_state = (
        student.student_id,
        frozenset(student.completed_courses),
        student.current_credits,
        student.outstanding_dues,
        frozenset(student.registered_courses),
    )
    course_state = (
        course.code,
        course.credit_hours,
        course.capacity,
        course.enrolled,
        frozenset(course.prerequisites),
        tuple(course.waitlist),
    )
    return student_state, course_state


def assert_unchanged(student, course, before):
    """Assert that neither supplied object has changed."""
    assert snapshot(student, course) == before


# ---------------------------------------------------------------------------
# A1 — Equivalence Class Partitioning (ECP)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "current_credits,new_credits,expected",
    [
        pytest.param(10, 3, True, id="ECP-01"),
        pytest.param(16, 4, False, id="ECP-02"),
    ],
)
def test_ecp_check_credit_limit_valid_classes(current_credits, new_credits, expected):
    """ECP-01/02: valid numeric inputs with permitted/excess combined credits."""
    assert check_credit_limit(current_credits, new_credits) is expected


@pytest.mark.parametrize(
    "current_credits,new_credits,error_message",
    [
        pytest.param(-2, 2, "Invalid current credits", id="ECP-03"),
        pytest.param(20, 2, "Invalid current credits", id="ECP-04"),
        pytest.param(10, -1, "Invalid course credits", id="ECP-05"),
        pytest.param(10, 5, "Invalid course credits", id="ECP-06"),
    ],
)
def test_ecp_check_credit_limit_invalid_classes(
    current_credits, new_credits, error_message
):
    """ECP-03..06: invalid current-credit/course-credit equivalence classes."""
    with pytest.raises(ValueError, match=f"^{error_message}$"):
        check_credit_limit(current_credits, new_credits)


def test_ecp_07_zero_dues_allow_registration_decision():
    """ECP-07: zero dues are valid and an otherwise eligible student can register."""
    student = make_student(current_credits=5, outstanding_dues=0)
    course = make_course(credit_hours=3, capacity=5, enrolled=3)
    before = snapshot(student, course)

    assert registration_decision(student, course) == "REGISTERED"
    assert_unchanged(student, course, before)


def test_ecp_08_positive_dues_block_registration_decision():
    """ECP-08: every positive outstanding balance blocks registration."""
    student = make_student(outstanding_dues=50)
    course = make_course(credit_hours=2, capacity=8, enrolled=2)
    before = snapshot(student, course)

    assert registration_decision(student, course) == "DUES_BLOCK"
    assert_unchanged(student, course, before)


def test_ecp_09_negative_dues_raise_value_error():
    """ECP-09: negative dues are invalid under FR-15."""
    student = make_student(outstanding_dues=-5)
    course = make_course(capacity=5, enrolled=0)
    before = snapshot(student, course)

    with pytest.raises(ValueError, match="^Invalid dues$"):
        registration_decision(student, course)
    assert_unchanged(student, course, before)


def test_ecp_10_empty_prerequisite_set_is_satisfied():
    """ECP-10: no required prerequisites means the prerequisite condition passes."""
    assert prerequisites_satisfied(set(), set()) is True


def test_ecp_11_all_prerequisites_completed():
    """ECP-11: every required prerequisite has been completed."""
    completed = {"CS101", "MATH101"}
    required = {"CS101", "MATH101"}
    assert prerequisites_satisfied(completed, required) is True


def test_ecp_12_some_prerequisites_missing_blocks_registration():
    """ECP-12: one completed and one missing prerequisite must block registration."""
    student = make_student(completed_courses={"CS101"})
    course = make_course(prerequisites={"CS101", "MATH101"})
    before = snapshot(student, course)

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"
    assert_unchanged(student, course, before)


def test_ecp_13_no_prerequisites_completed_blocks_registration():
    """ECP-13: none of the required prerequisites has been completed."""
    student = make_student()
    course = make_course(prerequisites={"CS101", "MATH101"})
    before = snapshot(student, course)

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"
    assert_unchanged(student, course, before)


def test_ecp_14_seat_available_returns_registered():
    """ECP-14: enrollment below capacity returns REGISTERED."""
    student = make_student(current_credits=4)
    course = make_course(credit_hours=2, capacity=6, enrolled=2)
    before = snapshot(student, course)

    assert registration_decision(student, course) == "REGISTERED"
    assert_unchanged(student, course, before)


def test_ecp_15_course_full_returns_waitlisted():
    """ECP-15: an otherwise eligible student is waitlisted at exact capacity."""
    student = make_student(student_id="S015", current_credits=4)
    course = make_course(credit_hours=2, capacity=6, enrolled=6)
    before = snapshot(student, course)

    assert registration_decision(student, course) == "WAITLISTED"
    assert_unchanged(student, course, before)


@pytest.mark.parametrize(
    "capacity,enrolled",
    [
        pytest.param(0, 1, id="ECP-16"),
        pytest.param(5, 7, id="ECP-17"),
        pytest.param(5, -1, id="ECP-18"),
    ],
)
def test_ecp_invalid_capacity_or_enrollment(capacity, enrolled):
    """ECP-16..18: invalid course capacity/enrollment combinations raise ValueError."""
    student = make_student()
    course = make_course(capacity=capacity, enrolled=enrolled)
    before = snapshot(student, course)

    with pytest.raises(ValueError, match="^Invalid capacity or enrollment$"):
        registration_decision(student, course)
    assert_unchanged(student, course, before)


def test_ecp_19_already_registered_student_is_rejected():
    """ECP-19: an existing target-course registration returns ALREADY_REGISTERED."""
    student = make_student(current_credits=3, registered_courses={"CS219"})
    course = make_course(code="CS219", credit_hours=3, capacity=5, enrolled=1)
    before = snapshot(student, course)

    assert registration_decision(student, course) == "ALREADY_REGISTERED"
    assert_unchanged(student, course, before)


def test_ecp_20_negative_dues_validation_precedes_invalid_capacity():
    """ECP-20: FR-15 requires dues validation before capacity validation."""
    student = make_student(outstanding_dues=-5)
    course = make_course(capacity=0, enrolled=1)
    before = snapshot(student, course)

    with pytest.raises(ValueError, match="^Invalid dues$"):
        registration_decision(student, course)
    assert_unchanged(student, course, before)


# ---------------------------------------------------------------------------
# A2 — Boundary Value Analysis (BVA)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "current_credits,new_credits,expected",
    [
        pytest.param(-1, 1, "Invalid current credits", id="BVA-01"),
        pytest.param(0, 1, True, id="BVA-02"),
        pytest.param(1, 1, True, id="BVA-03"),
        pytest.param(17, 1, True, id="BVA-04"),
        pytest.param(18, 1, False, id="BVA-05"),
        pytest.param(19, 1, "Invalid current credits", id="BVA-06"),
        pytest.param(3, 0, "Invalid course credits", id="BVA-07"),
        pytest.param(3, 1, True, id="BVA-08"),
        pytest.param(3, 2, True, id="BVA-09"),
        pytest.param(3, 3, True, id="BVA-10"),
        pytest.param(3, 4, True, id="BVA-11"),
        pytest.param(3, 5, "Invalid course credits", id="BVA-12"),
        pytest.param(14, 3, True, id="BVA-13"),
        pytest.param(15, 3, True, id="BVA-14"),
        pytest.param(16, 3, False, id="BVA-15"),
    ],
)
def test_bva_credit_hour_boundaries(current_credits, new_credits, expected):
    """BVA-01..15: current-credit, course-credit and combined-credit boundaries."""
    if isinstance(expected, str):
        with pytest.raises(ValueError, match=f"^{expected}$"):
            check_credit_limit(current_credits, new_credits)
    else:
        assert check_credit_limit(current_credits, new_credits) is expected


@pytest.mark.parametrize(
    "student_kwargs,course_kwargs,expected",
    [
        pytest.param(
            {"current_credits": 0},
            {"credit_hours": 1, "capacity": 1, "enrolled": 0},
            "REGISTERED",
            id="BVA-16",
        ),
        pytest.param(
            {"current_credits": 0},
            {"credit_hours": 1, "capacity": 1, "enrolled": 1},
            "WAITLISTED",
            id="BVA-17",
        ),
        pytest.param(
            {"current_credits": 0},
            {"credit_hours": 1, "capacity": 30, "enrolled": 29},
            "REGISTERED",
            id="BVA-18",
        ),
        pytest.param(
            {"current_credits": 0},
            {"credit_hours": 1, "capacity": 30, "enrolled": 30},
            "WAITLISTED",
            id="BVA-19",
        ),
    ],
)
def test_bva_course_capacity_boundaries(student_kwargs, course_kwargs, expected):
    """BVA-16..19: the last available seat and exact-capacity transition."""
    student = make_student(**student_kwargs)
    course = make_course(**course_kwargs)
    before = snapshot(student, course)

    assert registration_decision(student, course) == expected
    assert_unchanged(student, course, before)


@pytest.mark.parametrize(
    "capacity,enrolled",
    [
        pytest.param(30, 31, id="BVA-20"),
        pytest.param(0, 0, id="BVA-21"),
        pytest.param(1, -1, id="BVA-22"),
    ],
)
def test_bva_invalid_capacity_and_enrollment(capacity, enrolled):
    """BVA-20..22: values just outside the valid capacity/enrollment region."""
    student = make_student()
    course = make_course(capacity=capacity, enrolled=enrolled)
    before = snapshot(student, course)

    with pytest.raises(ValueError, match="^Invalid capacity or enrollment$"):
        registration_decision(student, course)
    assert_unchanged(student, course, before)


@pytest.mark.parametrize(
    "dues,expected",
    [
        pytest.param(-1, "Invalid dues", id="BVA-23"),
        pytest.param(0, "REGISTERED", id="BVA-24"),
        pytest.param(1, "DUES_BLOCK", id="BVA-25"),
    ],
)
def test_bva_outstanding_dues_near_zero(dues, expected):
    """BVA-23..25: just below, at and just above zero outstanding dues."""
    student = make_student(outstanding_dues=dues)
    course = make_course(credit_hours=1, capacity=2, enrolled=1)
    before = snapshot(student, course)

    if expected == "Invalid dues":
        with pytest.raises(ValueError, match="^Invalid dues$"):
            registration_decision(student, course)
    else:
        assert registration_decision(student, course) == expected
    assert_unchanged(student, course, before)


# ---------------------------------------------------------------------------
# A3 — Decision Table Testing (DT)
# ---------------------------------------------------------------------------


DECISION_TABLE_CASES = [
    pytest.param(
        {"outstanding_dues": 1, "current_credits": 10, "completed_courses": {"CS101"}},
        {"credit_hours": 3, "prerequisites": {"CS101"}, "enrolled": 0, "capacity": 30},
        "DUES_BLOCK",
        id="DT-01",
    ),
    pytest.param(
        {
            "outstanding_dues": 1,
            "current_credits": 18,
            "registered_courses": {"CS201"},
            "completed_courses": set(),
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 30,
            "capacity": 30,
        },
        "DUES_BLOCK",
        id="DT-02",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 10,
            "registered_courses": {"CS201"},
            "completed_courses": {"CS101"},
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 0,
            "capacity": 30,
        },
        "ALREADY_REGISTERED",
        id="DT-03",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 18,
            "registered_courses": {"CS201"},
            "completed_courses": set(),
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 30,
            "capacity": 30,
        },
        "ALREADY_REGISTERED",
        id="DT-04",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 10,
            "registered_courses": set(),
            "completed_courses": set(),
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 0,
            "capacity": 30,
        },
        "PREREQUISITES_MISSING",
        id="DT-05",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 18,
            "registered_courses": set(),
            "completed_courses": set(),
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 30,
            "capacity": 30,
        },
        "PREREQUISITES_MISSING",
        id="DT-06",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 16,
            "registered_courses": set(),
            "completed_courses": {"CS101"},
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 29,
            "capacity": 30,
        },
        "CREDIT_LIMIT",
        id="DT-07",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 18,
            "registered_courses": set(),
            "completed_courses": {"CS101"},
        },
        {
            "code": "CS201",
            "credit_hours": 1,
            "prerequisites": {"CS101"},
            "enrolled": 30,
            "capacity": 30,
        },
        "CREDIT_LIMIT",
        id="DT-08",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 15,
            "registered_courses": set(),
            "completed_courses": {"CS101"},
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 30,
            "capacity": 30,
        },
        "WAITLISTED",
        id="DT-09",
    ),
    pytest.param(
        {
            "outstanding_dues": 0,
            "current_credits": 15,
            "registered_courses": set(),
            "completed_courses": {"CS101"},
        },
        {
            "code": "CS201",
            "credit_hours": 3,
            "prerequisites": {"CS101"},
            "enrolled": 29,
            "capacity": 30,
        },
        "REGISTERED",
        id="DT-10",
    ),
]


@pytest.mark.parametrize("student_kwargs,course_kwargs,expected", DECISION_TABLE_CASES)
def test_decision_table_registration_priority(student_kwargs, course_kwargs, expected):
    """DT-01..10: each distinct outcome and important higher-priority combinations."""
    student = make_student(**student_kwargs)
    course = make_course(**course_kwargs)
    before = snapshot(student, course)

    assert registration_decision(student, course) == expected
    # FR-10: the decision function must not mutate either input object.
    assert_unchanged(student, course, before)


# ---------------------------------------------------------------------------
# A4 — Registration and withdrawal state changes (FR-10 to FR-14)
# ---------------------------------------------------------------------------


def test_state_01_successful_registration_updates_student_and_course():
    """STATE-01 / FR-11: successful registration updates all three state values."""
    student = make_student(student_id="S100", current_credits=6)
    course = make_course(code="CS301", credit_hours=3, capacity=10, enrolled=4)

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS301" in student.registered_courses
    assert student.current_credits == 9
    assert course.enrolled == 5
    assert course.waitlist == []


def test_state_02_waitlisted_registration_adds_student_once_without_enrollment_change():
    """STATE-02 / FR-12: waiting-list entry is unique; credits/enrollment stay unchanged."""
    student = make_student(student_id="S101", current_credits=6)
    course = make_course(code="CS302", credit_hours=3, capacity=2, enrolled=2)

    first_result = register_course(student, course)
    assert first_result == "WAITLISTED"
    assert course.waitlist == ["S101"]
    assert student.current_credits == 6
    assert student.registered_courses == set()
    assert course.enrolled == 2

    # A repeated attempt must not add the same student twice (FR-12).
    second_result = register_course(student, course)
    assert second_result == "WAITLISTED"
    assert course.waitlist == ["S101"]
    assert student.current_credits == 6
    assert student.registered_courses == set()
    assert course.enrolled == 2


@pytest.mark.parametrize(
    "student_kwargs,course_kwargs,expected",
    [
        pytest.param(
            {"outstanding_dues": 1},
            {"credit_hours": 3, "capacity": 10, "enrolled": 0},
            "DUES_BLOCK",
            id="STATE-03-DUES_BLOCK",
        ),
        pytest.param(
            {"registered_courses": {"CS201"}},
            {"code": "CS201", "credit_hours": 3, "capacity": 10, "enrolled": 0},
            "ALREADY_REGISTERED",
            id="STATE-04-ALREADY_REGISTERED",
        ),
        pytest.param(
            {"completed_courses": set()},
            {"prerequisites": {"CS101"}, "credit_hours": 3, "capacity": 10, "enrolled": 0},
            "PREREQUISITES_MISSING",
            id="STATE-05-PREREQUISITES_MISSING",
        ),
        pytest.param(
            {"current_credits": 18, "completed_courses": {"CS101"}},
            {"prerequisites": {"CS101"}, "credit_hours": 1, "capacity": 10, "enrolled": 0},
            "CREDIT_LIMIT",
            id="STATE-06-CREDIT_LIMIT",
        ),
    ],
)
def test_state_unsuccessful_registration_does_not_change_objects(
    student_kwargs, course_kwargs, expected
):
    """STATE-03..06 / FR-11..12: rejected registration leaves both objects unchanged."""
    student = make_student(**student_kwargs)
    course = make_course(**course_kwargs)
    before = snapshot(student, course)

    assert register_course(student, course) == expected
    assert_unchanged(student, course, before)


def test_state_07_successful_withdrawal_updates_student_and_course():
    """STATE-07 / FR-13: withdrawal removes course, credits and one enrollment."""
    student = make_student(
        student_id="S107",
        current_credits=9,
        registered_courses={"CS307"},
    )
    course = make_course(code="CS307", credit_hours=3, capacity=10, enrolled=5)

    assert withdraw_course(student, course) is True
    assert "CS307" not in student.registered_courses
    assert student.current_credits == 6
    assert course.enrolled == 4


def test_state_08_withdrawal_when_not_registered_leaves_objects_unchanged():
    """STATE-08 / FR-14: a failed withdrawal returns False and changes no state."""
    student = make_student(current_credits=6, registered_courses={"CS101"})
    course = make_course(code="CS308", credit_hours=3, capacity=10, enrolled=5)
    before = snapshot(student, course)

    assert withdraw_course(student, course) is False
    assert_unchanged(student, course, before)


def test_state_09_registration_value_error_does_not_change_objects():
    """STATE-09 / FR-15: invalid registration input raises without state changes."""
    student = make_student(outstanding_dues=-1)
    course = make_course(capacity=0, enrolled=0)
    before = snapshot(student, course)

    with pytest.raises(ValueError, match="^Invalid dues$"):
        register_course(student, course)
    assert_unchanged(student, course, before)
