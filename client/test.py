#!/usr/bin/env python3
import requests
from io import BytesIO
import json

with open("client/cardinalis-cardinalis.wav", "rb") as audio:
    audio_bytes = audio.read()

r = requests.post("http://localhost:8081/v1/birds/detect", data=audio_bytes)

results = json.loads(r.text)
print(
    [x for x in results["predictions"][0] if "cardinalis-cardinalis" in x][0]
    == "cardinalis-cardinalis: 0.05695"
)
