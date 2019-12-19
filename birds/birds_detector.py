#!/usr/bin/env python
import tensorflow as tf
import numpy as np
from PIL import Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont

from io import BytesIO

# from librosa import resample, to_mono, power_to_db
import librosa
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
    """
    Applies a bandpass filter to a spectrogram

    Inputs:
        lower: low-frequency bound (Hz)
        upper: high-frequency bound (Hz)
        freq: ndarray of sample frequencies
        spec: spectrogram
    Returns:
        freq, spec adjusted to only include the desired frequencies
        
    """

    lowest_index = np.abs(freq - lower).argmin()
    highest_index = np.abs(freq - upper).argmin()
    spec = spec[lowest_index:highest_index, :]
    freq = freq[lowest_index:highest_index]
    return freq, spec


def samples_to_spec(input_samples, input_sample_rate, target_sample_rate=22050):
    """
    Generates a spectrogram image from samples

    Inputs:
        input_samples: The input samples
        input_sample_rate: The sampling rate of the input samples
        target_sample_rate: The target sampling rate

    Returns:
        spectrogram: As a Frequency x Time matrix

    Note: this code was revamped by Justin Kitzes, 2019/06/28
    """

    samples = librosa.resample(
        input_samples, input_sample_rate, target_sample_rate, res_type="kaiser_fast"
    )

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
    spec = librosa.power_to_db(spec[::-1, :])

    # Apply gain and range as in Audacity defaults
    #spec_gain = 20
    #spec_range = 80
    #spec[spec > -spec_gain] = -spec_gain
    #spec[spec < -(spec_gain + spec_range)] = -(spec_gain + spec_range)

    return 255 - min_max_scale(spec, feature_range=(0, 200))


def to_mono(samples):
    """ Reshape samples and convert to_mono via librosa
    """
    # libsndfile reads dual-channel files as (N, 2) but librosa
    # requires (2, N)
    return librosa.to_mono(np.reshape(samples, (2, -1)))


def load_samples(audio_bytes):
    """ Use libsndfile to extract the samples and sample rate

    Args:
        audio_bytes: wav file in bytes

    Return:
        samples: The audio samples
        sample_rate: The sample rate of the original audio
    """
    return soundfile_read(audio_bytes)


def audio_duration(samples, sample_rate):
    """ Given samples and sample rate return data to make predictions on

    Args:
        samples: The audio samples from libsndfile
        sample_rate: The sampling rate of the samples

    Return:
        duration: The audio duration in seconds
        image: A 299 by 299 image
    """
    return len(samples) / sample_rate


def open_audio(samples, input_sample_rate, duration):
    """ Given samples and sample rate return data to make predictions on

    Args:
        samples: The audio samples from libsndfile
        sample_rate: The sampling rate of the samples
        duration: The duration of the audio

    Return:
        images: array of 299 by 299 images, each 
            representing up to 5s of audio
    """

    # Number of frames
    frames = len(samples)

    # Determine 5 second chunks which need to
    # be predicted on
    samples_needed = 5 * input_sample_rate
    start = 0
    starts = []
    stop = samples_needed
    stops = []
    while start < frames:
        if start + samples_needed > frames:
            starts.append(frames - samples_needed)
            stops.append(frames)
        else:
            starts.append(start)
            stops.append(stop)

        start += samples_needed
        stop += samples_needed

    # Now we can generate spectrograms and store them in
    # images
    images = np.empty((len(starts), 299, 299, 3))
    for idx, (begin, end) in enumerate(zip(starts, stops)):
        # Generate the spectrogram
        spectrogram = samples_to_spec(samples[begin:end], input_sample_rate)

        # Generate an image and resize it
        image = Image.fromarray(spectrogram).convert("RGB").resize((299, 299))

        images[idx] = np.array(image) / 255.0

    return images
