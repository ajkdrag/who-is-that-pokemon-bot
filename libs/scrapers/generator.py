"""Base script to generate all pokemon names for a given generation"""


class InvalidGenError(Exception):
    pass


class PokemonNamesGenerator:
    URL = "https://www.serebii.net/pokemon/gen{gen_num}pokemon.shtml"
    VALID_GENS = ["1"]
    SPECIAL_CHARACTERS_MAP = {
        "♀": "-f",
        "♂": "-m",
    }

    def __init__(self, gen, out_path):
        self.gen = gen
        self.out_path = out_path
        self.validate()

    def validate(self):
        if self.gen is None or self.gen not in self.VALID_GENS:
            raise InvalidGenError(f"Invalid Pokemon Generation: {self.gen}")
        LOG.info("Successfully validated params: %s", self.__dict__)

    def parse(self):
        url = self.URL.format(gen_num=gen)
        pokedex = pd.read_html(url, header=1)[0]
        pattern = "|".join(self.SPECIAL_CHARACTERS_MAP.keys())
        repl = lambda match: self.SPECIAL_CHARACTERS_MAP.get(match.group(0))
        pokemon_names = pokedex.loc[:, "Name"].str.replace(pattern, repl, regex=True)
        LOG.info("Parsed table from url: %s", url)
        pokemon_names.to_csv(self.out_path, index=False)
        LOG.info("Successfully written names to: %s", self.out_path)


if __name__ == "__main__":
    import pandas as pd
    import argparse
    import logging

    logging.basicConfig(level=logging.INFO)

    LOG = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g", "--gen", type=str, required=True, help="the generation #."
    )

    parser.add_argument("-o", "--output", type=str, required=True, help="output file.")
    args = parser.parse_args()
    gen = args.gen
    out = args.output
    nameGenerator = PokemonNamesGenerator(gen=gen, out_path=out)
    nameGenerator.parse()
