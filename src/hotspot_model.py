import pandas as pd
from sklearn.cluster import KMeans
import os

def find_hotspots(data_path, n_clusters=3):
    df = pd.read_csv(data_path)
    coords = df[['latitude', 'longitude']]
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(coords)
    return df, kmeans.cluster_centers_

if __name__ == "__main__":
    # Get absolute path to dataset
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "crime_data.csv")

    df, centers = find_hotspots(data_path)
    print("Hotspot Centers:\n", centers)
