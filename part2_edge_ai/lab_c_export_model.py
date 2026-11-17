"""Lab C (part 1, OPTIONAL, run on a laptop): train a tiny neural network
and export it as m3_model.tflite.  Needs: pip install tensorflow
You can skip this: m3_model.tflite is already included.
"""
import numpy as np, pandas as pd, tensorflow as tf

df = pd.read_csv("m3_labeled.csv")
X = df[["temp", "vibration", "current"]].values.astype("float32")
classes = ["bearing", "normal", "overheat", "overload"]
y = df["label"].map({c: i for i, c in enumerate(classes)}).values

norm = tf.keras.layers.Normalization()
norm.adapt(X)                                  # scaling is baked into the model
model = tf.keras.Sequential([tf.keras.Input(shape=(3,)), norm,
                             tf.keras.layers.Dense(16, activation="relu"),
                             tf.keras.layers.Dense(4, activation="softmax")])
model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(X, y, epochs=40, batch_size=32, verbose=0,
          class_weight={0: 10, 1: 1, 2: 10, 3: 10})

conv = tf.lite.TFLiteConverter.from_keras_model(model)
conv.optimizations = [tf.lite.Optimize.DEFAULT]   # quantize weights -> smaller
open("m3_model.tflite", "wb").write(conv.convert())
print("Saved m3_model.tflite")
