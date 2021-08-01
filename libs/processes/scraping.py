import logging
from libs.processes import BaseProcess
from utils.functions import get_class_based_on_class_type
from utils.constants.config_contract import SCRAPING_TYPE_MAP

LOG = logging.getLogger(__name__)


class ScrapingProcess(BaseProcess):
    _list_scrapers = []

    def _add_scraper(self, new_scraper):
        self._list_scrapers.append(new_scraper)

    def _compile(self):
        scrapers_to_use = self.config.get("scrapers")
        for scraping_type in scrapers_to_use:
            scraper = get_class_based_on_class_type(scraping_type, SCRAPING_TYPE_MAP)(
                self.config.get("extraArgs")
            )
            self._add_scraper(scraper)

    def _execute(self):
        for scraper in self._list_scrapers:
            scraper.scrape()
