import json

from playwright.sync_api import sync_playwright, Page, ElementHandle
from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


# informaconnect.com - Agenda - TMRE 2024 Day 1: Tuesday, October 8 | TMRE: The Market Research Event
# https://informaconnect.com/tmre/agenda/2/?searchInput=&stream=1

# informaconnect.com - Agenda - TMRE 2024 Day 2: Wednesday, October 9 | TMRE: The Market Research Event
# TARGET_URL = "https://informaconnect.com/tmre/agenda/3/?searchInput=&stream=1"


# SCRAPE_TARGETS = [
#     {
#         url: "https://informaconnect.com/tmre/agenda/2/?searchInput=&stream=1",
#         scraper: 
#     }
# ]



class Scrape(ABC):
    @abstractmethod
    def doScrape(self, page: Page) -> List[str]:
        pass


def try_scrape_text(element: ElementHandle, selector: str) -> str:
    print(f"Scraping text from {selector}... ", end="")
    result = "NOT_FOUND"
    try:
        result = element.query_selector(selector).inner_text()
    except:
        pass
    print(result)
    return result

def try_scrape_attribute(element: ElementHandle, selector: str, attribute: str) -> str:
    print(f"Scraping attribute {attribute} from {selector}... ", end="")
    result = "NOT_FOUND"
    try:
        result = element.query_selector(selector).get_attribute(attribute)
    except:
        pass
    print(result)
    return result



class SessionSpeakerData(BaseModel):
    """ Data model for a session speaker """
    name: str = "SPEAKER_NAME"
    title: str = "SPEAKER_TITLE"
    company: str = "SPEAKER_COMPANY"
    profileUrl: str = "SPEAKER_PROFILE_URL"
    bio: str = "SPEAKER_BIO"

class SessionData(BaseModel):
    """ Data model for a session """
    session_type: str = "SESSION_TYPE"
    title: str = "SESSION_TITLE"
    description: str = "SESSION_DESCRIPTION"
    track: str = "SESSION_TRACK"
    time: str = "SESSION_TIME"
    speakers: List[SessionSpeakerData] = []


class SessionDataScraper():
    """ A scraper for session data """

    def __init__(self, session_data: SessionData):
        self._session_data = session_data


    def doScrape(self, session_info_element: ElementHandle) -> SessionData:
        self._scrape_session_text_info(session_info_element)
        self._scrape_session_speakers(session_info_element)
        return self._session_data


    def _scrape_session_text_info(self, element: ElementHandle) -> None:
        self._session_data.session_type = try_scrape_text(element, ".c-session-info__body-format")
        self._session_data.title = try_scrape_text(element, ".c-session-info__body-title")
        self._session_data.description = try_scrape_text(element, ".c-session-info__body-description")
        self._session_data.track = try_scrape_text(element, ".c-session-info__body-stream")
        self._session_data.time = try_scrape_text(element, ".c-session-info__body-time")


    def _scrape_session_speakers(self, element: ElementHandle) -> None:
        speaker_elements = element.query_selector_all(".session-speakers__item")
        self._session_data.speakers = []
        for speaker_element in speaker_elements:
            speaker = SessionSpeakerData()
            speaker.name = try_scrape_text(speaker_element, ".session-speakers__item-name")
            speaker.title = try_scrape_text(speaker_element, ".session-speakers__item-job")
            speaker.company = try_scrape_text(speaker_element, ".session-speakers__item-company")
            speaker.profileUrl = f'https://informaconnect.com{try_scrape_attribute(speaker_element, ".session-speakers__item-link", "href")}'
            speaker.bio = "SPEAKER_BIO"
            self._session_data.speakers.append(speaker)


class AgendaScraper(Scrape):

    def __init__(self, browser):
        self.browser = browser
        self._all_session_data = []

    def doScrape(self, url: str) -> List[SessionData]:
        page = self.browser.new_page()
        page.goto(url)

        # wait for the page to load
        page.wait_for_selector(".c-agenda-stream-item-session")
        elements = page.query_selector_all(".c-agenda-stream-item-session")

        for element in elements:
            element.click()
            page.wait_for_selector(".c-session-info")
            session_info_element = page.query_selector(".c-session-info")
            session_data = SessionDataScraper(SessionData()).doScrape(page)
            # print(session_data.model_dump())

            self._all_session_data.append(session_data)

            page.query_selector(".c-session-info__header-close").click()
            page.wait_for_timeout(2000)


        for session_data in self._all_session_data:
            print(f"|")
            print(f"| Scraping speaker bios for session {session_data.title}...")
            for speaker in session_data.speakers:
            
                print(f"| Scraping speaker bio for {speaker.profileUrl}...")
                print(f"| ")
                page.goto(speaker.profileUrl)
                try:
                    page.wait_for_selector(".c-person-content-section__container")
                    speaker.bio = try_scrape_text(page, ".c-person-content-section__container")
                except:
                    print(f"| Speaker bio for {speaker.profileUrl} not found.")
                    speaker.bio = "BIO_NOT_FOUND"
                page.go_back()
                page.wait_for_timeout(1500)

        page.close()
        return self._all_session_data



# Example usage:
if __name__ == "__main__":
    aggregated_session_data: List[SessionData] = []

    day_one = "https://informaconnect.com/tmre/agenda/2/?searchInput=&stream=1"
    day_two = "https://informaconnect.com/tmre/agenda/3/?searchInput=&stream=1"


    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)

    for url in [day_one, day_two]:
        aggregated_session_data.extend(AgendaScraper(browser).doScrape(url))

    browser.close()
    playwright.stop()

    with open("session_data.json", "w") as file:
        file.write(json.dumps([session_data.dict() for session_data in aggregated_session_data], indent=2))



