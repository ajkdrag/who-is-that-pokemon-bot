import uuid
import logging
from utils.functions import make_dirs, download_file, join

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
                out_dir = join(self.config.get("out_dir"), line)
                make_dirs(out_dir)
                download_file(img_url, join(out_dir, f"{uuid.uuid4().hex}.jpg"))
                LOG.info("Successfully downloaded: %s", line)
