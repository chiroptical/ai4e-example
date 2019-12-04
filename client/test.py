#!/usr/bin/env python3
import requests
from io import BytesIO

with open("client/cardinalis-cardinalis.wav", "rb") as audio:
    audio_bytes = audio.read()

r = requests.post("http://localhost:8081/v1/birds/detect", data=audio_bytes)

print(r.text)
