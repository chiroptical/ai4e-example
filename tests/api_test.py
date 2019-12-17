#!/usr/bin/env python3
import pytest
import requests
from io import BytesIO


@pytest.fixture
def basic_wav_file():
    with open("client/cardinalis-cardinalis.wav", "rb") as audio:
        return audio.read()


@pytest.fixture
def dual_channel_audio():
    with open("client/dual-channel.wav", "rb") as audio:
        return audio.read()


@pytest.fixture
def four_channel_audio():
    with open("client/four-channel.wav", "rb") as audio:
        return audio.read()


@pytest.fixture
def api_url():
    return "http://localhost:8081/v1/birds/detect"


def test_post_with_no_data_errors(api_url):
    req = requests.post(api_url)
    assert req.json() == {"error": "No data was given with post?"}


def test_post_with_junk_data_errors(api_url):
    req = requests.post(api_url, data=b"helloworld")
    assert req.json() == {"error": "I could not load the audio"}


def test_predicts_cardinalis(basic_wav_file, api_url):
    req = requests.post(api_url, data=basic_wav_file)
    assert [x for x in req.json()["predictions"][0] if "cardinalis-cardinalis" in x][
        0
    ] == "cardinalis-cardinalis: 0.05695"


def test_four_channel_fails(four_channel_audio, api_url):
    req = requests.post(api_url, data=four_channel_audio)
    assert req.json() == {"error": "Audio has more than two channels, ignoring"}


def test_dual_channel_returns_predictions(dual_channel_audio, api_url):
    res = requests.post(api_url, data=dual_channel_audio).json()
    assert len(res["predictions"]) == 2
    assert len(res["predictions"][0]) == 508
