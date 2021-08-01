import logging
from utils.functions import download_file, join

LOG = logging.getLogger(__name__)


class PokemonDB:
    URL = "https://pokemondb.net/pokedex"
    IMG_BASE_URL = "https://img.pokemondb.net/artwork/{pokemon}.jpg"

    def __init__(self, config):
        self.config = config

    def scrape(self):
        dex = self.config.get("dex")
        with open(dex) as stream:
            next(stream)
            for line in stream:
                line = line.strip()
                img_url = self.IMG_BASE_URL.format(pokemon=line)
                download_file(img_url, join(self.config.get("out_dir"), line))
                LOG.info("Successfully downloaded: %s", line)
