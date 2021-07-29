from libs.processes import BaseProcess


class ScrapingProcess(BaseProcess):
    _list_scrapers = []

    def _add_scraper(self, new_scraper):
        self._list_scrapers.append(new_scraper)

    def _execute(self):
        pass
