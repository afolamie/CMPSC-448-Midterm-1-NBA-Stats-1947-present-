"""Exploratory CMPSC 448 RQ4 baselines from the held-out WildBench splits.

Usage: python CMPSC448_feature_baseline.py --data-dir generated/splits
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def features(df):
    response = df["LLM_output"].fillna("").astype(str)
    return pd.DataFrame({
        "log_word_count": np.log1p(response.str.split().str.len()),
        "bullet_list": response.str.contains(r"(?m)^\s*[-*]\s+", regex=True).astype(int),
        "numbered_list": response.str.contains(r"(?m)^\s*\d+[.)]\s+", regex=True).astype(int),
        "markdown_heading": response.str.contains(r"(?m)^#{1,6}\s+", regex=True).astype(int),
        "code_fence": response.str.contains("```", regex=False).astype(int),
        "bold_markdown": response.str.contains("**", regex=False).astype(int),
        "log_linebreaks": np.log1p(response.str.count("\n")),
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="generated/splits")
    parser.add_argument("--output", default="results/feature_baseline.json")
    args = parser.parse_args()
    source = Path(args.data_dir)
    train = pd.read_csv(source / "train.csv")
    test = pd.read_csv(source / "test.csv")
    assert not set(train.LLM_Input) & set(test.LLM_Input), "Prompt leakage detected"
    feat_train, feat_test = features(train), features(test)
    labels = ["claude", "gemini", "gpt"]
    results = []
    for title, columns in [
        ("response length", ["log_word_count"]),
        ("length and formatting", feat_train.columns.tolist()),
    ]:
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, random_state=448))
        model.fit(feat_train[columns], train.LLM_name)
        prediction = model.predict(feat_test[columns])
        result = {
            "feature_set": title,
            "features": columns,
            "train_count": len(train),
            "test_count": len(test),
            "accuracy": float(accuracy_score(test.LLM_name, prediction)),
            "macro_f1": float(f1_score(test.LLM_name, prediction, average="macro")),
            "confusion_matrix": confusion_matrix(test.LLM_name, prediction, labels=labels).tolist(),
            "class_order": labels,
        }
        print(f"{title}: accuracy={result['accuracy']:.4f}, macro_f1={result['macro_f1']:.4f}")
        results.append(result)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
