"""Step 0: create the practice data for the labs.

  m3_normal.csv   -> 3000 normal readings only   (Lab A: anomaly detection)
  m3_labeled.csv  -> 3000 readings with a label  (Lab B: classification)

With a real project, you replace these with data you logged yourself (Part 1).
"""
import csv, random
from m3_common import FEATURES, fake_reading

random.seed(42)

with open("m3_normal.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(FEATURES)
    for _ in range(3000):
        w.writerow(fake_reading())

# Faults are rare in real life: about 3% each
with open("m3_labeled.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(FEATURES + ["label"])
    for _ in range(3000):
        r = random.random()
        label = ("bearing" if r < 0.03 else "overheat" if r < 0.06
                 else "overload" if r < 0.09 else "normal")
        w.writerow(fake_reading(None if label == "normal" else label) + [label])

print("Created m3_normal.csv and m3_labeled.csv")
