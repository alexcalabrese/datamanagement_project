import glob
import os
import pandas as pd
import time
from deep_translator import GoogleTranslator
import textwrap
from datetime import date


class Translator:
    def __init__(self):
        self.df_translated = self.load_latest_translated_file()

    def translate(self, df_to_translate):
        if not self.df_translated.empty:
            return self.df_translated

        languages = ["es", "fr", "it"]

        # Calculate the number of rows that represent 10% of the total
        ten_percent_rows = len(df_to_translate) // 50

        # Initialize a counter for the number of processed rows
        processed_rows = 0

        # Get the total number of iterations
        total_iterations = len(df_to_translate)

        # Iterate over each row of the dataframe
        for index, row in df_to_translate.iterrows():
            # skip the row if there is a none value
            if row["question"] is None or row["answer"] is None:
                print(
                    "[INFO] Skipping row {} because it has a None value".format(index)
                )
                processed_rows += 1
                continue

            if row["language"] != "en":
                print(
                    "[INFO] Skipping row {} because it is not in English".format(index)
                )
                processed_rows += 1
                continue

            # choose the language by % 3
            language = languages[index % 3]

            # check if the answer contains a code block
            if row["answer"] and row["question"] and "```" not in row["answer"]:
                # If the question is longer than 4500 characters, split it into parts
                if len(row["question"]) > 4500:
                    parts = textwrap.wrap(row["question"], 4500)
                    translated_parts = [
                        GoogleTranslator(source="en", target=language).translate(part)
                        for part in parts
                    ]
                    df_to_translate.loc[index, "question"] = " ".join(translated_parts)
                else:
                    df_to_translate.loc[index, "question"] = GoogleTranslator(
                        source="en", target=language
                    ).translate(row["question"])

                # If the answer is longer than 4500 characters, split it into parts
                if len(row["answer"]) > 4500:
                    parts = textwrap.wrap(row["answer"], 4500)
                    translated_parts = [
                        GoogleTranslator(source="en", target=language).translate(part)
                        for part in parts
                    ]
                    df_to_translate.loc[index, "answer"] = " ".join(translated_parts)
                else:
                    df_to_translate.loc[index, "answer"] = GoogleTranslator(
                        source="en", target=language
                    ).translate(row["answer"])

                # print the question and answer
                print("[PROGRESS] {}/{}".format(processed_rows, total_iterations))
                print("[LOG] Index: {}".format(index))
                print(" - Question: {}".format(row["question"][:25]))
                print(" - Answer: {}".format(row["answer"][:25]))
                print(" From {} -> {}".format(row["language"], language))
            else:
                print(
                    "[INFO] Skipping row {} because it does contain a code block".format(
                        index
                    )
                )

            df_to_translate.loc[index, "language"] = language

            # Increment the counter for the number of processed rows
            processed_rows += 1

            # If the number of processed rows is a multiple of ten_percent_rows, save the DataFrame
            if processed_rows % ten_percent_rows == 0:
                today = date.today().strftime("%m%d")
                df_to_translate.to_pickle(f"{today}_{processed_rows}_translated.pkl")
                print("[INFO] Saved DataFrame to {}.pkl".format(today))

            time.sleep(0.1)

        return df_to_translate

    def load_latest_translated_file(self):
        try:
            path = os.path.join(
                os.getcwd(), "backups", "finetuning", "*_translated.pkl"
            )

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

                df_translated = pd.read_pickle(latest_file)

                print(f"Backup loaded: {latest_file}")
                return df_translated
            else:
                print("[WARNING] Pickle file not found")
                return pd.DataFrame()
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
