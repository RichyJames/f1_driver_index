import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

os.makedirs("outputs", exist_ok=True)

df = pd.read_csv("data/processed/driver_summary_2025.csv")

driver_names = df["driver"]


numeric_df = df.select_dtypes(include=["number"]).copy()

if "races_entered" in numeric_df.columns:
    numeric_df = numeric_df.drop(columns=["races_entered"])


scaler = StandardScaler()
scaled_data = scaler.fit_transform(numeric_df)


pca = PCA()
principal_components = pca.fit_transform(scaled_data)


explained_variance = pca.explained_variance_ratio_
cumulative_variance = explained_variance.cumsum()

variance_df = pd.DataFrame({
    "Principal Component": [f"PC{i+1}" for i in range(len(explained_variance))],
    "Explained Variance Ratio": explained_variance,
    "Cumulative Variance": cumulative_variance
})

print("\nPCA Explained Variance:")
print(variance_df)

variance_df.to_csv("outputs/pca_explained_variance.csv", index=False)


plt.figure(figsize=(8, 5))
plt.plot(range(1, len(explained_variance) + 1), explained_variance, marker="o")
plt.xlabel("Principal Component")
plt.ylabel("Explained Variance Ratio")
plt.title("Scree Plot")
plt.xticks(range(1, len(explained_variance) + 1))
plt.tight_layout()
plt.savefig("outputs/pca_scree_plot.png")
plt.show()


plt.figure(figsize=(8, 5))
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker="o")
plt.xlabel("Principal Component")
plt.ylabel("Cumulative Explained Variance")
plt.title("Cumulative Explained Variance")
plt.xticks(range(1, len(cumulative_variance) + 1))
plt.tight_layout()
plt.savefig("outputs/pca_cumulative_variance.png")
plt.show()


loadings = pd.DataFrame(
    pca.components_.T,
    columns=[f"PC{i+1}" for i in range(len(numeric_df.columns))],
    index=numeric_df.columns
)

print("\nPCA Loadings:")
print(loadings)

loadings.to_csv("outputs/pca_loadings.csv")


pca_2 = PCA(n_components=2)
pc_scores = pca_2.fit_transform(scaled_data)

pca_plot_df = pd.DataFrame({
    "driver": driver_names,
    "PC1": pc_scores[:, 0],
    "PC2": pc_scores[:, 1]
})

plt.figure(figsize=(10, 7))
plt.scatter(pca_plot_df["PC1"], pca_plot_df["PC2"])

for _, row in pca_plot_df.iterrows():
    plt.text(row["PC1"], row["PC2"], row["driver"], fontsize=8)

plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("PCA Scatter Plot of Drivers")
plt.tight_layout()
plt.savefig("outputs/pca_driver_scatter.png")
plt.show()