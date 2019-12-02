#!/usr/bin/env python
import tensorflow as tf
import numpy as np
from PIL import Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont

from io import BytesIO
from librosa import resample, to_mono, power_to_db
from scipy import signal
from sklearn.preprocessing import MinMaxScaler
from soundfile import read as soundfile_read


def min_max_scale(spect, feature_range=(0, 1)):
    bottom, top = feature_range
    spect_min = spect.min()
    spect_max = spect.max()
    scale_factor = (top - bottom) / (spect_max - spect_min)
    return scale_factor * (spect - spect_min) + bottom


def bandpass(lower, upper, freq, spec):
    '''
    Applies a bandpass filter to a spectrogram

    Inputs:
        lower: low-frequency bound (Hz)
        upper: high-frequency bound (Hz)
        freq: ndarray of sample frequencies
        spec: spectrogram
    Returns:
        freq, spec adjusted to only include the desired frequencies
        
    '''

    lowest_index = np.abs(freq - lower).argmin()
    highest_index = np.abs(freq - upper).argmin()
    spec = spec[lowest_index:highest_index, :]
    freq = freq[lowest_index:highest_index]
    return freq, spec


def samples_to_spec(input_samples, input_sample_rate, target_sample_rate=22050):
    '''
    Generates a spectrogram image from samples

    Inputs:
        input_samples: The input samples
        input_sample_rate: The sampling rate of the input samples
        target_sample_rate: The target sampling rate

    Returns:
        spectrogram: As a Frequency x Time matrix

    Note: this code was revamped by Justin Kitzes, 2019/06/28
    '''

    samples = resample(input_samples, input_sample_rate, target_sample_rate, res_type="kaiser_fast")

    # freq, time, spec = ...
    _, _, spec = signal.spectrogram(
        samples,
        target_sample_rate,
        window="hann",
        nperseg=512,
        noverlap=256,
        nfft=512,
        scaling="spectrum",
    )

    # Convert to decibel units
    spec = power_to_db(spec[::-1, :])
    
    # Apply gain and range as in Audacity defaults
    spec_gain = 20
    spec_range = 80
    spec[spec > -spec_gain] = -spec_gain
    spec[spec < -(spec_gain + spec_range)] = -(spec_gain + spec_range)
    
    return 255 - min_max_scale(spec, feature_range=(0, 200))


def open_audio(audio_bytes):
    """ Open audio in binary format using ...
    Args:
        audio_bytes: wav file in bytes
    Returns:
        image: A 299 by 299 image
    """

    # Load the samples
    samples, input_sample_rate = soundfile_read(
        audio_bytes,
    )

    # Generate the spectrogram
    spectrogram = samples_to_spec(samples, input_sample_rate)

    
    # Generate an image and resize it
    image = Image \
        .fromarray(spectrogram) \
        .convert("RGB") \
        .resize((299, 299))

    return image
