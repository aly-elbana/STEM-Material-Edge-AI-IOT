"""Lab B: prove the accuracy. Never trust a number measured on training data.

Run 00_make_data.py first.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv("m3_labeled.csv")
X = df[["temp", "vibration", "current"]]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=42)   # rare faults in both sets

clf = RandomForestClassifier(class_weight="balanced", random_state=42)
clf.fit(X_train, y_train)          # study on training data only

pred = clf.predict(X_test)         # exam on unseen data
labels = sorted(y.unique())
print("Rows = truth, columns = prediction:", labels)
print(confusion_matrix(y_test, pred, labels=labels))
print(classification_report(y_test, pred))

# Look at recall for each fault: how many real faults did we catch?
# Then compare: clf.score(X_train, y_train) vs clf.score(X_test, y_test)
print("train accuracy:", round(clf.score(X_train, y_train), 3),
      "| test accuracy:", round(clf.score(X_test, y_test), 3))
