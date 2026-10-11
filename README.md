# Who Wrote It? Identifying LLMs from Their Responses

CMPSC 448 midterm project at Penn State. This project tests whether a CNN or LSTM can identify which language model produced a text response. It also checks whether including the original prompt changes classification performance.

The initial examples in [`responses/`](responses/) compare NBA players and teams. The main experiments use a larger, publicly available dataset of general-purpose responses from GPT, Claude, and Gemini. **The reported accuracy figures come from that WildBench dataset, not the NBA examples.**

[Read the project report (PDF)](CMPSC_448_Midterm_Report.pdf)

## Dataset

Source: [WildBench V2 Model Outputs](https://huggingface.co/datasets/allenai/WildBench-V2-Model-Outputs)

The dataset builder selects one version of each model family:

| Label | Model version | Responses |
| --- | --- | ---: |
| GPT | `gpt-4o-2024-05-13` | 979 |
| Claude | `claude-3-sonnet-20240229` | 979 |
| Gemini | `gemini-1.5-pro` | 979 |
| **Total** | | **2,937** |

Only sessions with matching prompts and usable outputs from all three families are retained. Each record includes `LLM_name`, `LLM_Input`, and `LLM_output`. There are 979 matched prompts. Responses to the same prompt are kept together during splitting to prevent prompt overlap between training and testing.

| Split | Responses | Distinct prompts |
| --- | ---: | ---: |
| Train | 2,055 | 685 |
| Validation | 294 | 98 |
| Test | 588 | 196 |

## Models and experiments

Two TensorFlow/Keras models are trained using the same data:

- **CNN:** TextVectorization, embedding, Conv1D, global max pooling, dropout, and a softmax classifier.
- **LSTM:** TextVectorization, embedding, LSTM layer, dropout, and a softmax classifier.

Each model is tested with three inputs: **prompt only**, **response only**, and **prompt + response**. Training uses Adam, sparse categorical cross-entropy, early stopping on validation loss, and up to eight epochs in the recorded GitHub Actions run. The test set is reserved for final evaluation.

## Results

Results from the successful [GitHub Actions evaluation](https://github.com/afolamie/CMPSC-448-Midterm-1-NBA-Stats-1947-present-/actions/runs/38167743136), measured on 588 held-out responses:

| Model | Input | Test accuracy | Macro F1 |
| --- | --- | ---: | ---: |
| CNN | Prompt only | 33.3% | 30.7% |
| LSTM | Prompt only | 33.3% | 17.9% |
| **CNN** | **Response only** | **67.7%** | **67.5%** |
| LSTM | Response only | 42.9% | 41.0% |
| CNN | Prompt + response | 64.5% | 64.5% |
| LSTM | Prompt + response | 36.6% | 26.9% |

The response-only CNN performed best. Adding the prompt did not improve either architecture in this run. Prompt-only accuracy was 33.3%, consistent with chance-level prediction in a balanced, three-class dataset where the same prompts were used for all three models. These results apply to the selected WildBench model versions and this train/test split; they are not estimates for every model or topic.

The [report](CMPSC_448_Midterm_Report.pdf) includes confusion matrices, additional analysis of response length and formatting, limitations, and lessons learned.

## Run the project

Use Python 3.11 and run these commands from the repository root:

```bash
pip install -r requirements.txt
python build_wildbench_data.py --output generated/llm_responses.csv
python prepare_test_data.py --input generated/llm_responses.csv --output generated/splits
python -m unittest discover -s tests -v
python evaluate_models.py --data-dir generated/splits --output results --epochs 8
```

**Note:** `data` is already a file in this repository, so the generated CSVs and splits go under `generated/`, not `data/`. Downloading the public dataset requires internet access.

The evaluation creates `results/comparison.csv`, per-experiment metric JSON files, and prediction CSVs. GitHub Actions also saves the generated dataset, splits, and results as the `cmpsc448-test-results` artifact on the [successful workflow run](https://github.com/afolamie/CMPSC-448-Midterm-1-NBA-Stats-1947-present-/actions/runs/38167743136). Generated outputs are **not** automatically committed to this repository.

See [`TESTING.md`](TESTING.md) for the evaluation instructions.

## Repository files

- [`CMPSC_448_Midterm_Report.pdf`](CMPSC_448_Midterm_Report.pdf): written report and figures
- [`build_wildbench_data.py`](build_wildbench_data.py): collect and match public model outputs
- [`prepare_test_data.py`](prepare_test_data.py): split examples by prompt
- [`evaluate_models.py`](evaluate_models.py): CNN/LSTM training and evaluation
- [`tests/test_pipeline.py`](tests/test_pipeline.py): data-processing checks
- [`requirements.txt`](requirements.txt): Python dependencies
- [`responses/`](responses/): initial NBA comparison prompts and responses
- [`.github/workflows/wildbench-evaluation.yml`](.github/workflows/wildbench-evaluation.yml): reproducible GitHub Actions experiment
