import os
from datetime import datetime, time

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiNortheasternIlUniversitySpider(CityScrapersSpider):
    name = "chi_northeastern_il_university"
    agency = "Northeastern Illinois University"
    timezone = "America/Chicago"
    # start_urls = ["https://www.neiu.edu/about/board-of-trustees/calendar-of-meetings", "https://www.neiu.edu/about/board-of-trustees/board-meeting-materials",]
    start_urls = [
        f"file://{os.getcwd()}/tests/files/chi_northeastern_il_university_calendar.html"
    ]

    title_regex = "<li>.*?(?P<title>(Academic|Audit|Executive|Finance|Ad\\ hoc).*?(Committee)).*?<\\/li>"
    desc_regex = "<li>.*?(?P<title>(Academic|Audit|Executive|Board|Finance|Special|Ad\\ hoc|All).*?((Committee.*Meeting)|Committee|Meeting)).*?<\\/li>"

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        for annum in response.css("section.page-content ul"):
            year_str = annum.xpath("preceding-sibling::h2[1]").re_first(
                "(?P<year>\\d{4}) Board Meetings"
            )

            for item in annum.css("li"):
                meeting = Meeting(
                    classification=self._parse_classification(item),
                    title=self._parse_title(item),
                    description=self._parse_description(item),
                    start=self._parse_start(item, year_str),
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item, year_str),
                    links=self._parse_links(item),
                    source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_classification(self, item):
        if "Meeting" in item.get():
            return BOARD
        else:
            return COMMITTEE

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        if "Meeting" in item.get():
            return "Board of Trustees"
        else:
            return item.re_first(self.title_regex).replace("\xa0", " ")

    def _parse_description(self, item):
        return item.re_first(self.desc_regex).replace("\xa0", " ")

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object."""
        date_str = item.re(".*day(,)? (?P<date>.*?\\d{1,2}).*")[-1]
        date = datetime.strptime(f"{year} {date_str}", "%Y %B %d")
        if "Meeting" in item.get():
            return datetime.combine(date, time(13))
        else:
            return datetime.combine(date, time(8, 30))

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item, year):
        """Parse or generate location."""
        if year == "2018" and item.re_first("Thursday, September 20\\*"):
            return {
                "address": "700 E. Oakwood Blvd., Chicago, IL, 60653",
                "name": "Carruthers Center for Inner City Studies",
            }
        elif item.re(".*\\d{1,2}(<strong>)?\\*{2}"):
            return {
                "address": "700 E. Oakwood Blvd., Chicago, IL, 60653",
                "name": "Jacob H. Carruthers Center",
            }
        elif item.re(".*\\d{1,2}(<strong>)?\\*(?!\\*)"):
            return {
                "address": "3390 North Avondale Ave., Chicago, IL, 60618",
                "name": "El Centro",
            }
        else:
            return {
                "address": "5500 North St. Louis Ave., Chicago, IL., 60625",
                "name": "Northeastern Illinois University",
            }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
