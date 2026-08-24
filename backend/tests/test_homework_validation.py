"""Homework rubric validation: syntax, whitespace tolerance, min lines."""
from app.routers.lessons import pattern_found


def current_lesson(client, enrollment):
    response = client.get(
        f"/api/enrollments/{enrollment['enrollment_id']}/lesson",
        headers={"X-Enrollment-Token": enrollment["token"]},
    )
    assert response.status_code == 200
    return response.json()


def submit(client, enrollment, lesson_id, code):
    return client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": lesson_id, "code": code},
        headers={"X-Enrollment-Token": enrollment["token"]},
    )


# --- pure unit tests for the pattern matcher -------------------------------

def test_print_with_no_space_matches():
    assert pattern_found("print(", 'print("hello")')


def test_print_with_space_before_paren_matches():
    assert pattern_found("print(", 'print ("hello")')


def test_print_with_newline_before_paren_matches():
    assert pattern_found("print(", "print\n('hello')")


def test_prefixed_name_does_not_match():
    assert not pattern_found("print(", 'myprint("hello")')


def test_def_keyword_matches_but_define_does_not():
    assert pattern_found("def ", "def foo(): pass")
    assert not pattern_found("def ", "define = 5")


def test_try_colon_tolerates_space():
    assert pattern_found("try:", "try :\n    pass")


# --- API integration --------------------------------------------------------

def test_syntax_error_reports_line_and_fails(client, enrollment):
    lesson = current_lesson(client, enrollment)
    response = submit(client, enrollment, lesson["id"], "print('hi'\n")
    body = response.json()
    assert body["passed"] is False
    assert body["checks"]["syntax_ok"] is False
    assert "Syntax error" in body["feedback"]


def test_too_few_lines_fails_with_actionable_feedback(client, enrollment):
    lesson = current_lesson(client, enrollment)
    code = "name = 'riya'\nprint('Hello, ' + name)"          # 2 lines < 3
    body = submit(client, enrollment, lesson["id"], code).json()
    assert body["passed"] is False
    assert body["checks"]["lines_written"] == 2
    assert body["checks"]["min_lines"] == 3
    assert "at least 3" in body["feedback"]


def test_missing_required_pattern_fails(client, enrollment):
    lesson = current_lesson(client, enrollment)
    code = "a = 1\nb = 2\nc = a + b"                          # no print(
    body = submit(client, enrollment, lesson["id"], code).json()
    assert body["passed"] is False
    missing = [p for p in body["checks"]["patterns"] if not p["found"]]
    assert any(p["pattern"] == "print(" for p in missing)


def test_spaced_print_now_passes_the_rubric(client, enrollment):
    """Regression: the original bug — 'print (' failed a literal substring check."""
    lesson = current_lesson(client, enrollment)
    code = "name = 'riya'\ngoal = 'learn python'\nprint ('Hello, ' + name)"
    body = submit(client, enrollment, lesson["id"], code).json()
    assert body["passed"] is True, body["feedback"]
    assert body["checks"]["syntax_ok"] is True
    assert all(p["found"] for p in body["checks"]["patterns"])


def test_valid_submission_passes_and_awards_xp_once(client, enrollment):
    lesson = current_lesson(client, enrollment)
    code = "name = 'riya'\nprint('Hello, ' + name)\nprint('Goal set')"
    first = submit(client, enrollment, lesson["id"], code).json()
    second = submit(client, enrollment, lesson["id"], code).json()
    assert first["passed"] is True and second["passed"] is True

    dashboard = client.get(
        f"/api/enrollments/{enrollment['enrollment_id']}/dashboard",
        headers={"X-Enrollment-Token": enrollment["token"]},
    ).json()
    assert dashboard["xp"] == 15      # awarded once despite two passing submits


def test_submit_without_token_rejected(client, enrollment):
    lesson = current_lesson(client, enrollment)
    response = client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": lesson["id"], "code": "x=1"},
    )
    assert response.status_code == 401


def test_submit_with_wrong_token_rejected(client, enrollment):
    lesson = current_lesson(client, enrollment)
    response = client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": lesson["id"], "code": "x=1"},
        headers={"X-Enrollment-Token": "forged-token"},
    )
    assert response.status_code == 401
