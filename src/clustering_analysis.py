import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


df = pd.read_csv("data/processed/driver_summary_2025.csv")


drivers = df["driver"]


numeric_df = df.select_dtypes(include=["number"]).copy()


if "races_entered" in numeric_df.columns:
    numeric_df = numeric_df.drop(columns=["races_entered"])

scaler = StandardScaler()
scaled_data = scaler.fit_transform(numeric_df)


inertia = []
k_values = range(1, 10)

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)

plt.figure()
plt.plot(k_values, inertia, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()

k = 3

kmeans = KMeans(n_clusters=k, random_state=42)
clusters = kmeans.fit_predict(scaled_data)

df["cluster"] = clusters

print(df[["driver", "cluster"]].sort_values("cluster"))

plt.figure()
plt.scatter(df["points_per_race"], df["average_finish_position"], c=clusters)

for i, name in enumerate(drivers):
    plt.text(df["points_per_race"][i], df["average_finish_position"][i], name, fontsize=8)

plt.xlabel("Points per Race")
plt.ylabel("Average Finish Position")
plt.title("Driver Clusters")
plt.show()