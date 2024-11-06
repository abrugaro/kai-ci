import json
import shutil
import sys
from datetime import datetime
import logging
import os
import pandas as pd

import git

import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.getenv("KAI_EVAL_PATH"))

logger = logging.getLogger(__name__)

# TODO (@abrugaro): Move utility functions to a different module

def download_kai_binary():
    kai_url = os.getenv("KAI_CLIENT_DOWNLOAD_URL")
    file_name = kai_url.replace("\\", "/").split("/").pop()
    response = requests.get(kai_url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
            logger.info(f"Downloaded {file_name}")
    else:
        logger.info(f"Failed to download the file. Status code: {response.status_code}")


def clone_repository(app_name, repository_url, branch):
    clone_dir = os.path.join("data", f"{app_name}_{branch}")
    git.Repo.clone_from(repository_url, clone_dir, branch=branch)
    logger.info(f"Repository cloned into 'data' with branch 'main'")


def zip_folder(app_name, path):
    current_time = datetime.now().strftime("%Y-%m-%d--%H-%M")

    zip_filename = f"{current_time}-{app_name}-report.zip"
    zip_path = os.path.join("data", zip_filename)

    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', path)

    logger.info(f"Repository compressed into {zip_path}")

def to_camel_case(original_str):
    components = original_str.split(' ')
    return components[0].lower() + ''.join(x.title() for x in components[1:])

# TODO (@abrugaro) The kai_eval_report.csv file should be generated by the kai-evaluator and placed automatically in the data folder, then remove from output folder
def kai_eval_report_to_json():
    df = pd.read_csv("output/kai_eval_report.csv")
    df.columns = [to_camel_case(col) for col in df.columns]
    json_data = json.loads(df.to_json(orient='records'))

    return json_data


def append_to_json_array(file_path, new_data):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    data.append(new_data)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


if __name__ == '__main__':

    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    logger.setLevel("DEBUG")

    test_app_name = os.getenv("APP_NAME")
    test_original_branch = os.getenv("ORIGINAL_BRANCH")
    test_repository_url = os.getenv("REPOSITORY_URL")

    shutil.rmtree('data')
    os.makedirs("data")

    # download_binary()
    clone_repository(test_app_name, test_repository_url, test_original_branch)

    json_report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kaiEvalData": kai_eval_report_to_json()
    }
    append_to_json_array('./output/report.json', json_report)

    zip_folder(test_app_name, os.path.join("data", f"{test_app_name}_{test_original_branch}"))