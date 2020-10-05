#!/usr/bin/env python
from math import ceil
import numpy as np
from opensoundscape.spectrogram import Spectrogram
import torch
from torchvision import transforms


def split_audio(audio_obj, seg_duration=5, seg_overlap=1):
    duration = audio_obj.duration()
    times = np.arange(0.0, duration, duration / audio_obj.samples.shape[0])

    num_segments = ceil((duration - seg_overlap) / (seg_duration - seg_overlap))
    outputs = [None] * num_segments
    for idx in range(num_segments):
        if idx == num_segments - 1:
            end = duration
            begin = end - seg_duration
        else:
            begin = seg_duration * idx - seg_overlap * idx
            end = begin + seg_duration

        audio_segment_obj = audio_obj.trim(begin, end)
        outputs[idx] = audio_segment_obj

    return outputs


class BasicDataset(torch.utils.data.Dataset):
    def __init__(self, images):
        self.images = images
        self.mean = torch.tensor([0.5 for _ in range(3)])
        self.stddev = torch.tensor([0.5 for _ in range(3)])
        self.transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize(self.mean, self.stddev)]
        )

    def __len__(self):
        return len(self.images)

    def __getitem__(self, item_idx):
        img = self.images[item_idx]
        return {"X": self.transform(img)}
