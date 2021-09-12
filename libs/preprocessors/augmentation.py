import logging
import tensorflow as tf
from pathlib import Path
from tensorflow.keras.preprocessing.image import ImageDataGenerator


LOG = logging.getLogger(__name__)


class Augmentation:
    def __init__(self, config):
        self.config = config

    def _get_data_generator(self):
        aug_data_generator = ImageDataGenerator(
            rotation_range=20,
            rescale=1.0 / 255,
            width_shift_range=0.1,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            shear_range=0.1,
            fill_mode="constant",
            cval=255,
        )
        return aug_data_generator

    def preprocess(self):
        in_path = Path(self.config.get("processed_dir"))
        for subdir in in_path.iterdir():
            label = subdir.name
            LOG.info("Performing augmentation for class: %s", label)
            save_path = Path(self.config.get("augmented_dir"), label)
            save_path.mkdir(parents=True, exist_ok=True)
            aug_data_generator = self._get_data_generator()
            aug_data = aug_data_generator.flow_from_directory(
                str(in_path),
                classes=[label],
                target_size=(128, 128),
                batch_size=10,
                shuffle=True,
                class_mode="categorical",
                save_to_dir=str(save_path),
                save_prefix="aug",
            )
            for _ in range(self.config.get("num_aug_images")):
                next(aug_data)
