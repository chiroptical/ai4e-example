#!/usr/bin/env python3
import requests
from io import BytesIO

with open("750B-2015-02-03_17-40.wav", "rb") as audio:
    audio_bytes = audio.read()

r = requests.post("http://localhost:8081/v1/rats/detect", data=audio_bytes)

print(r.text)
