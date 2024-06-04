import requests
import pandas as pd
from typing import Dict


class Preprocessor:
    def __init__(self):
        pass

    def json_to_df(self, df: Dict[str, list]) -> pd.DataFrame:
        """
        Convert a dictionary containing rows data to a pandas DataFrame.

        Parameters
        ----------
        df : Dict[str, list]
            A dictionary containing rows data in the format {'rows': [row1, row2, ...]}.
            Each row should be a dictionary with keys representing columns.

        Returns
        -------
        pd.DataFrame
            A DataFrame constructed from the rows data.

        Example
        -------
        Consider a dictionary `data` in the format:
        data = {'rows': [{'col1': val1, 'col2': val2}, {'col1': val3, 'col2': val4}]}
        df = json_to_df(data)
        """
        rows_data = [row["row"] for row in df["rows"]]
        df = pd.DataFrame(rows_data)
        return df

    def fetch_rows(self, url: str, total_rows: int) -> pd.DataFrame:
        """
        Fetch rows of data from an API endpoint and compile them into a pandas DataFrame.

        Parameters
        ----------
        url : str
            The URL of the API endpoint to fetch data.
        total_rows : int
            The total number of rows to retrieve.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the compiled rows of data fetched from the API.

        Notes
        -----
        This function fetches rows of data from the provided API endpoint using the given URL. It iteratively
        retrieves data in chunks defined by 'rows_per_request' until 'total_rows' are fetched or an error occurs.
        The 'json_to_df' function is utilized to convert fetched JSON data to a DataFrame.
        """
        offset = 0
        rows_per_request = 100
        full_dataset = pd.DataFrame()

        while offset < total_rows:
            length = min(rows_per_request, total_rows - offset)
            api_url = f"{url}&offset={offset}&length={length}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                df_data = self.json_to_df(data)
                full_dataset = pd.concat([full_dataset, df_data], ignore_index=True)
                offset += length
            else:
                print(
                    f"Failed to fetch data from {api_url}. Status code: {response.status_code}"
                )
                break

        return full_dataset

    def df_openhermes_preproc(self, df_openhermes: pd.DataFrame) -> pd.DataFrame:
        df_openhermes = df_openhermes.drop("input", axis=1)

        df_openhermes = df_openhermes.iloc[:, ::-1]
        df_openhermes = df_openhermes.rename(
            columns={"instruction": "question", "output": "answer"}
        )

        return df_openhermes

    def df_slimOrca_preproc(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess a DataFrame containing 'conversations' data in a specific format.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame containing 'conversations' data.

        Returns
        -------
        pd.DataFrame
            A DataFrame with extracted 'question' and 'answer' values from the 'conversations' data.

        Notes
        -----
        This function preprocesses a DataFrame assumed to have a column 'conversations' containing a list of
        dictionaries. It extracts 'question' and 'answer' values from these dictionaries and creates a new
        DataFrame based on the extracted values.
        """
        extracted_values = []

        for index, row in df.iterrows():
            conversations = row["conversations"]
            row_values = []

            for conv in conversations:
                if "value" in conv:
                    row_values.append(conv["value"])

            if len(row_values) >= 3:
                extracted_values.append(
                    {"question": row_values[1], "answer": row_values[2]}
                )
            else:
                extracted_values.append({"question": None, "answer": None})

        return pd.DataFrame(extracted_values)
