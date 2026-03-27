import logging
from foundry_client import get_prediction_claude

import pandas as pd



INPUT_FILE = "data/results/with_llm_predictions.csv"
PROMPT_PREFIX = "Classify Bug"
OUTPUT_FILE = "data/results/llm_predictions_all.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_user_prompt(text: str) -> str:
    cleaned_text = text.strip()
    return f"{PROMPT_PREFIX}\n{cleaned_text}"


df = pd.read_csv(INPUT_FILE)

result_df = df.copy()
result_df["label"] = ""
result_df["reasoning"] = ""
result_df["evidence"] = ""

total_rows = len(result_df)
logger.info("Loaded %s rows", total_rows)

for index, row in result_df.iterrows():
    text = row.get("text", "")
    user_prompt = build_user_prompt(text)

    logger.info("Processing row %s/%s", index + 1, total_rows)
    prediction = get_prediction_claude(user_prompt=user_prompt)

    result_df.at[index, "label_claude"] = prediction.label
    result_df.at[index, "reasoning_claude"] = prediction.reasoning
    result_df.at[index, "evidence_claude"] = prediction.evidence
    

result_df.to_csv(OUTPUT_FILE, index=False)

logger.info("Done. Output written to %s", OUTPUT_FILE)

