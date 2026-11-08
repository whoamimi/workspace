# Map Charting Student Math Misunderstandings

## Overview

Kaggle competition: *MAP — Charting Student Math Misunderstandings*.
Predict the category and (where applicable) misconception label for a
student's short written explanation of a math answer.

#### Objective

Given a math question, the student's selected/typed answer, and their
free-text explanation, classify the response into one of:

- `True_Correct` — correct answer, correct reasoning.
- `False_Correct` — incorrect answer, but the explanation shows correct
  reasoning (likely a slip, not a misconception).
- `False_Misconception:<name>` — incorrect answer *and* the explanation
  reveals a specific, named misconception (see `const.json` for the full
  taxonomy, e.g. `Adding_across`, `Additive`, `Base_rate`, `Denominator-only_change`).
- `False_Neither` — incorrect, with no identifiable misconception pattern.

#### Data

Kaggle-provided train/test tables of `(QuestionText, MC_Answer,
StudentExplanation)` rows labeled with the category+misconception taxonomy
defined in [`const.json`](./const.json) (label → natural-language
definition, used both for reference and as LLM prompt context).

## Methods Implemented

Two-stage pipeline (`02_map_final.ipynb`, "Phi-Instruct + SentenceTransformer"):

1. **Model I — Correctness**: predicts whether the selected answer is
   correct (`True`/`False` half of the category label).
2. **Model II — Misconception detection**: conditional on an incorrect
   answer, assesses whether the explanation reveals a misconception, and
   which one, using sentence embeddings over the explanation text plus a
   Phi instruct-tuned LLM for reasoning-style classification
   (`01_map_model_building.ipynb` "Sentence Embeddings Treehouse").
3. Outputs are combined into the final `Category:Misconception` label.

## Results & Evaluation

**Not available**

## Extensions

- Finish the flagged improvements in `01_map_model_building.ipynb`
  (`child_role_play`, `add_contrast_responses`, `build_feature_pool` are
  stubs).
- Move data processors and the two-stage model classes into `src/` so
  `00_map_eda.ipynb` → `01_map_model_building.ipynb` →
  `02_map_final.ipynb` share code instead of redefining it per notebook.
- Add a `03_submission.ipynb` (or confirm `02_map_final.ipynb` is that
  step and rename it).
