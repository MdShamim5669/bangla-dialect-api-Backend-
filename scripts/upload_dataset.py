import os
import unicodedata
import random
import pandas as pd
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi

REGIONS = ["Pabna", "Noakhali", "Jashore", "Rangpur", "Mymensingh", "Barishal", "Chittagong"]

def clean_text(text):
    if pd.isna(text):
        return ""
    text = unicodedata.normalize("NFC", str(text))
    for ch in ["\u200B", "\u200C", "\u200D", "\uFEFF"]:
        text = text.replace(ch, "")
    return " ".join(text.strip().split())

from pathlib import Path

def main():
    candidate_paths = [
        Path(__file__).resolve().parent.parent / "Dataset" / "Master_sheet_Dataset.xlsx",
        Path(r"e:\Imon\backend\Dataset\Master_sheet_Dataset.xlsx"),
        Path(r"e:\Imon\Dataset\Master_sheet_Dataset.xlsx"),
    ]
    dataset_path = next((p for p in candidate_paths if p.exists()), candidate_paths[0])
    print(f"Reading dataset from: {dataset_path}")
    df_raw = pd.read_excel(dataset_path)

    print(f"Original shape: {df_raw.shape}")

    # Build long format pairs
    processed_rows = []
    for _, row in df_raw.iterrows():
        std_bangla = clean_text(row.get("Standard Bangla", ""))
        row_id = row.get("ID")
        if not std_bangla:
            continue

        for region in REGIONS:
            if region in row and pd.notna(row[region]):
                dialect_sent = clean_text(row[region])
                if dialect_sent:
                    prompt = f"translate {region} to Bangla: {dialect_sent}"
                    processed_rows.append({
                        "id": row_id,
                        "region": region,
                        "input_text": prompt,
                        "target_text": std_bangla,
                        "dialect_sentence": dialect_sent,
                    })

    df_long = pd.DataFrame(processed_rows)
    print(f"Total dialect-standard pairs generated: {len(df_long)}")

    # Deterministic ID-grouped split (80 / 10 / 10, seed=42)
    unique_ids = sorted(df_long["id"].unique().tolist())
    rng = random.Random(42)
    rng.shuffle(unique_ids)

    n = len(unique_ids)
    n_train = int(n * 0.80)
    n_val = int(n * 0.10)

    train_ids = set(unique_ids[:n_train])
    val_ids = set(unique_ids[n_train:n_train + n_val])
    test_ids = set(unique_ids[n_train + n_val:])

    train_df = df_long[df_long["id"].isin(train_ids)].copy().reset_index(drop=True)
    val_df = df_long[df_long["id"].isin(val_ids)].copy().reset_index(drop=True)
    test_df = df_long[df_long["id"].isin(test_ids)].copy().reset_index(drop=True)

    print(f"Split completed: Train={len(train_df)} pairs, Validation={len(val_df)} pairs, Test={len(test_df)} pairs")

    # Create Hugging Face DatasetDict
    hf_dataset = DatasetDict({
        "train": Dataset.from_pandas(train_df),
        "validation": Dataset.from_pandas(val_df),
        "test": Dataset.from_pandas(test_df),
    })

    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]
    repo_id = f"{username}/bangla-regional-dialect-dataset"

    print(f"\nUploading Dataset to Hugging Face: {repo_id} ...")
    hf_dataset.push_to_hub(repo_id, private=False)

    print(f"\n🎉 SUCCESS! Dataset is now live on Hugging Face at:")
    print(f"https://huggingface.co/datasets/{repo_id}")

if __name__ == "__main__":
    main()
