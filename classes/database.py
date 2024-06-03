import os
from pymongo import MongoClient
from typing import Dict, Any
import pandas as pd


class DatabaseHandler:
    """
    A class to handle MongoDB operations.

    Attributes
    ----------
    client : MongoClient
        The MongoDB client instance.
    db : Database
        The specific database instance.
    """

    def __init__(
        self,
        connection_string: str = os.environ["MONGODB_CONNECTION_STRING"],
        collection_name: str = "news",
    ):
        """
        Initializes the DatabaseHandler with a connection string.

        Parameters
        ----------
        connection_string : str
            The connection string for MongoDB.
        """
        self.client = MongoClient(connection_string)
        self.collection_name = collection_name
        self.db = self.client[collection_name]

    def get_collection(self, collection_name: str = None):
        """
        Retrieves a collection from the database.

        Parameters
        ----------
        collection_name : str
            The name of the collection to retrieve.

        Returns
        -------
        Collection
            The collection instance.
        """
        if not collection_name:
            collection_name = self.collection_name

        return self.db[collection_name]

    def delete_objects(self, collection_name: str = None) -> None:
        """
        Deletes all documents in the specified collection.

        Parameters
        ----------
        collection_name : str
            The name of the collection from which to delete documents.
        """
        if not collection_name:
            collection_name = self.collection_name

        collection = self.get_collection(collection_name)
        delete_result = collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} documents.")

    def substitute_sources(
        self, to_save_dict: Dict[str, Any], df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Substitutes source indices with the actual source data from a DataFrame.

        Parameters
        ----------
        to_save_dict : Dict[str, Any]
            The dictionary containing data with source indices.
        df : pd.DataFrame
            The DataFrame containing source data.

        Returns
        -------
        Dict[str, Any]
            The updated dictionary with actual source data.
        """
        for key, value in to_save_dict.items():
            sources = value.get("sources", [])
            new_sources = []
            for source in sources:
                if isinstance(source, dict):
                    new_sources.append(source)
                else:
                    new_sources.append(
                        {**df.iloc[int(source)].to_dict(), "id": float(source)}
                    )
            to_save_dict[key]["sources"] = new_sources
        return to_save_dict

    def clean_and_prepare_data(self, to_save_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans and prepares the data for insertion into MongoDB.

        Parameters
        ----------
        to_save_dict : Dict[str, Any]
            The dictionary containing data to be cleaned.

        Returns
        -------
        Dict[str, Any]
            The cleaned and prepared data.
        """
        to_save_dict = {str(k): v for k, v in to_save_dict.items()}
        for key in to_save_dict:
            to_save_dict[key]["similarity"] = [
                float(similarity) if similarity is not None else None
                for similarity in to_save_dict[key].get("similarity", [])
            ]
        to_save_dict = {k: v for k, v in to_save_dict.items() if k != "_id"}
        return to_save_dict

    def insert_data(
        self,
        data: Dict[str, Any],
        collection_name: str = None,
    ) -> None:
        """
        Inserts data into the specified collection.

        Parameters
        ----------
        collection_name : str
            The name of the collection to insert data into.
        data : Dict[str, Any]
            The data to insert.
        """
        if not collection_name:
            collection_name = self.collection_name

        collection = self.get_collection(collection_name)
        data_list = [{**{k: {}}, **v} for k, v in data.items()]
        collection.insert_many(data_list)
        print(f"Inserted {len(data_list)} documents.")
