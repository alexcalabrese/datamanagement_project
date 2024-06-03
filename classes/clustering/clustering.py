import pickle
from tqdm import tqdm
from classes.llm.groq import GroqChatClient
from classes.embeddings.utils import TextEmbeddings
from detoxify import Detoxify
import pandas as pd
import os


class ClusteringProcessor:
    """
    A class for processing clusters and generating summaries.

    Attributes:
        df (pandas.DataFrame): The dataframe containing the news data.
        summarize_clusters (dict): A dictionary to store summarized clusters.

    """

    def __init__(self, df, text_embeddings=TextEmbeddings()):
        """
        Initialize the ClusteringProcessor.

        Args:
            df (pandas.DataFrame): The dataframe containing the news data.

        """
        self.df = df
        self.backup_filename = "3_days_mixtral_summarize_clusters_dict"
        self.summarize_clusters = self.load_integrated_summarize_clusters_dict_backup()
        self.groq_client = GroqChatClient()
        self.text_embeddings = text_embeddings
        self.filename = "mixtral_integrated_df"

    def process_cluster(self, key, cluster):
        """
        Process a cluster and generate a summary.

        Args:
            key (int): The key of the cluster.
            cluster (list): The list of news indices in the cluster.

        """
        if self.summarize_clusters.get(key) is not None:
            tqdm.write("[SKIP] Skipping")
            return

        tags = self.df[["tags"]].iloc[key, 0]
        date = self.df[["date"]].iloc[key, 0]
        cluster_to_summarize = self.build_cluster_summary(cluster)

        if not cluster_to_summarize:
            return

        summary = self.summarize_and_analyze(cluster_to_summarize, cluster)
        self.summarize_clusters[key] = self.create_cluster_data(
            date, tags, cluster, summary
        )

        # self.save_integrated_summarize_clusters_dict_backup()

    def build_cluster_summary(self, cluster):
        """
        Build a summary for a cluster.

        Args:
            cluster (list): The list of news indices in the cluster.

        Returns:
            str: The summary text.

        """
        summary_text = ""
        for news in cluster:
            title = self.df[["title"]].iloc[news, 0]
            content = self.df[["content"]].iloc[news, 0]
            # tqdm.write(f"Title: {title}")
            summary_text += f"Title: {title} \n Content: {content}\n"
        if title is None or content is None:
            tqdm.write("[SKIP] Skipping NONE title or content")
            return None
        return summary_text

    def summarize_and_analyze(self, cluster_summary, cluster):
        """
        Summarize and analyze a cluster summary.

        Args:
            cluster_summary (str): The cluster summary text.

        Returns:
            tuple: A tuple containing the summary, similarity scores, and toxicity analysis.

        """
        summarize_prompt = f"""Considerati più titoli e contenuti degli articoli, riassumili e integrali in un unico testo.
        Input: {cluster_summary}
        Output Summary in italian: """

        output_json = self.groq_client.send_chat_message(summarize_prompt)
        summary = output_json if output_json else "Error: LLM call failed"

        # if summary == "Error: LLM call failed":
        #     summary = "Harmful content found in the news"
        #     return summary, [0 for _ in range(len(cluster))]
        # else:
        similarity_from_source = [
            (
                self.text_embeddings.similarity_text(
                    summary,
                    ""
                    + self.df[["title"]].iloc[news, 0]
                    + " "
                    + self.df[["content"]].iloc[news, 0],
                )
                if self.df[["title"]].iloc[news, 0]
                and self.df[["content"]].iloc[news, 0]
                else None
            )
            for news in cluster
        ]
        toxicity_analisys = Detoxify("multilingual").predict(summary)
        return summarize_prompt, summary, similarity_from_source, toxicity_analisys

    def create_cluster_data(self, date, tags, cluster, summary):
        """
        Create a dictionary containing cluster data.

        Args:
            date (str): The date of the cluster.
            tags (str): The tags of the cluster.
            cluster (list): The list of news indices in the cluster.
            summary (tuple): A tuple containing the summary, similarity scores, and toxicity analysis.

        Returns:
            dict: The cluster data dictionary.

        """
        (summarize_prompt, summary, similarity, toxicity_analysis) = summary

        return {
            "date": date,
            "tags": tags,
            "sources": cluster,
            "similarity": similarity,
            "question": summarize_prompt,
            "answer": summary,
            "toxicity": toxicity_analysis["toxicity"],
            "severe_toxicity": toxicity_analysis["severe_toxicity"],
            "obscene": toxicity_analysis["obscene"],
            "identity_attack": toxicity_analysis["identity_attack"],
            "insult": toxicity_analysis["insult"],
            "threat": toxicity_analysis["threat"],
            "sexual_explicit": toxicity_analysis["sexual_explicit"],
        }

    def get_summarized_clusters(self):
        """
        Get the summarized clusters.

        Returns:
            dict: The summarized clusters.

        """
        return self.summarize_clusters

    def load_integrated_df_backup(self):
        try:
            print(f"Loading backup: {self.filename}")
            pickle_file = os.path.join(os.getcwd(), "backups", f"{self.filename}.pkl")

            print(f"Searching backup in: {pickle_file}")
            print(f"Backup is existing: {os.path.exists(pickle_file)}")

            if os.path.exists(pickle_file):
                print(f"Backup found: {self.filename}")
                integrated_df = pd.read_pickle(pickle_file)

                print(f"Backup loaded: {self.filename}")

                return integrated_df
            else:
                print("[WARNING] Pickle file not found")
                integrated_df = pd.DataFrame()
                return integrated_df
        except Exception as e:
            print(f"An exception occurred: {str(e)}")

    def save_integrated_summarize_clusters_dict_backup(
        self,
    ):
        try:
            print(f"Saving backup: {self.backup_filename}")
            pickle_file = os.path.join(
                os.getcwd(), "backups", "multiple_days", f"{self.backup_filename}.pkl"
            )

            print(f"Saving backup in: {pickle_file}")

            with open(pickle_file, "wb") as f:
                pickle.dump(self.summarize_clusters, f)

            print(f"Backup saved: {self.backup_filename}")
        except Exception as e:
            print(f"An exception occurred: {str(e)}")

    def load_integrated_summarize_clusters_dict_backup(self):
        try:
            print(f"Loading backup: {self.backup_filename}")
            pickle_file = os.path.join(
                os.getcwd(), "backups", "multiple_days", f"{self.backup_filename}.pkl"
            )

            print(f"Searching backup in: {pickle_file}")
            print(f"Backup is existing: {os.path.exists(pickle_file)}")

            if os.path.exists(pickle_file):
                print(f"Backup found: {self.backup_filename}")
                with open(pickle_file, "rb") as f:
                    summarize_clusters = pickle.load(f)

                print(f"Backup loaded: {self.backup_filename}")
                return summarize_clusters
            else:
                print("[WARNING] Pickle file not found")
                summarize_clusters = {}
                return summarize_clusters
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
