import logging
import cv2 as cv
from utils.functions import iter_dir, join, make_dirs

LOG = logging.getLogger(__name__)


class Silhouette:
    def __init__(self, config):
        self.config = config

    def get_holes(self, image, thresh, base):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        im_bw = cv.threshold(gray, thresh, 255, cv.THRESH_BINARY)[1]
        im_bw_inv = cv.bitwise_not(im_bw)

        contour, _ = cv.findContours(im_bw_inv, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contour:
            cv.drawContours(im_bw_inv, [cnt], 0, base, -1)

        nt = cv.bitwise_not(im_bw)
        im_bw_inv = cv.bitwise_or(im_bw_inv, nt)
        return im_bw_inv

    def remove_background(
        self, image, thresh, base=255, scale_factor=0.45, kernel_range=range(1, 2), border=None
    ):

        border = border or kernel_range[-1]

        holes = self.get_holes(image, thresh, base)
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
        for file in iter_dir(self.config.get("in_dir")):
            relative_path = file.parent.relative_to(self.config.get("in_dir"))
            out_dir = join(self.config.get("out_dir"), relative_path)
            LOG.info("Reading :%s", str(file))
            img = cv.imread(str(file))
            silhouette = 255 - self.remove_background(image=img, thresh=230)
            make_dirs(out_dir)
            out_path = join(out_dir, file.name)
            cv.imwrite(out_path, silhouette)
            LOG.info("Successfully extracted silhouette to: %s", out_path) 
