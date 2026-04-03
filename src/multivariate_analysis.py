import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/driver_summary_2025.csv")


numeric_df = df.select_dtypes(include=["number"])


corr_matrix = numeric_df.corr()


print(corr_matrix)

# Plot heatmap
plt.figure(figsize=(10, 8))
plt.imshow(corr_matrix, aspect='auto')
plt.colorbar()

plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)

plt.title("Correlation Matrix of Driver Performance Variables")
plt.tight_layout()
plt.show()