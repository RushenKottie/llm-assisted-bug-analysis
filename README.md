# AI Tools for Quality Maturity in Non-AI Projects: A Case Study of LLM-Based Bug Analysis

Nowadays, we see massive AI adoption in new projects, AI-native applications, or approaches designed for the near future. However, it is equally important to explore what AI can bring to teams that have been operating their applications for many years, working with legacy code and accumulated system knowledge, and where modern AI technologies can be applied from a quality engineering perspective.

## Hypothesis

Modern LLMs can support retrospective bug analysis by identifying the most efficient testing level for defect detection and providing transparent reasoning, acting as a second QA perspective to reduce bias and support decision-making in resource-constrained teams.

## Approach

For this project, I selected several open-source fintech repositories and collected their issues. From these, I randomly sampled 100 issues to form the initial (“golden”) dataset and labeled them according to my professional judgment of the most appropriate testing level. Next, the same issues were labeled by an LLM, and the results were compared. I then manually reviewed the model’s reasoning and updated some labels where the arguments were convincing. Finally, the evaluation metrics were recalculated, and the change rate was measured.

Technical stack: Python, Claude Sonnet 4.5, deployed on Microsoft Azure.

## Phase 0. Data preparation

Several open-source fintech repositories were selected for analysis. The fintech domain was chosen due to my professional experience in testing financial systems, which enabled faster identification of patterns and more reliable interpretation of defects. As these repositories were new to me, domain expertise helped ensure consistent labeling decisions.

The repositories were intentionally diverse in size, programming language, and specialization within the fintech domain. This variability was introduced to increase the robustness of the evaluation and reduce the risk of domain-specific bias aligning too closely with the model’s prior knowledge.

Issues were collected using the “bug” label, as this label is typically assigned by maintainers to confirmed defects. In addition, each issue was required to be linked to a closed pull request. This requirement ensured that only verified defects resulting in code changes were included, excluding cases where issues were initially labeled as bugs but later dismissed without modifications.

The golden dataset was constructed using a balanced sampling strategy. Due to significant differences in repository sizes, a purely random selection would have led to overrepresentation of larger repositories. Therefore, a baseline of 6 issues was selected from each repository, and the remaining 40 issues were sampled randomly to preserve proportional representation.

The data analyzed by both the human reviewer and the LLM included the issue title, description, and the first five comments, as these typically contain the most relevant diagnostic information. Preprocessing involved cleaning stack traces, logs, and formatting artifacts while preserving meaningful exception messages.

The labels assigned by me are stored in the column “label_human”.

In addition to the primary label, the dataset included an alternative column used to record alternative interpretations for certain cases. This column captured situations where the optimal testing level was not immediately obvious or where multiple testing strategies could be considered valid. These notes were preserved to support later review and comparison with the model’s reasoning.

## Phase 1. Tool validation

After the golden dataset was fully prepared and labeled, the next step was to evaluate whether an LLM could produce consistent and meaningful decisions on the same data.

Each issue from the dataset was processed sequentially using a fixed prompt. For every record, the model returned three outputs: the predicted label, a short reasoning explaining the decision, supporting evidence — a specific phrase extracted from the issue description that justified the classification

