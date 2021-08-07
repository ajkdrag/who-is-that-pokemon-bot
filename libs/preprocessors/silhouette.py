import logging
import cv2 as cv
from utils.functions import scrape_dir, join

LOG = logging.getLogger(__name__)


class Silhouette:
    def __init__(self, config):
        self.config = config

    def get_holes(self, image, thresh):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        im_bw = cv.threshold(gray, thresh, 255, cv.THRESH_BINARY)[1]
        im_bw_inv = cv.bitwise_not(im_bw)

        contour, _ = cv.findContours(im_bw_inv, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contour:
            cv.drawContours(im_bw_inv, [cnt], 0, 255, -1)

        nt = cv.bitwise_not(im_bw)
        im_bw_inv = cv.bitwise_or(im_bw_inv, nt)
        return im_bw_inv

    def remove_background(
        self, image, thresh, scale_factor=0.45, kernel_range=range(1, 2), border=None
    ):

        border = border or kernel_range[-1]

        holes = self.get_holes(image, thresh)
        small = cv.resize(holes, None, fx=scale_factor, fy=scale_factor)
        bordered = cv.copyMakeBorder(
            small, border, border, border, border, cv.BORDER_CONSTANT
        )

        for i in kernel_range:
            kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2 * i + 1, 2 * i + 1))
            bordered = cv.morphologyEx(bordered, cv.MORPH_CLOSE, kernel)

        unbordered = bordered[border:-border, border:-border]
        mask = cv.resize(unbordered, (image.shape[1], image.shape[0]))
        return mask

    def preprocess(self):
        for filename in scrape_dir(self.config.get("in_dir")):
            filepath = join(self.config.get("in_dir"), filename)
            outpath = join(self.config.get("out_dir"), filename)
            img = cv.imread(filepath)
            silhouette = 255 - self.remove_background(img, 230)
            cv.imwrite(outpath, silhouette)
            LOG.info("Successfully extracted silhouette for: %s", filename)
