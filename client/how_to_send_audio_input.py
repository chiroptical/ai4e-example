#!/usr/bin/env python3
from io import BytesIO
import soundfile as sf
from librosa import resample

with open("750B-2015-02-03_17-40.wav", "rb") as audio:
    audio_bytes = BytesIO(audio.read())

samples, input_sample_rate = sf.read(
    audio_bytes,
)

output_sample_rate = 22050

samples = resample(
    samples,
    input_sample_rate,
    output_sample_rate,
    res_type="kaiser_best"
)

print(samples.shape)
