# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from PIL import Image
from io import BytesIO
from os import getenv
import uuid
import sys
import tensorflow as tf
import numpy as np
import rats_detector

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ["audio/vnd.wav"]

app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

# Load the model
# The model was copied to this location when the container was built; see ../Dockerfile
#model_path = "/app/rats/frozen_inference_graph.pb"
#detection_graph = rats_detector.load_model(model_path)

# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    return_values = {"audio_bytes": None}
    try:
        # Attempt to load the body
        return_values["audio_bytes"] = BytesIO(request.data)
    except:
        log.log_error("Unable to load the request data")  # Log to Application Insights
    return return_values


# POST, async API endpoint example
@ai4e_service.api_sync_func(
    api_path="/detect",
    methods=["POST"],
    request_processing_function=process_request_data,  # This is the data process function that you created above.
    maximum_concurrent_requests=5,  # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types=ACCEPTED_CONTENT_TYPES,
    content_max_length=10000,  # In bytes
    trace_name="post:detect",
)
def detect(*args, **kwargs):
    print("runserver.py: detect() called, generating detections...")
    audio_bytes = kwargs.get("audio_bytes")

    image = rats_detector.open_audio(audio_bytes)

    X = tf.keras.preprocessing.image.img_to_array(image)
    X = np.expand_dims(X, axis=0)

    print("Get Model!")
    model = tf.keras.applications.inception_v3.InceptionV3()

    preds = model.predict(X)

    print("runserver.py: detect() finished.")

    scores = []
    for outer in tf.keras.applications.inception_v3.decode_predictions(preds):
        for _, cls, score in outer:
            scores.append((cls, str(score)))

    return {"predictions": scores}


if __name__ == "__main__":
    app.run()
