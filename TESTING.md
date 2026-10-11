# Testing data and CNN/LSTM evaluation

The source is the public [WildBench V2 Model Outputs](https://huggingface.co/datasets/allenai/WildBench-V2-Model-Outputs) dataset. The builder selects one GPT, one Claude and one Gemini version, retains only matching prompt/session IDs shared by all three, and saves records with `LLM_name`, `LLM_Input`, and `LLM_output`. No synthetic records are presented as real model outputs.

Run from the repository root:

```bash
pip install -r requirements.txt
python build_wildbench_data.py --output generated/llm_responses.csv
python prepare_test_data.py --input generated/llm_responses.csv --output generated/splits
python -m unittest discover -s tests -v
python evaluate_models.py --data-dir generated/splits --output results --epochs 8
```

**Important:** The repository already contains a regular file named `data`, so all generated files belong under `generated/`. Do not try to create a `data/` directory.

The split groups identical prompts together: approximately 70% train, 10% validation and 20% test. Both CNN and LSTM are trained on prompt-only, response-only and combined input. Validation data controls early stopping; only held-out test data is used to report performance. Each experiment writes a metrics JSON and a predictions CSV; `results/comparison.csv` compares accuracy and macro-F1 across experiments.

On GitHub, open **Actions → CMPSC 448 WildBench Evaluation**. If a run succeeds, download `cmpsc448-test-results` under that run's **Artifacts** section to obtain generated data, splits, and evaluation results. The workflow does not automatically commit generated data or metrics to the repository.

A prompt-only result near one-third accuracy is expected when the three model families answer the same prompts and the split prevents prompt overlap.
