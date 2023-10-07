# Script to download demo (.dem) files from match IDs stored in match_ids.txt


import os
import re
import json
import requests
import configparser


def download_demo(url, save_path):
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
    with open(input_path, 'r', encoding='utf-8') as file:
        data = file.read()
        pattern = r'"([a-zA-Z0-9-]+)"'

        return re.findall(pattern, data)


def get_match_details(api_key, match_id):
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
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    print("File written:", filename)


def main():
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
