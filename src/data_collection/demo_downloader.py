<<<<<<< HEAD
version https://git-lfs.github.com/spec/v1
oid sha256:ea1c5518b2d0a233e74d41cc4a845fb519a1135410e33b48189e6174b3a351d0
size 3429
=======
# Script to download demo (.dem) files from match IDs stored in match_ids.txt


import os
import re
import json
import requests
import configparser


def download_demo(url, save_path):
    '''
    Downloads a demo file from the specified URL and saves it to the specified file path.

    Args:
        url (str): The URL of the demo file to download.
        save_path (str): The file path to save the downloaded demo file to.

    Raises:
        requests.exceptions.RequestException: If an error occurs while downloading the demo file.

    Returns:
        None
    '''
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Demo downloaded successfully to: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the demo: {e}")


def read_match_ids(input_path):
    '''
    Reads a file and returns a list of match IDs found in the file.

    Args:
        input_path (str): The path to the input file.

    Returns:
        list: A list of match IDs found in the file.
    '''
    with open(input_path, 'r', encoding='utf-8') as file:
        data = file.read()
        pattern = r'"([a-zA-Z0-9-]+)"'

        return re.findall(pattern, data)


def get_match_details(api_key, match_id):
    '''
    Retrieves the details of a Faceit match with the given ID.

    Args:
        api_key (str): The Faceit API key to use for authentication.
        match_id (str): The ID of the match to retrieve.

    Returns:
        dict: A dictionary containing the details of the match, or None if the request failed.
    '''
    base_url = "https://open.faceit.com/data/v4/matches/"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    url = f"{base_url}{match_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def write_json_to_file(data, filename):
    '''
    Write JSON data to a file.

    Args:
        data (dict): The JSON data to write to the file.
        filename (str): The name of the file to write the data to.

    Returns:
        None
    '''
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    print("File written:", filename)


def main():
    '''
    Downloads demos from Faceit API using match IDs provided in a file.
    Saves demos to a specified directory.

    Args:
        None

    Returns:
        None
    '''
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    config = configparser.ConfigParser()
    config.read('config.ini')

    faceit_api_key = config.get('API_KEYS', 'api_key_1')
    downloader_input = config.get('PATHS', 'downloader_input')
    save_path_base = config.get('PATHS', 'save_path')

    match_ids = read_match_ids(downloader_input)
    dnum = 0

    for match_id in match_ids:
        dnum += 1
        details = get_match_details(faceit_api_key, match_id)
        urls = details.get('demo_url', [])

        for url in urls:
            save_path = os.path.join(save_path_base, f"demo{dnum}.dem.gz")
            download_demo(url, save_path)


if __name__ == "__main__":
    main()
>>>>>>> e5036ff1c300019501499a9ba150bdee79f644b8
