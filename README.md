# Creating Synthetic Datasets for LLM Fine-Tuning: Multilingual and News Domains

This project is a comprehensive data management system that includes various functionalities such as data scraping, clustering, and fine-tuning of language models like Llama 3 and Gemma.

![Alt text](/img/readme_image.png "Optional title")

## Structure

The project is structured as follows:

- `dataset_multilingual_finetuning.ipynb`: This Jupyter notebook is used for creating a multilingual dataset for fine-tuning.

- `dataset_news.ipynb`: This Jupyter notebook is used for creating a news dataset.

- `requirements.txt`: This file lists the Python dependencies required by the project.

- `classes/`: This directory contains the main classes used in the project, including:
  - `clustering/`: Contains the `ClusteringProcessor` class for processing clusters and generating summaries.
  - `database.py`: Contains the `DatabaseHandler` class for handling database operations.
  - `embeddings/`: Contains the `TextEmbeddings` class for handling text embeddings.
  - `llm/`: Contains the `assistant_message` and `concat_list_elements` functions for language model operations.
  - `scrapers/`: Contains the `link_element` function for scraping data from various sources.

- `finetuning/`: This directory contains Jupyter notebooks for fine-tuning language models.

- `metrics/`: This directory contains Jupyter notebooks for calculating and visualizing various metrics.

- `backups/`: This directory contains backup files for the project.

- `img/`: This directory contains image files used in the project.

## Setup

To set up the project, you need to install the required dependencies listed in the `requirements.txt` file. You can do this by running the following command in your terminal:

```sh
pip install -r requirements.txt
```

Then, you can run the Jupyter notebooks in the finetuning/ and metrics/ directories to fine-tune the language models and calculate the metrics, respectively.

## Data
The project uses various datasets, which are processed and stored in the backups/ directory. The datasets are used for fine-tuning the language models and for clustering.

## Contributions
Contributions to this project are welcome. Please feel free to open an issue or submit