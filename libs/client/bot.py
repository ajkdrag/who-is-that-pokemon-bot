import logging
import time
import json
import requests
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from selenium import webdriver
from libs.preprocessors.silhouette import Silhouette

LOG = logging.getLogger(__name__)


class Bot:
    def __init__(self, config):
        self.config = config

    def _get_labels(self):
        dex_file = self.config.get("dex")
        with open(dex_file) as stream:
            stream.readline()  # skip header
            dex_data = stream.readlines()
        return sorted(dex_data)

    def setup(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--remote-debugging-port=9222")
        self.options.add_argument("--disable-dev-shm-using")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-infobars")
        self.dex_data = self._get_labels()

    def start(self):
        browser = webdriver.Chrome(
            self.config.get("chromedriver"), options=self.options
        )
        browser.get(self.config.get("bot_url"))
        selected_gens = browser.find_elements_by_css_selector(".genSelect.selected")
        for gen in selected_gens:
            if gen.get_attribute("id") != "gen1":
                gen.click()

        give_ans = browser.find_element_by_id("giveAnswer")
        give_ans.click()
        time.sleep(4)
        for _ in range(10):
            img_bbox = browser.find_element_by_id("shadowImage")
            ss = img_bbox.screenshot_as_png
            img = Image.open(BytesIO(ss))
            img = img.resize((128, 128))
            silhouette = Silhouette(config=None)
            img_silhouette = 255 - silhouette.remove_background(
                image=np.asarray(img, dtype=np.uint8),
                thresh=100,
                base=255,
                scale_factor=1,
            )
            img_silhouette = cv2.cvtColor(img_silhouette, cv2.COLOR_GRAY2BGR)
            img_silhouette = np.expand_dims(img_silhouette / 255, axis=0)
            data = json.dumps({"instances": img_silhouette.tolist()})
            url = "http://localhost:8501/v1/models/Xception:predict"
            resp = requests.post(url, data=data)
            predictions = resp.json()["predictions"][0]
            best_prediction = self.dex_data[np.argmax(predictions)].strip()
            ans_box = browser.find_element_by_id("pokemonGuess")
            ans_box.send_keys(best_prediction)
            time.sleep(4)
