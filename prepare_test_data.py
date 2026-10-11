import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

REQUIRED = ["LLM_name", "LLM_Input", "LLM_output"]

def prepare(frame, seed=448):
    if not set(REQUIRED).issubset(frame.columns):
        raise ValueError(f"Missing columns: {set(REQUIRED)-set(frame.columns)}")
    data = frame[REQUIRED].dropna().drop_duplicates().copy()
    for c in REQUIRED:
        data[c] = data[c].astype(str).str.strip()
    data = data[(data[REQUIRED] != "").all(axis=1)].reset_index(drop=True)
    if data.LLM_Input.nunique() < 5:
        raise ValueError("Need at least five distinct prompts")
    data.LLM_name = data.LLM_name.str.lower().replace({"chatgpt":"gpt", "openai":"gpt", "gpt-4o":"gpt", "anthropic":"claude", "google":"gemini"})
    split = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=seed)
    rest_idx, test_idx = next(split.split(data, groups=data.LLM_Input))
    rest, test = data.iloc[rest_idx].reset_index(drop=True), data.iloc[test_idx].reset_index(drop=True)
    split = GroupShuffleSplit(n_splits=1, test_size=.125, random_state=seed)
    train_idx, val_idx = next(split.split(rest, groups=rest.LLM_Input))
    train, val = rest.iloc[train_idx].reset_index(drop=True), rest.iloc[val_idx].reset_index(drop=True)
    if any(d.empty for d in (train, val, test)):
        raise ValueError("Empty split")
    groups = [set(d.LLM_Input) for d in (train, val, test)]
    assert not (groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
    return train, val, test

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="data/splits")
    p.add_argument("--seed", type=int, default=448)
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in zip(("train","validation","test"), prepare(pd.read_csv(args.input), args.seed)):
        df.to_csv(out/f"{name}.csv", index=False)
        print(name, len(df), "responses;", df.LLM_Input.nunique(), "prompts")
