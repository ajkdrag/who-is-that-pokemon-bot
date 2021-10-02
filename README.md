# Who's-That-Pokemon-Bot

Bot for the online game: [Who's that pokemon](https://gearoid.me/pokemon/)

## Prerequisites
* Docker
* Chromedriver
* :heart: for Pokemons

Once Docker is setup, pull the latest **Tensorflow serving** docker image.
```bash
docker pull tensorflow/serving
```
Download Chromedriver for your chrome/chromium version from: [ChromeDriver](https://chromedriver.chromium.org/downloads)


## Usage

Clone/Download this repo 
```bash
git clone https://github.com/ajkdrag/Who-Is-That-Pokemon-Bot.git
```
Go to the root dir and create a virtual env with the **requirements.txt** file.

```bash
cd Who-Is-That-Pokemon-Bot
conda create --name wtp-bot --file requirements.txt
conda activate wtp-bot
```
Edit the **inferencing.cfg.yaml** file in **configs** dir to point to the downloaded chromedriver.
```bash
├── hyps.yaml
├── launcher.cfg.yaml
└── processes
    ├── inferencing.cfg.yaml
    ├── pipeline.cfg.yaml
    ├── preprocessing.cfg.yaml
    ├── scraping.cfg.yaml
    └── training.cfg.yaml
```

Run the launcher script
```bash
python launcher.py --config configs/launcher.cfg.yaml
```
This launches a new chrome window and opens [Who's that pokemon](https://gearoid.me/pokemon/), followed by guessing (predicting :sparkles: ) the pokemons. At the end a stats file is generated under the **export** dir.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[Standard MIT](https://choosealicense.com/licenses/mit/)

