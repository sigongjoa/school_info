"""Tests for src/models.py"""
import pytest
from src.models import Subject, Curriculum, AchievementStat, SchoolData


def test_subject_creation():
    """Test Subject model creation"""
    subject = Subject(name="Math", code="MAT101", credit=3.0, semester=1)

    assert subject.name == "Math"
    assert subject.code == "MAT101"
    assert subject.credit == 3.0
    assert subject.semester == 1


def test_subject_defaults():
    """Test Subject model with defaults"""
    subject = Subject(name="English")

    assert subject.name == "English"
    assert subject.code is None
    assert subject.credit == 0.0
    assert subject.semester == 1


def test_curriculum_creation():
    """Test Curriculum model creation"""
    subjects = [
        Subject(name="Math", credit=3.0),
        Subject(name="English", credit=2.0)
    ]
    curriculum = Curriculum(year=2024, grade=7, subjects=subjects)

    assert curriculum.year == 2024
    assert curriculum.grade == 7
    assert len(curriculum.subjects) == 2
    assert curriculum.subjects[0].name == "Math"


def test_curriculum_empty_subjects():
    """Test Curriculum with empty subjects"""
    curriculum = Curriculum(year=2024, grade=7)

    assert curriculum.subjects == []


def test_achievement_stat_creation():
    """Test AchievementStat model creation"""
    stat = AchievementStat(
        grade=7,
        semester=1,
        subject="Math",
        mean=85.5,
        std_dev=10.2,
        grade_distribution={"A": 0.3, "B": 0.4, "C": 0.2, "D": 0.08, "E": 0.02}
    )

    assert stat.grade == 7
    assert stat.semester == 1
    assert stat.subject == "Math"
    assert stat.mean == 85.5
    assert stat.std_dev == 10.2
    assert stat.grade_distribution["A"] == 0.3
    assert len(stat.grade_distribution) == 5


def test_school_data_creation():
    """Test SchoolData model creation"""
    school = SchoolData(
        school_code="B100000662",
        school_name="동도중학교",
        address="서울시 강남구",
        founding_date="2000-03-01"
    )

    assert school.school_code == "B100000662"
    assert school.school_name == "동도중학교"
    assert school.address == "서울시 강남구"
    assert school.founding_date == "2000-03-01"
    assert school.curriculum == []
    assert school.achievement_stats == []


def test_school_data_with_curriculum():
    """Test SchoolData with curriculum"""
    curriculum = Curriculum(
        year=2024,
        grade=7,
        subjects=[Subject(name="Math", credit=3.0)]
    )
    school = SchoolData(
        school_code="TEST001",
        school_name="Test School",
        curriculum=[curriculum]
    )

    assert len(school.curriculum) == 1
    assert school.curriculum[0].year == 2024
    assert school.curriculum[0].subjects[0].name == "Math"


def test_school_data_with_stats():
    """Test SchoolData with achievement stats"""
    stat = AchievementStat(
        grade=7,
        semester=1,
        subject="Math",
        mean=85.0,
        std_dev=10.0,
        grade_distribution={"A": 0.3, "B": 0.4, "C": 0.3}
    )
    school = SchoolData(
        school_code="TEST002",
        school_name="Test School 2",
        achievement_stats=[stat]
    )

    assert len(school.achievement_stats) == 1
    assert school.achievement_stats[0].subject == "Math"
    assert school.achievement_stats[0].mean == 85.0


def test_school_data_optional_fields():
    """Test SchoolData with minimal required fields"""
    school = SchoolData(
        school_code="MIN001",
        school_name="Minimal School"
    )

    assert school.school_code == "MIN001"
    assert school.school_name == "Minimal School"
    assert school.address is None
    assert school.founding_date is None
