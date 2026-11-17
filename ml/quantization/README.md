# Quantization: make the model smaller and faster

| Type | Size | Speed on Pi CPU | Accuracy | How |
|---|---|---|---|---|
| float32 | 1x | 1x | reference | default export |
| float16 | 1/2 | ~same on CPU | ~same | `supported_types=[tf.float16]` |
| dynamic range int8 | ~1/4 | faster | small drop | `optimizations=[DEFAULT]` |
| full int8 | 1/4 | fastest, needed by many accelerators | check it! | + `representative_dataset` (real samples) |

Rule: **measure before and after** (`compare_tflite.py`): size, ms per inference, accuracy on the test set.
If accuracy drops more than ~1-2 points, keep fp16 or use more/better representative samples.
