import logging
import json
import requests
import numpy as np
from PIL import Image

LOG = logging.getLogger(__name__)
LABEL_RENAME_MAP = {"mr-mime": "mr. mime"}


def get_prepared_img(img_path):
    img = Image.open(img_path).convert("RGB")
    resized = np.array(img.resize((128, 128))).astype(np.uint8)
    return np.expand_dims(resized / 255.0, axis=0)


def get_prediction(url, prepared_img):
    data = json.dumps({"instances": prepared_img.tolist()})
    resp = requests.post(url, data=data)
    predictions = resp.json()["predictions"][0]
    return np.argmax(predictions)


def get_labels(dex_file):
    with open(dex_file) as stream:
        stream.readline()  # skip header
        dex_data = [
            LABEL_RENAME_MAP.get(label.strip(), label.strip())
            for label in stream.readlines()
        ]
    return sorted(dex_data)


if __name__ == "__main__":
    logging.basicConfig()
    LOG.setLevel(logging.INFO)

    url = "http://localhost:8501/v1/models/Xception:predict"
    dex_file_path = "data/dex.csv"
    test_img_path = (
        "data/images/preprocessed/mr-mime/ff8c7ee37f754382b82793bb9a8870c8.jpg"
    )

    prepared_img = get_prepared_img(test_img_path)
    prediction = get_prediction(url, prepared_img)
    category_index = get_labels(dex_file_path)
    print(category_index[prediction])
