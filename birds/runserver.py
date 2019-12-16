# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from io import BytesIO
import tensorflow as tf
import pandas as pd
import numpy as np
import birds_detector

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ["audio/vnd.wav"]

app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

# Load the model and species dataframe
# The model was copied to this location when the container was built; see ../Dockerfile
MODEL = tf.keras.models.load_model("/app/birds/model.h5")
SPECIES = pd.read_csv("/app/birds/species.csv")

# Define a function for processing request data, if appliciable. This function
# loads data or files into a dictionary for access in your API function. We
# pass this function as a parameter to your API setup.
def process_request_data(req):
    """ Wrap input data into BytesIO object
    """
    try:
        return_values = {"audio_io": None}
        if req.data != b"":
            return_values["audio_io"] = BytesIO(req.data)
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
    """ Return predictions
    """
    print("runserver.py: detect() called")
    audio_io = kwargs.get("audio_io")

    print("runserver.py: detect() checking inputs")
    # Just return error if no data was posted
    if not audio_io:
        return {"error": "No data was given with post?"}

    # Make sure we can load the data given to us
    print("runserver.py: detect() load samples")
    try:
        samples, sample_rate = birds_detector.load_samples(audio_io)
    except:
        return {"error": "I could not load the audio"}

    # Check the duration is between 5 and 20 seconds
    duration = birds_detector.audio_duration(samples, sample_rate)
    if duration < 5 or duration > 20:
        return {"error": "Audio duration should be between 5 and 20 seconds long"}

    # Check for single- or dual-channel
    if len(samples.shape) == 2 and samples.shape[0] > 2:
        return {"error": "Audio has more than two channels, ignoring"}

    # libsndfile, reads dual-channel files as (N, 2) but librosa
    # requires (2, N)
    if len(samples.shape) == 2:
        samples = birds_detector.to_mono(samples)

    print("runserver.py: detect(), opening audio")
    images = birds_detector.open_audio(samples, sample_rate, duration)

    print("runserver.py: detect(), predict")
    preds = MODEL.predict(images)

    print("runserver.py: detect(), generate scores")
    scores = [[None] * SPECIES.shape[0] for _ in range(preds.shape[0])]
    for p_idx, pred in enumerate(preds):
        for idx, (cls, score) in enumerate(zip(SPECIES["species"].values, pred)):
            scores[p_idx][idx] = f"{cls}: {score:.5f}"

    print("runserver.py: detect(), return predictions")
    return {"predictions": scores}


if __name__ == "__main__":
    app.run()
