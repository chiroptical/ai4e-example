#!/usr/bin/env python3
import pytest
import requests
from io import BytesIO


@pytest.fixture
def basic_wav_file():
    name = "client/cardinalis-cardinalis.wav"
    with open(name, "rb") as audio:
        return audio.read()


# @pytest.fixture
# def dual_channel_audio():
#     with open("client/dual-channel.wav", "rb") as audio:
#         return audio.read()


# @pytest.fixture
# def four_channel_audio():
#     with open("client/four-channel.wav", "rb") as audio:
#         return audio.read()


@pytest.fixture
def detect_cardinalis_cardinalis_api_url():
    return "http://localhost:8081/v1/birds/detect/cardinalis_cardinalis"


def test_post_with_no_data_errors(detect_cardinalis_cardinalis_api_url):
    req = requests.post(detect_cardinalis_cardinalis_api_url)
    assert req.status_code == 401


def test_post_with_junk_data_errors(detect_cardinalis_cardinalis_api_url):
    req = requests.post(detect_cardinalis_cardinalis_api_url, data=b"helloworld")
    assert req.status_code == 401


def test_detect_passerines_cardinalis(
    basic_wav_file, detect_cardinalis_cardinalis_api_url
):
    req = requests.post(
        detect_cardinalis_cardinalis_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][1] > 0.99


# def test_four_channel_fails(four_channel_audio, detect_cardinalis_cardinalis_api_url):
#     req = requests.post(detect_cardinalis_cardinalis_api_url, data=four_channel_audio)
#     assert req.json() == {"error": "Audio has more than one channel, ignoring"}


# def test_dual_channel_fails(dual_channel_audio, detect_cardinalis_cardinalis_api_url):
#     req = requests.post(detect_cardinalis_cardinalis_api_url, data=dual_channel_audio)
#     assert req.json() == {"error": "Audio has more than one channel, ignoring"}


# # def test_spectrogram_dimensions(basic_wav_file, spectrogram_api_url):
# #     req = requests.post(spectrogram_api_url, data=basic_wav_file)
# #     assert len(req.json()["images"]) == 1
# #     assert len(req.json()["images"][0]) == 299
# #     assert len(req.json()["images"][0][0]) == 299
# #     assert len(req.json()["images"][0][0][0]) == 3
# #     with pytest.raises(TypeError) as info:
# #         len(req.json()["images"][0][0][0][0])
# #     assert "object of type 'float' has no len()" in str(info.value)


# def test_detect_status_code_200(basic_wav_file, detect_cardinalis_cardinalis_api_url):
#     req = requests.post(detect_cardinalis_cardinalis_api_url, data=basic_wav_file)
#     assert req.status_code == 200


# # def test_spectrogram_status_code_200(basic_wav_file, spectrogram_api_url):
# #     req = requests.post(spectrogram_api_url, data=basic_wav_file)
# #     assert req.status_code == 200
