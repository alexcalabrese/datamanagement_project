import re
from typing import Dict, Any
import os
import pandas as pd
import glob
from tqdm import tqdm
from datetime import date


class Evaluator:
    def __init__(self):
        self.df_to_evaluate = self.load_latest_translated_file()

    def evaluate(self, df_to_evaluate, gemini, evaluator):
        dimension = ["accuracy"]
        input = ""

        # get the 10% of the total rows
        ten_percent_rows = len(df_to_evaluate) // 100

        # Initialize a counter for the number of processed rows
        processed_rows = 0

        # Iterate over each row of the dataframe
        for index, row in tqdm(df_to_evaluate.iterrows()):
            if row["accuracy"] != -1:
                processed_rows += 1
                continue

            # Assign the values of the columns to the variables
            instruction = row["question"]
            response = row["answer"]

            eval_prompt = f"""System Prompt:
                We would like to request your feedback on the performance of AI assistant in response to the instruction
                and the given input displayed following.
                Instruction: {instruction}
                Input: {input}
                Response: {response}
                User Prompt:
                Please rate according to the {dimension[0]} of the response to the instruction and the input. Each assistant
                receives a score on a scale of 0 to 5, where a higher score indicates higher level of the {dimension[0]}. Please
                first output a single line containing the value indicating the scores. In the subsequent line, please provide a
                comprehensive explanation of your evaluation, avoiding any potential bias."""

            response_json = gemini.generate_content(eval_prompt)

            texts = gemini.get_text_from_response(response_json)

            result = evaluator.extract_score_and_description(texts[0])

            # Assign the score and description to the dataframe
            df_to_evaluate.at[index, "accuracy"] = result["score"]
            df_to_evaluate.at[index, "acc_explanation"] = result["description"]

            # Increment the counter for the number of processed rows
            processed_rows += 1

            # If the number of processed rows is a multiple of ten_percent_rows, save the DataFrame
            if processed_rows % ten_percent_rows == 0:
                # Get today's date in YYYYMMDD format
                today = date.today().strftime("%m%d")
                df_to_evaluate.to_pickle(f"{today}_{processed_rows}_evaluated.pkl")

        return df_to_evaluate

    def extract_score_and_description(self, string: str) -> Dict[int, str]:
        """
        Extracts the score and description from a given string using regex.

        Parameters
        ----------
        string (str): The string to be processed.

        Returns
        -------
        A dictionary with keys 'score' and 'description' and their corresponding values.
        """
        # cover the case of an empty string
        if type(string) != str or string == "":
            return {"score": -2, "description": "Empty string or not a string type"}

        try:
            # Split the string by newline characters
            lines = string.split("\n")

            # Use regex to match the score and description patterns
            score_pattern = r"(\d+)"

            # Find the score and description in the string
            score = re.search(score_pattern, string)
            description = "\n".join(lines[1:])
        except:
            return {"score": -2, "description": "Regex failed"}

        # Return the score and description as a dictionary
        return {"score": int(score.group()), "description": description}

    def parse_score_and_description(self, string: str) -> Dict[str, Any]:
        """
        Parses a string that contains a score and a description and returns a dict with the score as an int and the description as a str.

        Parameters
        ----------
        string (str): The string to parse.

        Returns
        -------
        result (Dict[str, Any]): A dict with two keys: "score" and "description". The value of "score" is an int that represents the score on the first line of the string. The value of "description" is a str that contains the remaining lines of the string.
        """
        # Split the string by newline characters
        lines = string.split("\n")

        # Initialize an empty dict to store the result
        result = {}

        # Get the first line of the string and extract the score as an int
        first_line = lines[0]
        score = int(first_line.split(":")[1].strip())
        result["score"] = score

        # Get the remaining lines of the string and join them as a description
        description = "\n".join(lines[1:])
        result["description"] = description

        # Return the result dict
        return result

    def load_latest_translated_file(self):
        try:
            path = os.path.join(os.getcwd(), "backups", "finetuning", "*_evaluated.pkl")

            file_list = glob.glob(path)

            if len(file_list) == 0:
                return pd.DataFrame()

            # Sort the file list by name
            file_list.sort()

            # Get the last file in the sorted list
            latest_file = file_list[-1]

            print(f"Searching backup in: {file_list}")

            if len(file_list) > 0:
                print(f"Backup found: {latest_file}")

                df_to_evaluate = pd.read_pickle(latest_file)

                print(f"Backup loaded: {latest_file}")
                return df_to_evaluate
            else:
                print("[WARNING] Pickle file not found")
                return pd.DataFrame()
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
