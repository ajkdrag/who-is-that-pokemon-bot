import numpy as np
import tensorflow as tf
import logging

from os.path import join
from PIL import Image
from tensorflow.python.framework import tensor_util
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_log_pb2

LOG = logging.getLogger(__name__)


def get_prepared_img(img_path):
    img = Image.open(img_path).convert("RGB")
    np_img = np.asarray(img.resize((128, 128)), dtype=np.uint8)
    return np.expand_dims(np_img / 255.0, axis=0)


def write_warmup_records(
    model_name, img_path, out_path, signature="serving_default", num_recs=10
):
    with tf.io.TFRecordWriter(join(out_path, "tf_serving_warmup_requests")) as writer:
        predict_request = predict_pb2.PredictRequest()
        predict_request.model_spec.name = model_name
        predict_request.model_spec.signature_name = signature
        LOG.info(
            "Preparing request for model: %s , with signature: %s",
            model_name,
            signature,
        )

        np_img = get_prepared_img(img_path)
        LOG.info("Warmup data shape: %s", np_img.shape)

        predict_request.inputs["xception_input"].CopyFrom(
            tensor_util.make_tensor_proto(np_img.tolist())
        )

        log = prediction_log_pb2.PredictionLog(
            predict_log=prediction_log_pb2.PredictLog(request=predict_request)
        )

        LOG.info("Writing warmup records...")
        for _ in range(num_recs):
            writer.write(log.SerializeToString())

        LOG.info("Successfully written %s warmup record(s)", num_recs)


if __name__ == "__main__":
    logging.basicConfig()
    LOG.setLevel(logging.INFO)
    write_warmup_records("Xception", "tests/test.png", "tests")
