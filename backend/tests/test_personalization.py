"""Layer 3: concept-level learner state + read-time lesson personalisation."""
from tests.conftest import submit_answers
from tests.test_assessment import perfect_answers
from tests.test_homework_validation import current_lesson, submit


def _enroll(client, name, email, answers):
    path_row = client.get("/api/paths/web-dev").json()
    return client.post(
        "/api/assessment/submit",
        json={"path_id": path_row["id"], "student_name": name, "student_email": email, "answers": answers},
    ).json()


def test_placement_records_concept_state_and_drives_focus(client, enrollment):
    lesson = current_lesson(client, enrollment)
    personalization = lesson["personalization"]
    # The fixture answered every placement question wrong, so review topics exist.
    focus = personalization["focus"]
    assert focus and all(entry["source"] == "assessment" for entry in focus)


def test_advanced_learner_gets_concise_delivery(client):
    result = _enroll(client, "Ace", "ace-personal@example.com",
                     perfect_answers(client, client.get("/api/paths/web-dev").json()["id"]))
    assert result["level"] == "Advanced"
    lesson = client.get(
        f"/api/enrollments/{result['enrollment_id']}/lesson",
        headers={"X-Enrollment-Token": result["access_token"]},
    ).json()
    p = lesson["personalization"]
    assert p["delivery_level"] == "concise"
    assert p["show_example"] is False
    assert p["challenge"]
    assert p["focus"] == []          # no misses -> nothing to revisit


def test_foundation_learner_gets_guided_delivery(client, enrollment):
    p = current_lesson(client, enrollment)["personalization"]
    assert p["delivery_level"] == "guided"
    assert p["show_example"] is True
    assert len(p["hints"]) >= 3


def test_struggling_learner_must_add_an_assert_before_advancing(client, enrollment):
    lesson = current_lesson(client, enrollment)
    patterns = lesson["assignment"]["required_patterns"]
    # Two failed attempts on this lesson are the evidence of struggle.
    submit(client, enrollment, lesson["id"], "value = 1")
    submit(client, enrollment, lesson["id"], "value = 1")

    guided = current_lesson(client, enrollment)["personalization"]
    assert guided["remediation"] is True
    assert "assert" in guided["extra_patterns"]

    base_ok = "\n".join(["value = 1", "value = value + 1"] + [f"# uses {p}" for p in patterns])
    body = submit(client, enrollment, lesson["id"], base_ok).json()
    assert body["passed"] is False
    assert any(item["pattern"] == "assert" and not item["found"] for item in body["checks"]["patterns"])

    fixed = base_ok + "\nassert value == 2"
    assert submit(client, enrollment, lesson["id"], fixed).json()["passed"] is True
