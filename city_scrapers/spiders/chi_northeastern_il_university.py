from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime


class ChiNortheasternIlUniversitySpider(CityScrapersSpider):
    name = "chi_northeastern_il_university"
    agency = "Northeastern Illinois University"
    timezone = "America/Chicago"
    #start_urls = ["https://www.neiu.edu/about/board-of-trustees/calendar-of-meetings", "https://www.neiu.edu/about/board-of-trustees/board-meeting-materials"]
    start_urls = ['tests/files/chi_northeastern_il_university_calendar.html', 'tests/files/chi_northeastern_il_university_meeting_materials.html']
    title_regex = '<li>.*?(?P<title>(Academic|Audit|Executive|Finance|Ad\\ hoc).*?(Committee)).*?<\\/li>'

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        for annum in response.css("section.page-content ul"):
            year_str = annum.xpath('preceding-sibling::h2[1]').re_first('(?P<year>\\d{4}) Board Meetings')

            for item in annum.css("li"):
                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=self._parse_classification(item),
                    start=self._parse_start(item, year_str),
                    end=self._parse_end(item),
                    all_day=self._parse_all_day(item),
                    time_notes=self._parse_time_notes(item),
                    location=self._parse_location(item),
                    links=self._parse_links(item),
                    source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        if 'Meeting' in item.get():
            return "Board of Trustees"
        else:
            return item.re_first(title_regex).replace('\xa0', ' ')

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date_str = item.re_first('.*day, (?P<date>.*?\d{1,2}).*')
        return datetime.parser(f"{year_str} {date_str}", "%Y %B %d")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
