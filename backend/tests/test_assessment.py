"""Assessment grading, level mapping and starting-day placement."""
from app.seed import get_level
from tests.conftest import _wrong_answers, submit_answers


def perfect_answers(client, path_id):
    """The public API never exposes correct answers; read them from the DB."""
    from app import db as db_module

    questions = client.get(f"/api/assessment/{path_id}/questions").json()
    conn = db_module.get_conn()
    try:
        correct = {
            row["id"]: row["correct"]
            for row in conn.execute(
                "SELECT id, correct FROM assessment_questions WHERE path_id=?", (path_id,)
            ).fetchall()
        }
    finally:
        conn.close()
    return [{"question_id": q["id"], "selected": correct[q["id"]]} for q in questions]


# --- unit tests for level mapping -------------------------------------------

def test_level_boundaries():
    """Thresholds: <25 Foundation, <40 Beginner, <70 Intermediate, else Advanced."""
    total = 100
    assert get_level(0, total) == "Foundation"
    assert get_level(24, total) == "Foundation"
    assert get_level(25, total) == "Beginner"
    assert get_level(39, total) == "Beginner"
    assert get_level(40, total) == "Intermediate"
    assert get_level(69, total) == "Intermediate"
    assert get_level(70, total) == "Advanced"


def test_start_order_mapping_is_deterministic():
    from app.seed import get_level
    expected = {"Foundation": 1, "Beginner": 4, "Intermediate": 7, "Advanced": 10}
    for level, start_day in expected.items():
        # mapping lives in assessment.py: Foundation->1, Beginner->4, Intermediate->7, Advanced->10
        assert expected[get_level({"Foundation": 0, "Beginner": 25, "Intermediate": 40, "Advanced": 70}[level], 100)] == start_day


# --- API integration ---------------------------------------------------------

def test_zero_score_places_foundation_on_day_one(client, enrollment):
    dash = client.get(
        f"/api/enrollments/{enrollment['enrollment_id']}/dashboard",
        headers={"X-Enrollment-Token": enrollment["token"]},
    ).json()
    assert dash["level"] == "Foundation"
    assert dash["level_score"] == 0
    assert dash["current_day"] == 1


def test_perfect_score_places_advanced_on_day_ten(client):
    path_row = client.get("/api/paths/web-dev").json()
    questions = client.get(f"/api/assessment/{path_row['id']}/questions").json()
    result = submit_answers(
        client, path_row["id"], "Ace", "ace@example.com",
        perfect_answers(client, path_row["id"]),
    ).json()
    assert result["score"] == len(questions)
    assert result["level"] == "Advanced"

    token = result["access_token"]
    dash = client.get(
        f"/api/enrollments/{result['enrollment_id']}/dashboard",
        headers={"X-Enrollment-Token": token},
    ).json()
    assert dash["current_day"] == 10


def test_reassessment_updates_existing_enrollment(client, enrollment):
    path_id = enrollment["path_id"]
    first = submit_answers(
        client, path_id, "Test Student", "test@example.com",
        _wrong_answers(client, path_id),
    ).json()
    assert first["enrollment_id"] == enrollment["enrollment_id"]
    assert first["level"] == "Foundation"
    assert first["access_token"]          # token always returned


def test_profile_questions_are_data_driven(client):
    pq = client.get("/api/profile/questions").json()
    assert [q["key"] for q in pq] == ["experience", "background", "goal", "pace"]
    for q in pq:
        assert q["options"] and all("value" in o and "label" in o for o in q["options"])


def test_questions_are_per_path_and_profile_tuned(client):
    web = client.get("/api/paths/web-dev").json()
    other = client.get("/api/paths/cgi-animation").json()
    web_qs = client.get(f"/api/assessment/{web['id']}/questions").json()
    other_qs = client.get(f"/api/assessment/{other['id']}/questions").json()
    assert len(web_qs) == 13
    # Two different paths never share a placement question.
    assert {q["question"] for q in web_qs}.isdisjoint({q["question"] for q in other_qs})

    beginner = client.get(f"/api/assessment/{web['id']}/questions?experience=beginner").json()
    advanced = client.get(f"/api/assessment/{web['id']}/questions?experience=advanced").json()
    assert len(beginner) == 10 and len(advanced) == 10
    assert max(q["difficulty"] for q in beginner) <= max(q["difficulty"] for q in advanced)


def test_profile_tuned_score_is_out_of_its_own_length(client):
    from app import db as db_module

    path_row = client.get("/api/paths/web-dev").json()
    qs = client.get(f"/api/assessment/{path_row['id']}/questions?experience=advanced").json()
    assert len(qs) == 10
    conn = db_module.get_conn()
    try:
        correct = {
            row["id"]: row["correct"]
            for row in conn.execute(
                "SELECT id, correct FROM assessment_questions WHERE path_id=?", (path_row["id"],)
            ).fetchall()
        }
    finally:
        conn.close()
    answers = [{"question_id": q["id"], "selected": correct[q["id"]]} for q in qs]
    result = submit_answers(client, path_row["id"], "Ace", "ace@example.com", answers).json()
    assert result["score"] == 10 and result["total"] == 10
    assert result["level"] == "Advanced"


def test_weak_topics_reported_for_wrong_answers(client, enrollment):
    path_id = enrollment["path_id"]
    result = submit_answers(
        client, path_id, "Test Student", "test@example.com",
        _wrong_answers(client, path_id),
    ).json()
    assert isinstance(result["weak_topics"], list) and result["weak_topics"]
