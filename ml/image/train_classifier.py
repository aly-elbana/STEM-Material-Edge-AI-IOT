"""Image classifier with TRANSFER LEARNING (MobileNetV2) -> .tflite for the Pi.
Run on a laptop or Google Colab (free GPU), NOT on the Pi.

Data: split/train/<class>/*.jpg, split/val/<class>/*.jpg, split/test/<class>/*.jpg
      (make it with: python -m ml.datasets.split_dataset my_images --out split)
    pip install tensorflow
    python -m ml.image.train_classifier split --epochs 10 --size 224

Outputs (models/image/):
    model.keras              full model
    model_fp16.tflite        half size, same accuracy  (good default for Pi CPU)
    model_int8.tflite        4x smaller, fastest       (check accuracy did not drop!)
    labels.txt               class order
    report.txt + confusion_matrix.png  on the TEST split

Why transfer learning: MobileNetV2 already learned edges/shapes from 1.4 M photos.
You only train the last layer on your classes -> good results from ~100-300 photos per class.
"""
import argparse
import os

import numpy as np

p = argparse.ArgumentParser()
p.add_argument("data")
p.add_argument("--size", type=int, default=224)
p.add_argument("--epochs", type=int, default=10)
p.add_argument("--fine-tune", type=int, default=0, help="extra epochs unfreezing the top layers")
p.add_argument("--batch", type=int, default=32)
p.add_argument("--out", default="models/image")
p.add_argument("--weights", default="imagenet", help="imagenet (needs internet once) or none (offline test only)")
a = p.parse_args()

import tensorflow as tf  # noqa: E402

os.makedirs(a.out, exist_ok=True)
S = (a.size, a.size)
kw = dict(image_size=S, batch_size=a.batch, label_mode="categorical")
train = tf.keras.utils.image_dataset_from_directory(os.path.join(a.data, "train"), shuffle=True, **kw)
val = tf.keras.utils.image_dataset_from_directory(os.path.join(a.data, "val"), shuffle=False, **kw)
test = tf.keras.utils.image_dataset_from_directory(os.path.join(a.data, "test"), shuffle=False, **kw)
classes = train.class_names
open(os.path.join(a.out, "labels.txt"), "w").write("\n".join(classes))
print("classes:", classes)

augment = tf.keras.Sequential([tf.keras.layers.RandomFlip("horizontal"),
                               tf.keras.layers.RandomRotation(0.05),
                               tf.keras.layers.RandomZoom(0.1),
                               tf.keras.layers.RandomBrightness(0.2)])
base = tf.keras.applications.MobileNetV2(input_shape=S + (3,), include_top=False,
                                         weights=None if a.weights == "none" else "imagenet", alpha=0.35 if a.size <= 160 else 1.0)
base.trainable = False
inp = tf.keras.Input(shape=S + (3,))
x = augment(inp)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)   # scaling is INSIDE the model
x = base(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
out = tf.keras.layers.Dense(len(classes), activation="softmax")(x)
model = tf.keras.Model(inp, out)
model.compile(tf.keras.optimizers.Adam(1e-3), "categorical_crossentropy", metrics=["accuracy"])
stop = tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)
model.fit(train, validation_data=val, epochs=a.epochs, callbacks=[stop])

if a.fine_tune:
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False
    model.compile(tf.keras.optimizers.Adam(1e-5), "categorical_crossentropy", metrics=["accuracy"])
    model.fit(train, validation_data=val, epochs=a.fine_tune, callbacks=[stop])

# ---- honest evaluation on the locked test split
y_true = np.concatenate([np.argmax(y, 1) for _, y in test])
y_pred = np.argmax(model.predict(test, verbose=0), 1)
from sklearn.metrics import classification_report, confusion_matrix  # noqa: E402
rep = classification_report(y_true, y_pred, target_names=classes, digits=3)
cm = confusion_matrix(y_true, y_pred)
open(os.path.join(a.out, "report.txt"), "w").write(rep + "\n" + str(cm))
print(rep, cm, sep="\n")
try:
    from ml.tabular.train_tabular import save_confusion
    save_confusion(cm, classes, os.path.join(a.out, "confusion_matrix.png"))
except Exception:
    pass

model.save(os.path.join(a.out, "model.keras"))
# ---- export for the edge
conv = tf.lite.TFLiteConverter.from_keras_model(model)
conv.optimizations = [tf.lite.Optimize.DEFAULT]
conv.target_spec.supported_types = [tf.float16]
open(os.path.join(a.out, "model_fp16.tflite"), "wb").write(conv.convert())


def representative():   # ~100 real images so int8 knows the value ranges
    for imgs, _ in train.take(4):
        for i in range(imgs.shape[0]):
            yield [tf.cast(imgs[i:i + 1], tf.float32)]


conv = tf.lite.TFLiteConverter.from_keras_model(model)
conv.optimizations = [tf.lite.Optimize.DEFAULT]
conv.representative_dataset = representative
open(os.path.join(a.out, "model_int8.tflite"), "wb").write(conv.convert())
for f in ("model_fp16.tflite", "model_int8.tflite"):
    print(f, round(os.path.getsize(os.path.join(a.out, f)) / 1e6, 2), "MB")
print("Next: python -m ml.quantization.compare_tflite", a.out, os.path.join(a.data, "test"))
