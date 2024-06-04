import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import numpy as np
import pandas as pd
import sklearn
from typing import List, Dict

# Import TensorFlow and TensorFlow Hub
import sklearn.metrics as sk_metrics
import sklearn.metrics.pairwise as sk_pairwise

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"


class TextEmbeddings:
    def __init__(self):
        # Load the universal sentence encoder multilingual module
        module_url = (
            "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
        )
        self.model = hub.load(module_url)

    def embed_text(self, text_list: List[str]) -> tf.Tensor:
        """Generate the embedding of a list of texts using the model.

        Parameters:
            text_list (List[str]): The list of texts to transform into embeddings.

        Returns:
            tf.Tensor: The embedding tensor produced by the model.
        """
        # Convert the text list into a string tensor
        return self.model(text_list)

    def similarity_text(self, text1: str, text2: str) -> float:
        """Compute the similarity between two texts using the dot product between their embeddings.

        Parameters:
            text1 (str): The first text to compare.
            text2 (str): The second text to compare.

        Returns:
            float: The similarity between the two texts, ranging from -1 to 1.
        """
        # Compute the embeddings of the two texts
        embedding1 = self.embed_text([text1])
        embedding2 = self.embed_text([text2])
        # Check if the embeddings are the same
        if np.array_equal(embedding1, embedding2):
            return 1.0

        sim = (
            1 - np.arccos(sk_pairwise.cosine_similarity(embedding1, embedding2)) / np.pi
        )
        # Return the similarity
        return sim.item()

    def similarity_matrix(self, text_list: List[str]) -> np.ndarray:
        """Compute the similarity matrix for a list of texts.

        Parameters:
            text_list (List[str]): The list of texts to compare.

        Returns:
            np.ndarray: The similarity matrix for the list of texts.
        """
        # Compute the embeddings of the texts
        embeddings = self.embed_text([text for text in text_list if text is not None])
        # Compute the similarity matrix
        return np.inner(embeddings, embeddings)

    def get_most_similar_texts(
        self, text: str, text_list: List[str], top_k: int = 5
    ) -> List[str]:
        """Get the most similar texts to a given text from a list of texts.

        Parameters:
            text (str): The text to compare.
            text_list (List[str]): The list of texts to compare against.
            top_k (int): The number of most similar texts to return.

        Returns:
            List[str]: The most similar texts to the given text.
        """
        # Compute the similarity between the given text and the list of texts
        similarities = [
            self.similarity_text(text, other_text) for other_text in text_list
        ]
        # Get the indices of the most similar texts
        most_similar_indices = np.argsort(similarities)[-top_k:][::-1]
        # Return the most similar texts
        return [text_list[i] for i in most_similar_indices]

    def get_clusters(
        self, text_list: List[str], threshold=None
    ) -> Dict[int, List[str]]:
        """Get the clusters of similar texts from a list of texts.

        Parameters:
            text_list (List[str]): The list of texts to cluster.
            threshold (float): The similarity threshold for clustering. If None, the 3rd quartile of the similarities will be used.

        Returns:
            Dict[int, List[str]]: The clusters of similar texts.
        """
        # Compute the similarity matrix for the list of texts
        sim_matrix = self.similarity_matrix(text_list)

        threshold = 0.4

        # Calculate the threshold if None
        if threshold is None:
            similarities = sim_matrix[np.triu_indices(len(text_list), k=1)]
            threshold = np.percentile(similarities, 90)

        # Get the indices of the similar texts
        similar_indices = np.argwhere(sim_matrix > threshold)

        # Initialize the clusters
        clusters = {}

        # Iterate over the similar indices
        for i, j in similar_indices:
            # Check if the indices are the same
            if i == j:
                continue
            # Check if the indices are already in a cluster
            if i in clusters:
                clusters[i].append(j)
            elif j in clusters:
                clusters[j].append(i)
            else:
                clusters[i] = [i]

        cleaned_clusters = {}
        for cluster_id, texts in clusters.items():
            cleaned_texts = list(set(texts))
            cleaned_clusters[cluster_id] = cleaned_texts

        return cleaned_clusters

    def is_subset(self, array1, array2):
        set1 = set(array1)
        set2 = set(array2)
        return set1.issubset(set2)

    def remove_subsets(self, df: pd.DataFrame, clusters):
        subsets_to_remove = []

        titles = df["title"].values.tolist()

        # Get the clusters of similar titles
        clusters = self.get_clusters(titles)

        # check if the clusters are subsets of each other
        for cluster_id, cluster in clusters.items():
            for other_cluster_id, other_cluster in clusters.items():
                if cluster_id != other_cluster_id:
                    if self.is_subset(cluster, other_cluster):
                        print(
                            f"Cluster {cluster_id} is a subset of Cluster {other_cluster_id}"
                        )

                        # save all the subsets to a list
                        subsets_to_remove.append((cluster_id, other_cluster_id))

        # remove the subsets
        for cluster_id, other_cluster_id in subsets_to_remove:
            if cluster_id in clusters:
                del clusters[cluster_id]

        return clusters
