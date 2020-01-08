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
MODEL_PASSERINES = tf.keras.models.load_model("/app/birds/model_passerines.h5")
MODEL_NONPASSERINES = tf.keras.models.load_model("/app/birds/model_nonpasserines.h5")
SPECIES_PASSERINES = pd.read_csv("/app/birds/species_passerines.csv")
SPECIES_NONPASSERINES = pd.read_csv("/app/birds/species_nonpasserines.csv")

# Define a function for processing request data, if applicable. This function
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


def process_audio(func_name, audio_io):
    """
    Check inputs and return spectrogram images
    
    Check that inputs are in correct format (single-channel,
    between 5-20 seconds), and convert to images
    
    Args:
        func_name (str): name of calling function (for printing)
        audio_io (bytes): 
    
    Returns:
        array of 299x299 images, each representing up to 
            5s of the original audio
    
    """
    print(f"runserver.py: {func_name}() checking inputs")
    # Just return error if no data was posted
    if not audio_io:
        return {"error": "No data was given with post?"}

    # Make sure we can load the data given to us
    print(f"runserver.py: {func_name}() loading samples")
    try:
        samples, sample_rate = birds_detector.load_samples(audio_io)
    except:
        return {"error": "I could not load the audio"}
    print(f"runserver.py: {func_name}() loaded samples at sample_rate {sample_rate}")
    
    # Check the duration is between 5 and 20 seconds
    duration = birds_detector.audio_duration(samples, sample_rate)
    if duration < 5 or duration > 20:
        return {"error": "Audio duration should be between 5 and 20 seconds long"}

    # Check for single- or dual-channel
    # if len(samples.shape) == 2 and samples.shape[1] > 2:
    #    return {"error": "Audio has more than two channels, ignoring"}
    if len(samples.shape) > 1:
        return {"error": "Audio has more than one channel, ignoring"}

    # Force to mono
    # if len(samples.shape) == 2:
    #    print(f"runserver.py: {func_name}() forcing audio to mono")
    #    samples = birds_detector.to_mono(samples)

    print(f"runserver.py: {func_name}(), opening audio as spectrograms")
    return {"images": birds_detector.open_audio(samples, sample_rate, duration)}


# POST, async API endpoint example
@ai4e_service.api_sync_func(
    api_path="/detect/passerines",
    methods=["POST"],
    request_processing_function=process_request_data,  # This is the data process function that you created above.
    maximum_concurrent_requests=5,  # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types=ACCEPTED_CONTENT_TYPES,
    content_max_length=10000,  # In bytes
    trace_name="post:detect_passerines",
)
def detect(*args, **kwargs):
    """ Return predictions
    """
    print("runserver.py: detect(passerines) called")
    audio_io = kwargs.get("audio_io")

    load_output = process_audio(func_name="detect(passerines)", audio_io=audio_io)

    if "error" in load_output.keys():
        return load_output
    images = load_output["images"]

    print("runserver.py: detect(passerines), predict")
    preds = MODEL_PASSERINES.predict(images)

    print("runserver.py: detect(passerines), generate scores")
    scores = [{} for _ in range(preds.shape[0])]
    for p_idx, pred in enumerate(preds):
        for cls, score in zip(SPECIES_PASSERINES["species"].values, pred):
            scores[p_idx][cls] = round(float(score), 5)

    print("runserver.py: detect(passerines), return predictions")
    return {"predictions": scores}


# POST, async API endpoint example
@ai4e_service.api_sync_func(
    api_path="/detect/non_passerines",
    methods=["POST"],
    request_processing_function=process_request_data,  # This is the data process function that you created above.
    maximum_concurrent_requests=5,  # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types=ACCEPTED_CONTENT_TYPES,
    content_max_length=10000,  # In bytes
    trace_name="post:detect_nonpasserines",
)
def detect(*args, **kwargs):
    """ Return predictions
    """
    print("runserver.py: detect(non_passerines) called")
    audio_io = kwargs.get("audio_io")

    load_output = process_audio(func_name="detect(non_passerines)", audio_io=audio_io)

    if "error" in load_output.keys():
        return load_output
    images = load_output["images"]

    print("runserver.py: detect(non_passerines), predict")
    preds = MODEL_NONPASSERINES.predict(images)

    print("runserver.py: detect(non_passerines), generate scores")
    scores = [{} for _ in range(preds.shape[0])]
    for p_idx, pred in enumerate(preds):
        for cls, score in zip(SPECIES_NONPASSERINES["species"].values, pred):
            scores[p_idx][cls] = round(float(score), 5)

    print("runserver.py: detect(non_passerines), return predictions")
    return {"predictions": scores}


@ai4e_service.api_sync_func(
    api_path="/spectrogram",
    methods=["POST"],
    request_processing_function=process_request_data,
    maximum_concurrent_requests=5,
    content_types=ACCEPTED_CONTENT_TYPES,
    content_max_length=10000,
    trace_name="post:spectrogram",
)
def spect(*args, **kwargs):
    """ Return spectrogram
    """

    print("runserver.py: spect() called")
    audio_io = kwargs.get("audio_io")

    load_output = process_audio(func_name="spectrogram", audio_io=audio_io)

    if "error" in load_output.keys():
        return load_output
    images = load_output["images"]

    print("runserver.py: spect(), return spectrogram(s)")
    return {"images": (images * 255).tolist()}


if __name__ == "__main__":
    app.run()
