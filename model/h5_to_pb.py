#!/usr/bin/env python
import tensorflow as tf
model = tf.keras.models.load_model("model.h5")
tf.keras.experimental.export_saved_model(model, "save")