The exact system prompts used in this phase are available [here](https://github.com/RushenKottie/llm-assisted-bug-analysis/blob/6a7d59c6287225b309eb992f7621db1864072a10/inference/foundry_client.py#L7).

Before calculating the metrics, it is important to clarify the classification scheme used in this study. The analysis focused on three testing levels: service testing, end-to-end testing, manual testing.

While industry practice includes additional testing levels and more granular categorizations, the selected structure reflects a practical and commonly used abstraction in real engineering environments, where definitions often depend on team structure, domain constraints, and operational practices.

In this context, the testing levels were defined as follows:

- Service testing — the functionality can be validated in isolation, typically at the unit or service level, using controlled dependencies or mocks.
- End-to-end testing — multiple services or components must be validated together as a complete workflow within automated testing.
- Manual testing — automation is impractical, inefficient, or does not provide sufficient value compared to manual investigation.

Once the model predictions were collected, the next step was to calculate evaluation metrics in order to validate the tool.

The primary objective of this phase was to determine whether the model demonstrated a meaningful level of agreement with the human labeling. If the agreement had been too low, it would indicate that the model, the prompt, or the dataset required revision before continuing the experiment.

To make this assessment objective, a baseline threshold was defined. The baseline corresponds to the most frequent class in the dataset, in this case, the service testing category.

Since 69% of issues in the golden dataset belonged to this class, any useful model should demonstrate agreement exceeding this baseline level.

In addition to overall agreement, a full set of standard classification metrics was calculated to provide a more detailed and reliable evaluation of model performance. These included:

- Precision — the proportion of correct predictions among all predictions for a given label

- Recall — the proportion of correctly identified cases among all actual cases for a given label

- F1 score — the harmonic mean of precision and recall

- Macro F1 — the average F1 score across all labels, treating each class equally

- Confusion matrix — a detailed view of how predictions were distributed across true and predicted classes

- Overall agreement — the match across all labeles

- Agreement by label — the match for each label

These metrics made it possible to assess not only overall alignment, but also the quality of classification for each individual testing level and the balance of performance across classes.

In the initial evaluation, the baseline class (service testing) represented 69% of the dataset, while the overall agreement with the model reached 73%. This result exceeded the predefined threshold and indicated that the tool produced sufficiently consistent decisions to proceed to the next phase of the experiment.

Detailed metrics are provided below.

```text
Human label distribution (%):
END_TO_END: 15.00%
MANUAL: 16.00%
SERVICE: 69.00%
LLM label distribution (%):
END_TO_END: 5.00%
MANUAL: 14.00%
SERVICE: 81.00%

Agreement: 73.00%
Matched rows: 73 / 100

Correct predictions by label (%):

END_TO_END 2.74%
MANUAL 12.33%
SERVICE 84.93%

Confusion matrix:
                 PRED_END_TO_END  PRED_SERVICE  PRED_MANUAL
TRUE_END_TO_END                2            12            1
TRUE_SERVICE                   3            62            4
TRUE_MANUAL                    0             7            9

Per-label metrics:
END_TO_END:
  Precision: 0.4000
  Recall:    0.1333
  F1:        0.2000
  Support:   15
SERVICE:
  Precision: 0.7654
  Recall:    0.8986
  F1:        0.8267
  Support:   69
MANUAL:
  Precision: 0.6429
  Recall:    0.5625
  F1:        0.6000
  Support:   16

Macro F1: 0.5422
```

## Phase 2. QA Consilium

In this phase, I manually reviewed the model’s reasoning and the predicted label for each bug in the golden dataset and reassessed my original decisions.

For every case, I revisited the issue description and comments and evaluated whether the model’s explanation provided a more convincing interpretation of the defect and its optimal testing level.

During this review, most of the previously uncertain cases recorded in the alternative column were resolved in alignment with the model’s suggestions, which increased confidence in the consistency of the decision-making process.

After completing the re-evaluation, the updated labels were saved in a separate file named qa_concilium.csv, and the evaluation metrics were recalculated.

The observed improvements in the metrics were noticeable but gradual, indicating a realistic refinement of decisions rather than an artificial shift in results.

Following the review, the overall agreement increased to 88%.

The distribution of agreement across classes also became more balanced, with fewer extreme discrepancies between categories.

The final change rate — defined as the proportion of cases where the original human decision was revised after reviewing the model’s reasoning — reached 15%.

```text
Human label distribution (%):
END_TO_END: 11.00%
MANUAL: 16.00%
SERVICE: 73.00%
LLM label distribution (%):
END_TO_END: 5.00%
MANUAL: 14.00%
SERVICE: 81.00%

Agreement: 88.00%
Matched rows: 88 / 100

Correct predictions by label (%):

END_TO_END 5.68%
MANUAL 13.64%
SERVICE 80.68%

Confusion matrix:
                 PRED_END_TO_END  PRED_SERVICE  PRED_MANUAL
TRUE_END_TO_END                5             6            0
TRUE_SERVICE                   0            71            2
TRUE_MANUAL                    0             4           12

Per-label metrics:
END_TO_END:
  Precision: 1.0000
  Recall:    0.4545
  F1:        0.6250
  Support:   11
SERVICE:
  Precision: 0.8765
  Recall:    0.9726
  F1:        0.9221
  Support:   73
MANUAL:
  Precision: 0.8571
  Recall:    0.7500
  F1:        0.8000
  Support:   16

Macro F1: 0.7824
Change rate: 15.00%
```

## Conclusion

The resulting metrics, together with practical experience working with the model, suggest that an LLM can serve as a reliable second opinion when used with thoughtful design and well-prepared data.

An agreement level of 88% and a change rate of 15% indicate that the model demonstrates a meaningful level of practical professional knowledge about QA processes, testing practices, and the software development lifecycle.

Importantly, the model can provide perspectives that differ from long-established team assumptions, making the interaction feel similar to a professional discussion or brainstorming session rather than simple automation.

With proper data preparation and critical human oversight, LLMs can be effectively integrated into non-AI-native legacy projects that accumulate significant historical knowledge over time.

This approach can support quality maturity and help teams make more informed testing decisions — not only in test coverage planning, but potentially in other areas of engineering practice as well.
