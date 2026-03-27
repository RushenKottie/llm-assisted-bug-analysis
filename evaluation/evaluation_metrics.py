import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, f1_score

def calculate_metrics(file_path: str) -> float:
    df = pd.read_csv(file_path)

    predicted_label_human = df["label_human"].astype(str).str.upper()
    label_model = df["label_claude"].astype(str).str.upper()

    class_percentages_human = predicted_label_human.value_counts(normalize=True).mul(100).sort_index()
    class_percentages_model = label_model.value_counts(normalize=True).mul(100).sort_index()

    print("Human label distribution (%):")
    for class_name, percentage in class_percentages_human.items():
        print(f"{class_name}: {percentage:.2f}%")

    print("LLM label distribution (%):")
    for class_name, percentage in class_percentages_model.items():
        print(f"{class_name}: {percentage:.2f}%")

    matches = predicted_label_human == label_model
    match_percentage = matches.mean() * 100

    print()
    print(f"Agreement: {match_percentage:.2f}%")
    print(f"Matched rows: {matches.sum()} / {len(df)}")
    print("\nCorrect predictions by label (%):\n")

    matched_labels = predicted_label_human[matches]
    percentages = matched_labels.value_counts(normalize=True).mul(100).sort_index()

    for label, pct in percentages.items():
        print(f"{label} {pct:.2f}%")

    labels = ["END_TO_END", "SERVICE", "MANUAL"]

    print()
    print("Confusion matrix:")
    cm = confusion_matrix(predicted_label_human,label_model, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"TRUE_{label}" for label in labels], columns=[f"PRED_{label}" for label in labels])
    print(cm_df)

    precision, recall, f1, support = precision_recall_fscore_support(
        predicted_label_human,
        label_model,
        labels=labels,
        zero_division=0
    )

    print()
    print("Per-label metrics:")
    for i, label in enumerate(labels):
        print(f"{label}:")
        print(f"  Precision: {precision[i]:.4f}")
        print(f"  Recall:    {recall[i]:.4f}")
        print(f"  F1:        {f1[i]:.4f}")
        print(f"  Support:   {support[i]}")

    macro_f1 = f1_score(label_model, predicted_label_human, labels=labels, average="macro", zero_division=0)

    print()
    print(f"Macro F1: {macro_f1:.4f}")
    return match_percentage