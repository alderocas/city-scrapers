from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_northeastern_il_university import (
    ChiNortheasternIlUniversitySpider,
)

test_calendar_response = file_response(
    join(dirname(__file__), "files", "chi_northeastern_il_university_calendar.html"),
    url="https://www.neiu.edu/about/board-of-trustees/calendar-of-meetings",
)

spider = ChiNortheasternIlUniversitySpider()

freezer = freeze_time("2020-11-09")
freezer.start()

parsed_calendar_items = [item for item in spider.parse(test_calendar_response)]

freezer.stop()


def test_title():
    assert (
        parsed_calendar_items[0]["title"]
        == "Academic/Student Affairs and Enrollment Management Committee"
    )
    assert parsed_calendar_items[1]["title"] == "Audit Committee"
    assert parsed_calendar_items[2]["title"] == "Executive Committee"
    assert parsed_calendar_items[41]["title"] == "Ad hoc Committee"
    assert parsed_calendar_items[52]["title"] == "Finance Committee"
    assert parsed_calendar_items[-1]["title"] == "Board of Trustees"
    assert (
        parsed_calendar_items[7]["title"] == "Finance, Buildings and Grounds Committee"
    )
    assert (
        parsed_calendar_items[49]["title"] == "Academic and Student Affairs Committee"
    )


def test_description():
    assert parsed_calendar_items[1]["description"] == "Audit Committee"
    assert parsed_calendar_items[2]["description"] == "Executive Committee"
    assert parsed_calendar_items[3]["description"] == "Board Meeting"
    assert parsed_calendar_items[41]["description"] == "Ad hoc Committee"
    assert parsed_calendar_items[48]["description"] == "Special Board Meeting"
    assert parsed_calendar_items[52]["description"] == "Finance Committee"
    assert (
        parsed_calendar_items[0]["description"]
        == "Academic/Student Affairs and Enrollment Management Committee"
    )
    assert (
        parsed_calendar_items[7]["description"]
        == "Finance, Buildings and Grounds Committee"
    )
    assert (
        parsed_calendar_items[49]["description"]
        == "Academic and Student Affairs Committee"
    )
    assert (
        parsed_calendar_items[-1]["description"]
        == "All Committee Meetings followed by Board Meeting"
    )


def test_start():
    assert parsed_calendar_items[0]["start"] == datetime(2020, 1, 16, 8, 30)
    assert parsed_calendar_items[-1]["start"] == datetime(2018, 11, 15, 13, 00)


def test_id():
    assert (
        parsed_calendar_items[0]["id"]
        == "chi_northeastern_il_university/202001160830/x/academic_student_affairs_and_enrollment_management_committee"  # noqa
    )
    assert (
        parsed_calendar_items[1]["id"]
        == "chi_northeastern_il_university/202001270830/x/audit_committee"
    )
    assert (
        parsed_calendar_items[2]["id"]
        == "chi_northeastern_il_university/202002130830/x/executive_committee"
    )
    assert (
        parsed_calendar_items[7]["id"]
        == "chi_northeastern_il_university/202003230830/x/finance_buildings_and_grounds_committee"  # noqa
    )
    assert (
        parsed_calendar_items[41]["id"]
        == "chi_northeastern_il_university/201910170830/x/ad_hoc_committee"
    )
    assert (
        parsed_calendar_items[49]["id"]
        == "chi_northeastern_il_university/201801250830/x/academic_and_student_affairs_committee"  # noqa
    )
    assert (
        parsed_calendar_items[52]["id"]
        == "chi_northeastern_il_university/201803290830/x/finance_committee"
    )
    assert (
        parsed_calendar_items[-1]["id"]
        == "chi_northeastern_il_university/201811151300/x/board_of_trustees"
    )


def test_status():
    assert parsed_calendar_items[0]["status"] == "passed"
    assert parsed_calendar_items[23]["status"] == "tentative"


def test_location():
    assert parsed_calendar_items[0]["location"] == {
        "name": "Northeastern Illinois University",
        "address": "5500 North St. Louis Ave., Chicago, IL 60625",
    }
    assert parsed_calendar_items[8]["location"] == {
        "name": "El Centro",
        "address": "3390 North Avondale Ave., Chicago, IL 60618",
    }
    assert parsed_calendar_items[45]["location"] == {
        "name": "Jacob H. Carruthers Center",
        "address": "700 E. Oakwood Blvd., Chicago, IL 60653",
    }
    assert parsed_calendar_items[58]["location"] == {
        "name": "Carruthers Center for Inner City Studies",
        "address": "700 E. Oakwood Blvd., Chicago, IL 60653",
    }


def test_classification():
    assert parsed_calendar_items[0]["classification"] == COMMITTEE
    assert parsed_calendar_items[-1]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_calendar_items)
class TestParametrized:
    def test_end(self, item):
        assert item["end"] is None

    def test_time_notes(self, item):
        assert item["time_notes"] == "See agenda for meeting time"

    def test_all_day(self, item):
        assert item["all_day"] is False

    def test_source(self, item):
        assert (
            item["source"]
            == "https://www.neiu.edu/about/board-of-trustees/calendar-of-meetings"
        )
