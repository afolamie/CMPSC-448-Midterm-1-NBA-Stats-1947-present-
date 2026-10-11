# CMPSC 448 testing code

The dataset must contain three CSV columns: `LLM_name`, `LLM_Input`, and `LLM_output`.
Collect actual GPT, Claude, and Gemini answers into `data/llm_responses.csv`.

Run from the repository root:

```bash
pip install -r requirements.txt
python prepare_test_data.py --input data/llm_responses.csv
python -m unittest discover -s tests -v
python evaluate_models.py --data-dir data/splits --output results
```

The data split groups all responses to the same prompt together, so a prompt cannot occur in multiple splits. The target proportions are approximately 70% training, 10% validation, and 20% test, by prompt group. The CNN and LSTM are each run against prompt-only, response-only, and combined inputs. Results are saved in `results/`.

The synthetic observations in `tests/test_pipeline.py` test the processing code; they are not substitute LLM responses or benchmark results. No actual model accuracy can be reported until the real CSV is supplied and the models are run.
