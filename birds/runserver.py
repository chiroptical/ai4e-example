# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from io import BytesIO
import pandas as pd
import numpy as np
import torch
import torchvision
from opensoundscape.audio import Audio
from opensoundscape.spectrogram import Spectrogram
import birds_detector

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ["audio/vnd.wav"]

app = Flask(__name__)
# Maximum content length can be 5 mb
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

# Load the model
# The model was copied to this location when the container was built; see ../Dockerfile
num_classes = 2
opensoundscape_tar = torch.load(
    "/app/birds/cardinalis-cardinalis-2020-09-12-epoch-200.tar"
)
model = torchvision.models.resnet18(pretrained=False)
model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
model.load_state_dict(opensoundscape_tar["model_state_dict"])

# Define a function for processing request data, if applicable. This function
# loads data or files into a dictionary for access in your API function. We
# pass this function as a parameter to your API setup.
def process_request_data(req):
    """Wrap input data into BytesIO object"""
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
        audio = Audio.from_bytesio(
            audio_io, sample_rate=22050, resample_type="kaiser_fast"
        )
    except:
        return {"error": "Unable to load audio, multi-chennel input is ignored"}
    print(
        f"runserver.py: {func_name}() loaded samples at sample_rate {audio.sample_rate}"
    )

    # Check the duration is between 5 and 20 seconds
    duration = audio.duration()
    if duration < 5:
        return {"error": "Audio is shorter than 5 seconds"}
    elif duration > 20:
        return {"error": "Audio is longer than 20 seconds"}

    # 1. split audio into 5 second chunks
    # 2. generate spectrograms
    # 3. generate images
    audio_splits = birds_detector.split_audio(audio)
    spectrograms = [Spectrogram.from_audio(x) for x in audio_splits]
    images = [x.to_image(shape=(224, 224)) for x in spectrograms]

    print(f"runserver.py: {func_name}(), opening audio as spectrograms")
    return {"images": images}


# POST, async API endpoint example
@ai4e_service.api_sync_func(
    api_path="/detect/cardinalis_cardinalis",
    methods=["POST"],
    request_processing_function=process_request_data,
    maximum_concurrent_requests=5,
    content_types=ACCEPTED_CONTENT_TYPES,
    content_max_length=MAX_CONTENT_LENGTH,
    trace_name="post:detect_cardinalis_cardinalis",
)
def detect(*args, **kwargs):
    """Return predictions"""
    detect_str = "detect(cardinalis_cardinalis)"

    print(f"runserver.py: {detect_str} called")
    audio_io = kwargs.get("audio_io")

    load_output = process_audio(func_name=f"{detect_str}", audio_io=audio_io)

    if "error" in load_output.keys():
        return load_output
    images = load_output["images"]

    print(f"runserver.py: {detect_str} predict")
    # Generation predictions from model
    dataset = birds_detector.BasicDataset(images)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)
    scores = []
    model.eval()
    for batch in dataloader:
        X = batch["X"]
        predictions = model(X)
        for x in torch.nn.functional.softmax(predictions, 1).detach().cpu().numpy():
            scores.append(x.tolist())

    print(f"runserver.py: {detect_str} return predictions")
    return {"predictions": scores}


@ai4e_service.api_sync_func(
    api_path="/spectrogram",
    methods=["POST"],
    request_processing_function=process_request_data,
    maximum_concurrent_requests=5,
    content_types=ACCEPTED_CONTENT_TYPES,
    content_max_length=MAX_CONTENT_LENGTH,
    trace_name="post:spectrogram",
)
def spect(*args, **kwargs):
    """Return spectrogram"""

    print("runserver.py: spect() called")
    audio_io = kwargs.get("audio_io")

    load_output = process_audio(func_name="spectrogram", audio_io=audio_io)

    if "error" in load_output.keys():
        return load_output
    images = load_output["images"]

    # `images` is [Image], need regular Python lists for JSON serialization
    images = [np.array(x).tolist() for x in images]

    print("runserver.py: spect(), return spectrogram(s)")
    return {"images": images}


if __name__ == "__main__":
    app.run()
