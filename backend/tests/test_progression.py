"""Day progression: gates, completion side-effects, XP/streak."""
PASSING_CODE = "name = 'riya'\nprint('Hello, ' + name)\nprint('Goal set')"


def lesson(client, enrollment, expect=200):
    response = client.get(
        f"/api/enrollments/{enrollment['enrollment_id']}/lesson",
        headers={"X-Enrollment-Token": enrollment["token"]},
    )
    assert response.status_code == expect
    return response.json()


def dashboard(client, enrollment):
    response = client.get(
        f"/api/enrollments/{enrollment['enrollment_id']}/dashboard",
        headers={"X-Enrollment-Token": enrollment["token"]},
    )
    assert response.status_code == 200
    return response.json()


def complete(client, enrollment):
    return client.post(
        f"/api/enrollments/{enrollment['enrollment_id']}/complete",
        headers={"X-Enrollment-Token": enrollment["token"]},
    )


def test_complete_blocked_without_passing_homework(client, enrollment):
    assert complete(client, enrollment).status_code == 409
    body = dashboard(client, enrollment)
    assert body["current_day"] == 1


def test_complete_blocked_until_lesson_marked_read(client, enrollment):
    """UI gate: the button requires read-checkbox; API gate is the passed rubric.
    Here we verify the API still refuses when no pass exists even with reads."""
    lesson(client, enrollment)                       # viewed but not passed
    assert complete(client, enrollment).status_code == 409


def test_failed_submission_cannot_unlock_next_day(client, enrollment):
    current = lesson(client, enrollment)
    failing = client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": current["id"],
              "code": "print('too short')"},
        headers={"X-Enrollment-Token": enrollment["token"]},
    ).json()
    assert failing["passed"] is False
    assert complete(client, enrollment).status_code == 409
    assert dashboard(client, enrollment)["current_day"] == 1


def test_passing_submission_then_complete_advances_day(client, enrollment):
    current = lesson(client, enrollment)
    result = client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": current["id"],
              "code": PASSING_CODE},
        headers={"X-Enrollment-Token": enrollment["token"]},
    ).json()
    assert result["passed"] is True

    completed = complete(client, enrollment)
    assert completed.status_code == 200
    payload = completed.json()
    assert payload["current_day"] == 2

    body = dashboard(client, enrollment)
    assert body["current_day"] == 2
    assert body["xp"] == 25            # 15 (first passing submit) + 10 (completion)
    assert body["streak"] == 1


def test_completion_records_attendance_progress_and_mastery(client, enrollment, tmp_path):
    from app import db as db_module

    current = lesson(client, enrollment)
    client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": current["id"],
              "code": PASSING_CODE},
        headers={"X-Enrollment-Token": enrollment["token"]},
    )
    assert complete(client, enrollment).status_code == 200

    conn = db_module.get_conn()
    try:
        eid = enrollment["enrollment_id"]
        attendance = conn.execute(
            "SELECT present FROM attendance WHERE enrollment_id=? AND day=1", (eid,)
        ).fetchone()
        progress = conn.execute(
            "SELECT status, passed FROM lesson_progress WHERE enrollment_id=?", (eid,)
        ).fetchone()
        mastery = conn.execute(
            "SELECT code_passed, status FROM mastery_records WHERE enrollment_id=?", (eid,)
        ).fetchone()
    finally:
        conn.close()

    assert attendance and attendance["present"] == 1
    assert progress and progress["status"] == "completed" and progress["passed"] == 1
    assert mastery and mastery["code_passed"] == 1 and mastery["status"] == "ready_for_review"


def test_double_clicking_complete_is_safe(client, enrollment):
    current = lesson(client, enrollment)
    client.post(
        "/api/homework/submit",
        json={"enrollment_id": enrollment["enrollment_id"], "lesson_id": current["id"],
              "code": PASSING_CODE},
        headers={"X-Enrollment-Token": enrollment["token"]},
    )
    assert complete(client, enrollment).status_code == 200
    second = complete(client, enrollment)
    # Second click must not crash nor advance twice: day 1 is done, so it 409s.
    assert second.status_code == 409
    assert dashboard(client, enrollment)["current_day"] == 2
