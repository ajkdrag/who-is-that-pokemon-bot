import tensorflow as tf
import matplotlib.pyplot as plt
from pathlib import Path
from tensorflow.keras.layers import (
    Dense,
    Flatten,
    Dropout,
    Softmax,
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.xception import Xception
from utils.general.file_io import read_all_yaml_data


class Train:
    def __init__(self, config):
        self.config = config

    def setup(self):
        self._get_hyps()
        self._prepare_train_and_val_data()

    def run(self):
        self._first_stage_train()
        self._second_stage_train()

    def _get_hyps(self):
        hyp_path = self.config.get("hyps")
        with open(hyp_path) as stream:
            self.hyps = read_all_yaml_data(stream)

    def _prepare_train_and_val_data(self):
        width = self.hyps.get("width")
        height = self.hyps.get("height")
        batch_size = self.hyps.get("batch-size")
        input_dir = self.config.get("input_dir")
        self.img_sz = (height, width)

        train_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)
        val_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

        self.train_data = train_datagen.flow_from_directory(
            input_dir,
            target_size=self.img_sz,
            batch_size=batch_size,
            shuffle=True,
            subset="training",
        )

        self.val_data = val_datagen.flow_from_directory(
            input_dir,
            target_size=self.img_sz,
            batch_size=batch_size,
            shuffle=False,
            subset="validation",
        )

    def _get_backbone(self):
        backbone = Xception(
            include_top=False, input_shape=(*self.img_sz, 3), pooling="avg"
        )
        return backbone

    def _get_model(self, backbone):
        model = Sequential()
        model.add(backbone)
        model.add(Flatten())
        model.add(Dense(512))
        model.add(Dropout(0.2))
        model.add(Dense(151))
        model.add(Softmax())
        return model

    def _save_metrics(self, history):
        acc = history.history["accuracy"]

        val_acc = history.history["val_accuracy"]

        loss = history.history["loss"]
        val_loss = history.history["val_loss"]

        epochs_range = range(self.early_stopping.stopped_epoch)

        plt.figure(figsize=(20, 8))
        plt.subplot(1, 2, 1)
        plt.plot(epochs_range, acc, label="Training Accuracy")
        plt.plot(epochs_range, val_acc, label="Validation Accuracy")
        plt.legend(loc="lower right")
        plt.title("Training and Validation accuracy")

        plt.subplot(1, 2, 2)
        plt.plot(epochs_range, loss, label="Training Loss")
        plt.plot(epochs_range, val_loss, label="Validation Loss")
        plt.legend(loc="upper right")
        plt.title("Training and Validation loss")

        save_path = Path(self.config.get("model_dir"), "plots.png")
        plt.savefig(str(save_path), bbox_inches="tight")

    def _first_stage_train(self):
        backbone = self._get_backbone()
        backbone.trainable = False
        self.model = self._get_model(backbone)
        for layer in self.model.layers:
            if isinstance(layer, tf.keras.layers.BatchNormalization):
                layer._per_input_updates = {}

        self.model.compile(
            loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
        )
        self.model.fit(
            self.train_data,
            epochs=self.hyps.get("epochs"),
            validation_data=self.val_data,
        )
        saved_model_dir = Path(self.config.get("model_dir"), "saved_model_stg_1")
        saved_model_dir.mkdir(parents=True, exist_ok=True)
        self.model.save(str(saved_model_dir))

    def _second_stage_train(self):
        self.early_stopping = EarlyStopping(patience=5)
        callbacks = [self.early_stopping]
        self.model.trainable = True
        self.model.compile(
            loss="categorical_crossentropy", optimizer=Adam(1e-5), metrics=["accuracy"]
        )
        history = self.model.fit(
            self.train_data,
            epochs=self.hyps.get("epochs") * 3,
            validation_data=self.val_data,
            callbacks=callbacks,
        )
        self._save_metrics(history)

        saved_model_dir = Path(self.config.get("model_dir"), "saved_model_stg_2")
        saved_model_dir.mkdir(parents=True, exist_ok=True)
        self.model.save(str(saved_model_dir))
