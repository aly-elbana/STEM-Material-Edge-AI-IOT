"""Train + evaluate a model on ANY sensor CSV - the honest way.

Classification (you have labels: normal / fault_a / fault_b ...):
    python -m ml.tabular.train_tabular data.csv --target label
Anomaly detection (only normal data, labels optional for testing):
    python -m ml.tabular.train_tabular normal.csv --mode anomaly --test test.csv --target label

Outputs in --out (default models/):
    model.joblib          -> load on the Pi with joblib.load()
    report.txt            -> precision / recall / F1 per class  (put it in your logbook)
    confusion_matrix.png  -> the picture the judges want to see
    features.json         -> the exact column order the model expects

Models:
    rf      RandomForest   (default - strong, simple, no scaling needed)
    gb      GradientBoosting
    knn     k-nearest neighbours (scaled)
    svm     support vector machine (scaled)
    logreg  logistic regression (scaled, very small model)
"""
import argparse
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier, LocalOutlierFactor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def classifier(name):
    return {
        "rf": RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42),
        "gb": GradientBoostingClassifier(random_state=42),
        "knn": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "svm": make_pipeline(StandardScaler(), SVC(class_weight="balanced", probability=True)),
        "logreg": make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000)),
    }[name]


def detector(name, contamination):
    return {
        "ellipse": EllipticEnvelope(contamination=contamination, random_state=42),
        "lof": make_pipeline(StandardScaler(), LocalOutlierFactor(novelty=True, contamination=contamination)),
        "iforest": IsolationForest(contamination=contamination, random_state=42),
    }[name]


def save_confusion(cm, labels, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(1.2 * len(labels) + 3, 1.2 * len(labels) + 2.5))
    ax.imshow(cm, cmap="Oranges")
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual (truth)")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=12)
    ax.set_title("Confusion matrix (test set)")
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--target", default="label", help="label column name")
    p.add_argument("--features", nargs="*", help="columns to use (default: all numeric except target)")
    p.add_argument("--mode", choices=["classify", "anomaly"], default="classify")
    p.add_argument("--model", default=None, help="rf|gb|knn|svm|logreg  or  ellipse|lof|iforest")
    p.add_argument("--test", help="separate test CSV (anomaly mode: should contain some faults)")
    p.add_argument("--test-size", type=float, default=0.2)
    p.add_argument("--group", help="column to keep together when splitting (e.g. session, person, day)")
    p.add_argument("--contamination", type=float, default=0.01)
    p.add_argument("--out", default="models")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    df = pd.read_csv(a.csv)
    feats = a.features or [c for c in df.select_dtypes("number").columns
                           if c not in (a.target, "timestamp")]
    print("features:", feats)
    if len(df) < 10 * len(feats):
        print(f"WARNING: only {len(df)} rows for {len(feats)} features. Aim for at least "
              f"{10 * len(feats)} rows (record longer / more sessions), or use fewer features. "
              "With too little data the model flags everything new as an anomaly.")
    report = []

    if a.mode == "classify":
        df = df.dropna(subset=feats + [a.target])
        X, y = df[feats], df[a.target].astype(str)
        print("class counts:\n", y.value_counts().to_string())
        if a.group:   # no leakage: the same person/session never appears in train AND test
            from sklearn.model_selection import GroupShuffleSplit
            gss = GroupShuffleSplit(n_splits=1, test_size=a.test_size, random_state=42)
            tr, te = next(gss.split(X, y, df[a.group]))
            X_tr, X_te, y_tr, y_te = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
        else:
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=a.test_size,
                                                      stratify=y, random_state=42)
        clf = classifier(a.model or "rf")
        cv = cross_val_score(clf, X_tr, y_tr, cv=StratifiedKFold(5, shuffle=True, random_state=42))
        clf.fit(X_tr, y_tr)
        pred = clf.predict(X_te)
        labels = sorted(y.unique())
        cm = confusion_matrix(y_te, pred, labels=labels)
        report += [f"model: {a.model or 'rf'}",
                   f"train rows: {len(X_tr)}   test rows: {len(X_te)}",
                   f"5-fold CV accuracy on train: {cv.mean():.3f} +- {cv.std():.3f}",
                   f"TRAIN accuracy: {accuracy_score(y_tr, clf.predict(X_tr)):.3f}",
                   f"TEST accuracy:  {accuracy_score(y_te, pred):.3f}   <- report THIS one",
                   "", classification_report(y_te, pred, digits=3),
                   "confusion matrix (rows = truth, cols = predicted): " + str(labels), str(cm)]
        if hasattr(clf, "feature_importances_"):
            imp = sorted(zip(clf.feature_importances_, feats), reverse=True)
            report += ["", "feature importance:"] + [f"  {f}: {v:.3f}" for v, f in imp]
        model = clf
    else:
        X = df[feats].dropna()
        model = detector(a.model or "ellipse", a.contamination).fit(X)
        if a.test:
            t = pd.read_csv(a.test).dropna(subset=feats)
            truth = np.where(t[a.target].astype(str) == "normal", "normal", "anomaly")
            pred = np.where(model.predict(t[feats]) == 1, "normal", "anomaly")
            labels = ["normal", "anomaly"]
            cm = confusion_matrix(truth, pred, labels=labels)
            report += [f"detector: {a.model or 'ellipse'}  contamination={a.contamination}",
                       classification_report(truth, pred, digits=3), str(cm)]
        else:
            report += ["No --test file: train only. Test on readings that include real or",
                       "simulated faults, otherwise you cannot prove anything."]
            cm, labels = None, None

    if cm is not None:
        save_confusion(cm, labels, os.path.join(a.out, "confusion_matrix.png"))
    joblib.dump(model, os.path.join(a.out, "model.joblib"))
    with open(os.path.join(a.out, "features.json"), "w") as f:
        json.dump({"features": feats, "mode": a.mode}, f, indent=2)
    text = "\n".join(report)
    open(os.path.join(a.out, "report.txt"), "w").write(text)
    print(text)
    print(f"\nsaved -> {a.out}/model.joblib, report.txt, confusion_matrix.png")


if __name__ == "__main__":
    main()
