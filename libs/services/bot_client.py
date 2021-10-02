import logging
import time
import json
import requests
import numpy as np
import pandas as pd
import cv2
from os.path import join
from datetime import datetime
from io import BytesIO
from PIL import Image
from selenium import webdriver
from libs.preprocessors.silhouette import Silhouette

LOG = logging.getLogger(__name__)


class Bot:
    LABEL_RENAME_MAP = {
        "mr-mime": "mr. mime",
        "farfetchd": "farfetch'd",
        "nidoran-f": "nidoran",
        "nidoran-m": "nidoran",
    }

    def __init__(self, config):
        self.config = config

    def _get_labels(self):
        dex_file = self.config.get("dex")
        with open(dex_file) as stream:
            stream.readline()  # skip header
            dex_data = [
                self.LABEL_RENAME_MAP.get(label.strip(), label.strip())
                for label in stream.readlines()
            ]
        return sorted(dex_data)

    def setup(self):
        self.options = webdriver.ChromeOptions()
        # self.options.add_experimental_option("detach", True)
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-setuid-sandbox")
        self.options.add_argument("--remote-debugging-port=9222")
        self.options.add_argument("--disable-dev-shm-using")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-infobars")
        self.dex_data = self._get_labels()
        self.model_nm = self.config.get("model_name")
        self.url = f"http://localhost:8501/v1/models/{self.model_nm}:predict"
        self.k = self.config.get("num_attempts", 3)
        self.stat_rows = []

    def _dump_stats(self, browser):
        streak = browser.find_element_by_class_name("currentCountText").get_attribute(
            "textContent"
        )
        avg_time = browser.find_element_by_class_name("averageTimeText").get_attribute(
            "textContent"
        )

        stats = pd.DataFrame(
            self.stat_rows,
            columns=["Predictions", "Actual", "Num-retries", "Elapsed(ms)"],
        )
        stats_filename = join(
            self.config.get("export"), f"stats_{datetime.now():%Y-%m-%d_%H-%M-%S}.csv"
        )
        stats.to_csv(
            stats_filename,
            index_label="Index",
        )
        LOG.info(
            "Streak: %s\nAvg. Time: %s\nStats saved to: %s\n",
            streak,
            avg_time,
            stats_filename,
        )

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
        for _ in range(self.config.get("max_inferences")):
            img_bbox = browser.find_element_by_id("shadowImage")
            ss = img_bbox.screenshot_as_png
            img = Image.open(BytesIO(ss))
            np_img = np.array(img.resize((128, 128))).astype(np.uint8)
            silhouette = Silhouette(config=None)
            img_silhouette = 255 - silhouette.remove_background(
                image=np_img,
                thresh=100,
                base=255,
                scale_factor=1,
            )
            img_silhouette = cv2.cvtColor(img_silhouette, cv2.COLOR_GRAY2BGR)
            img_silhouette = np.expand_dims(img_silhouette / 255.0, axis=0)
            data = json.dumps({"instances": img_silhouette.tolist()})
            start = time.time()
            resp = requests.post(self.url, data=data)
            predictions = resp.json()["predictions"][0]
            elapsed = (time.time() - start) * 1000
            top_k_predictions = [
                self.dex_data[pred]
                for pred in sorted(
                    range(len(predictions)),
                    key=lambda idx: predictions[idx],
                    reverse=True,
                )[: self.k]
            ]
            ans_box = browser.find_element_by_id("pokemonGuess")
            string_predictions = ", ".join(top_k_predictions)
            correct_ans = ""
            retries = -1
            for k, pred in enumerate(top_k_predictions):
                ans_box.send_keys(pred)
                if ans_box.get_attribute("class") == "correct disabled":
                    retries = k
                    correct_ans = pred
                    break
                else:
                    ans_box.clear()
                    LOG.info("Mispredicted with: %s Trying next best prediction", pred)
            else:
                LOG.info("Giving up...")
                give_ans.click()
                correct_ans = ans_box.get_attribute("value")
                LOG.info("Correct ans: %s", correct_ans)
            row = [string_predictions, correct_ans, retries, elapsed]
            self.stat_rows.append(row)
            time.sleep(4)

        self._dump_stats(browser)
        browser.quit()
