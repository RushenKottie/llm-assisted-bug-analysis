import pandas as pd
import yaml

INPUT_PARQUET = "data/processed/bugs.parquet"
INPUT_YAML = "repos.yaml"
OUTPUT_CSV = "data/results/golden_dataset.csv"

REPO_COLUMN = "repo"
PER_REPO_SIZE = 6
EXTRA_SIZE = 40
RANDOM_SEED = 42

df = pd.read_parquet(INPUT_PARQUET)

with open(INPUT_YAML, "r", encoding="utf-8") as f:
    repo_list = yaml.safe_load(f)

selected_parts = []

for repo_name in repo_list:
    repo_df = df[df[REPO_COLUMN] == repo_name]

    sampled_repo = repo_df.sample(
        n=PER_REPO_SIZE,
        random_state=RANDOM_SEED,
        replace=False,
    )

    selected_parts.append(sampled_repo)

    df = df.drop(sampled_repo.index)

extra_sample = df.sample(
    n=EXTRA_SIZE,
    random_state=RANDOM_SEED,
    replace=False,
)

selected_parts.append(extra_sample)

golden_df = pd.concat(selected_parts).sample(
    frac=1,
    random_state=RANDOM_SEED,
).reset_index(drop=True)

golden_df = golden_df.sort_values(by="repo").reset_index(drop=True)
golden_df.to_csv(OUTPUT_CSV, index=False)

print(f"Golden dataset created: {OUTPUT_CSV}")
print(f"Rows selected: {len(golden_df)}")