import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv("data/processed/driver_summary_2025_clean.csv")


numeric_df = df.select_dtypes(include=["number"])


corr_matrix = numeric_df.corr()


print(corr_matrix)

plt.figure(figsize=(10, 8))
plt.imshow(corr_matrix, aspect="auto")
plt.colorbar()

plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)

plt.title("Correlation Matrix of Driver Performance Variables")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "correlation_matrix.png")
plt.show()