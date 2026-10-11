"""Build a three-family authorship dataset from public WildBench V2 outputs.

Source: https://huggingface.co/datasets/allenai/WildBench-V2-Model-Outputs
One version per family; match by session_id and keep identical prompts across all.
"""
import argparse
from pathlib import Path
import pandas as pd
from datasets import load_dataset

MODELS = {
    "gpt": "gpt-4o-2024-05-13",
    "claude": "claude-3-sonnet-20240229",
    "gemini": "gemini-1.5-pro",
}
SOURCE = "allenai/WildBench-V2-Model-Outputs"

def first_string(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return next((x.strip() for x in value if isinstance(x, str) and x.strip()), "")
    return ""

def load_family(label, config):
    ds = load_dataset(SOURCE, config, split="train")
    rows = []
    for record in ds:
        prompt = first_string(record.get("chat_history"))
        response = first_string(record.get("output"))
        session_id = str(record.get("session_id", "")).strip()
        if session_id and prompt and response:
            rows.append({"session_id": session_id, "LLM_name": label,
                         "LLM_Input": prompt, "LLM_output": response,
                         "source_model": config,
                         "primary_tag": record.get("primary_tag", "")})
    result = pd.DataFrame(rows).drop_duplicates(["session_id"])
    if result.empty:
        raise RuntimeError(f"No usable samples for {config}; check dataset schema")
    print(f"{label}: {len(result)} usable responses")
    return result

def build():
    frames = [load_family(label, config) for label, config in MODELS.items()]
    shared = set(frames[0].session_id)
    for frame in frames[1:]:
        shared &= set(frame.session_id)
    frames = [frame[frame.session_id.isin(shared)] for frame in frames]
    # Verify prompt identity: session_id matches are not sufficient if histories differ.
    common = frames[0].set_index("session_id")["LLM_Input"]
    for frame in frames[1:]:
        common = common[common.index.isin(frame.session_id)]
        other = frame.set_index("session_id")["LLM_Input"].reindex(common.index)
        common = common[common.eq(other)]
    valid = set(common.index)
    data = pd.concat([f[f.session_id.isin(valid)] for f in frames], ignore_index=True)
    counts = data.groupby("session_id").LLM_name.nunique()
    data = data[data.session_id.isin(counts[counts.eq(3)].index)].copy()
    if len(data) < 30 or data.LLM_name.nunique() != 3:
        raise RuntimeError(f"Insufficient matched examples: {len(data)} rows")
    return data.sort_values(["session_id", "LLM_name"]).reset_index(drop=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/llm_responses.csv")
    args = parser.parse_args()
    data = build()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
    print(f"Saved {len(data)} observations from {data.session_id.nunique()} matched prompts to {path}")
    print(data.LLM_name.value_counts().to_string())

if __name__ == "__main__":
    main()
