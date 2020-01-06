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
def detect_api_url():
    return "http://localhost:8081/v1/birds/detect"


@pytest.fixture
def spectrogram_api_url():
    return "http://localhost:8081/v1/birds/spectrogram"


def test_post_with_no_data_errors(detect_api_url):
    req = requests.post(detect_api_url)
    assert req.json() == {"error": "No data was given with post?"}


def test_post_with_junk_data_errors(detect_api_url):
    req = requests.post(detect_api_url, data=b"helloworld")
    assert req.json() == {"error": "I could not load the audio"}


def test_predicts_cardinalis(basic_wav_file, detect_api_url):
    req = requests.post(detect_api_url, data=basic_wav_file)
    assert req.json()["predictions"][0]["cardinalis-cardinalis"] == 0.05695


def test_four_channel_fails(four_channel_audio, detect_api_url):
    req = requests.post(detect_api_url, data=four_channel_audio)
    assert req.json() == {"error": "Audio has more than one channel, ignoring"}


def test_dual_channel_fails(dual_channel_audio, detect_api_url):
    req = requests.post(detect_api_url, data=dual_channel_audio)
    assert req.json() == {"error": "Audio has more than one channel, ignoring"}


def test_spectrogram_dimensions(basic_wav_file, spectrogram_api_url):
    req = requests.post(spectrogram_api_url, data=basic_wav_file)
    assert len(req.json()["images"]) == 1
    assert len(req.json()["images"][0]) == 299
    assert len(req.json()["images"][0][0]) == 299
    assert len(req.json()["images"][0][0][0]) == 3
    with pytest.raises(TypeError) as info:
        len(req.json()["images"][0][0][0][0])
    assert "object of type 'float' has no len()" in str(info.value)


def test_detect_status_code_200(basic_wav_file, detect_api_url):
    req = requests.post(detect_api_url, data=basic_wav_file)
    assert req.status_code == 200


def test_spectrogram_status_code_200(basic_wav_file, spectrogram_api_url):
    req = requests.post(spectrogram_api_url, data=basic_wav_file)
    assert req.status_code == 200
