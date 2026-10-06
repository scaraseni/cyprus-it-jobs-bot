import asyncio

import pytest

import jobs
from jobs import is_junior, is_relevant


def make_job(title, location="Limassol"):
    return {
        "company": "TestCo",
        "title": title,
        "location": location,
        "url": "https://example.com/job",
    }


@pytest.mark.parametrize(
    "title",
    [
        "Manual QA Tester",
        "Junior Software Developer",
        "QA Software Test Automation Engineers (Java)",
        "Software Development Engineers in Test (Python)",
        "Angular Developers",
        "Junior Corporate Services Systems Engineer",
    ],
)
def test_relevant_titles_are_accepted(title):
    assert is_relevant(make_job(title))


@pytest.mark.parametrize(
    "title",
    [
        "Senior QA Engineer",
        "Head of QA",
        "Lead Software Developer",
        "QA Manager",
        "Junior Dealer",
        "Customer Support Specialist",
        "International Customer Experience Coordinator",
    ],
)
def test_irrelevant_titles_are_rejected(title):
    assert not is_relevant(make_job(title))


@pytest.mark.parametrize("location", ["Limassol", "Limassol, Cyprus", "NICOSIA"])
def test_cyprus_locations_are_accepted(location):
    assert is_relevant(make_job("QA Engineer", location))


@pytest.mark.parametrize("location", ["Berlin, Germany", ""])
def test_other_locations_are_rejected(location):
    assert not is_relevant(make_job("QA Engineer", location))


@pytest.mark.parametrize(
    "title",
    [
        "Junior QA Engineer",
        "Software Engineering Intern",
        "Graduate Software Developer",
        "Trainee Tester",
        "Entry Level Developer",
    ],
)
def test_junior_titles_are_detected(title):
    assert is_junior(make_job(title))


@pytest.mark.parametrize(
    "title",
    ["Senior Developer", "QA Engineer", "International Sales Manager"],
)
def test_non_junior_titles_are_not_marked(title):
    assert not is_junior(make_job(title))


def test_get_relevant_jobs_filters_and_puts_junior_first(monkeypatch):
    async def fake_fetch_all():
        return [
            make_job("Software Engineer"),
            make_job("Junior QA Engineer"),
            make_job("Senior Developer"),
            make_job("Junior Dealer"),
        ]

    monkeypatch.setattr(jobs, "fetch_all", fake_fetch_all)

    result = asyncio.run(jobs.get_relevant_jobs())

    assert [job["title"] for job in result] == [
        "Junior QA Engineer",
        "Software Engineer",
    ]