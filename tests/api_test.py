#!/usr/bin/env python3
import pytest
import requests
from io import BytesIO


@pytest.fixture
def basic_wav_file():
    name = "client/cardinalis-cardinalis.wav"
    with open(name, "rb") as audio:
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
def detect_cardinalis_cardinalis_api_url():
    return "http://localhost:8081/v1/birds/detect/cardinalis_cardinalis"


@pytest.fixture
def detect_haemorhous_mexicanus_api_url():
    return "http://localhost:8081/v1/birds/detect/haemorhous_mexicanus"


@pytest.fixture
def detect_melospiza_melodia_api_url():
    return "http://localhost:8081/v1/birds/detect/melospiza_melodia"


@pytest.fixture
def detect_thryothorus_ludovicianus_api_url():
    return "http://localhost:8081/v1/birds/detect/thryothorus_ludovicianus"


@pytest.fixture
def detect_turdus_migratorius_api_url():
    return "http://localhost:8081/v1/birds/detect/turdus_migratorius"


@pytest.fixture
def detect_zenaida_macroura_api_url():
    return "http://localhost:8081/v1/birds/detect/zenaida_macroura"


@pytest.fixture
def spectrogram_api_url():
    return "http://localhost:8081/v1/birds/spectrogram"


def test_post_with_no_data_errors(detect_cardinalis_cardinalis_api_url):
    req = requests.post(detect_cardinalis_cardinalis_api_url)
    assert req.status_code == 401


def test_post_with_junk_data_errors(detect_cardinalis_cardinalis_api_url):
    req = requests.post(detect_cardinalis_cardinalis_api_url, data=b"helloworld")
    assert req.status_code == 401


def test_detect_cardinalis_cardinalis(
    basic_wav_file, detect_cardinalis_cardinalis_api_url
):
    req = requests.post(
        detect_cardinalis_cardinalis_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][1] > 0.99


def test_detect_haemorhous_mexicanus(
    basic_wav_file, detect_haemorhous_mexicanus_api_url
):
    req = requests.post(
        detect_haemorhous_mexicanus_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][0] > 0.99


def test_detect_melospiza_melodia(basic_wav_file, detect_melospiza_melodia_api_url):
    req = requests.post(
        detect_melospiza_melodia_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][0] > 0.90


def test_detect_thryothorus_ludovicianus(
    basic_wav_file, detect_thryothorus_ludovicianus_api_url
):
    req = requests.post(
        detect_thryothorus_ludovicianus_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][0] > 0.3
    assert req.json()["predictions"][0][1] > 0.6


def test_detect_turdus_migratorius(basic_wav_file, detect_turdus_migratorius_api_url):
    req = requests.post(
        detect_turdus_migratorius_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][0] > 0.90


def test_detect_zenaida_macroura(basic_wav_file, detect_zenaida_macroura_api_url):
    req = requests.post(
        detect_zenaida_macroura_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json()["predictions"][0][0] > 0.30
    assert req.json()["predictions"][0][1] > 0.60


def test_four_channel_fails(four_channel_audio, detect_cardinalis_cardinalis_api_url):
    req = requests.post(
        detect_cardinalis_cardinalis_api_url,
        data=four_channel_audio,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json() == {
        "error": "Unable to load audio, multi-chennel input is ignored"
    }


def test_dual_channel_fails(dual_channel_audio, detect_cardinalis_cardinalis_api_url):
    req = requests.post(
        detect_cardinalis_cardinalis_api_url,
        data=dual_channel_audio,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert req.json() == {
        "error": "Unable to load audio, multi-chennel input is ignored"
    }


def test_spectrogram_dimensions(basic_wav_file, spectrogram_api_url):
    req = requests.post(
        spectrogram_api_url,
        data=basic_wav_file,
        headers={"Content-type": "audio/vnd.wav"},
    )
    assert len(req.json()["images"]) == 1
    assert len(req.json()["images"][0]) == 224
    assert len(req.json()["images"][0][0]) == 224
    assert len(req.json()["images"][0][0][0]) == 3
    with pytest.raises(TypeError) as info:
        len(req.json()["images"][0][0][0][0])
    assert "object of type 'int' has no len()" in str(info.value)
