import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("data/processed/driver_summary_2025_clean.csv")

norm_df = df.copy()

numeric_cols = norm_df.select_dtypes(include=["number"]).columns
numeric_cols = [col for col in numeric_cols if col != "cluster"]

inverse_cols = [
    "average_finish_position",
    "average_grid_position",
    "average_qualifying_position",
    "dnf_rate",
    "finish_position_std"
]

for col in numeric_cols:
    min_val = norm_df[col].min()
    max_val = norm_df[col].max()

    if max_val - min_val == 0:
        norm_df[col] = 0
    else:
        norm_df[col] = (norm_df[col] - min_val) / (max_val - min_val)


for col in inverse_cols:
    if col in norm_df.columns:
        norm_df[col] = 1 - norm_df[col]

norm_df.to_csv("data/processed/driver_summary_2025_normalised.csv", index=False)

print("Normalisation complete ✅")
print(norm_df.head())

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

sample = norm_df.head(10).round(2)

plt.figure(figsize=(18, 6))
plt.axis('off')

table = plt.table(
    cellText=sample.values,
    colLabels=sample.columns,
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(8)
table.auto_set_column_width(col=list(range(len(sample.columns))))

plt.savefig(output_dir / "normalised_dataset_table.png", bbox_inches='tight')

plt.show()

print("Figure saved to outputs/normalised_dataset_table.png ✅")