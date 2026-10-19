"""Pydantic schemas for PySchool API."""
from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    depth_label: str
    sort_order: int


class PathOut(BaseModel):
    id: int
    category_id: int
    name: str
    description: str
    libraries: str
    slug: str
    difficulty: int


class PathDetailOut(PathOut):
    category_name: str
    category_icon: str
    assessment_count: int


class QuestionOut(BaseModel):
    id: int
    path_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: int


class AssessmentAnswer(BaseModel):
    question_id: int
    selected: str


class AssessmentSubmit(BaseModel):
    path_id: int
    student_name: str
    student_email: str
    answers: list[AssessmentAnswer]
    profile: dict = {}


class AssessmentResultOut(BaseModel):
    enrollment_id: int
    student_id: int
    path_id: int
    score: int
    total: int
    level: str
    feedback: str


class LessonOut(BaseModel):
    id: int
    path_id: int
    day_number: int
    title: str
    theory: str
    code_example: str
    questions: list[str]
    answers: list[str]
    homework: str


class HomeworkSubmit(BaseModel):
    enrollment_id: int
    lesson_id: int
    code: str


class HomeworkResultOut(BaseModel):
    passed: bool
    feedback: str


class EnrollmentOut(BaseModel):
    id: int
    path_id: int
    path_name: str
    level: str
    level_score: int
    current_day: int
    streak: int
    penalty_points: int
    xp: int


class StudentCreate(BaseModel):
    name: str
    email: str


class AttendanceOut(BaseModel):
    day: int
    date: str
    present: int
