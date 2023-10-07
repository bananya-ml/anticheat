# Script to retrieve hub matches from hub IDs in hub_details.json, stored in match_details.json


import requests
import json
import os
import configparser


def read_json_file(input_path):
    hub_ids = []  # Initialize the list here
    with open(input_path, 'r', encoding='utf-8') as file:
        for hub in file:
            data = json.loads(hub)
            hub_ids.append(data['hub_id'])
    return hub_ids


def get_hub_matches(api_key, hub_id_list):
    base_url = "https://open.faceit.com/data/v4/hubs/{hub_id}/matches?type=past&offset=0&limit=20"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    results = []

    for hub_id in hub_id_list:
        url = base_url.format(hub_id=hub_id)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            results.append(response.json())
        else:
            print(
                f"Error for hub_id {hub_id}: {response.status_code} - {response.text}")
    return results


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
    input_path = config.get('PATHS', 'hub_matches_input')
    output_path = config.get('PATHS', 'hub_matches_output')

    # Create the directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    hub_data = read_json_file(input_path)
    match_details = get_hub_matches(faceit_api_key, hub_data)

    if match_details:
        json_filename = os.path.join(output_path, 'match_details.json')
        write_json_to_file(match_details, json_filename)


if __name__ == "__main__":
    main()
