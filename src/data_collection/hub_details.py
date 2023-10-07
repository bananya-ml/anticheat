# Script to retrive hub details from manually retrieved hub IDs stored in hub_details.json

import requests
import json
import os
import configparser


def get_hub_details(api_key, hub_id):
    base_url = "https://open.faceit.com/data/v4/hubs/"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    url = f"{base_url}{hub_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def write_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    print("File written: ", filename)


if __name__ == "__main__":

    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    faceit_api_key = config.get('API_KEYS', 'api_key_1')

    hub_id = "bfbb0657-8694-4278-8007-a7dc58f544af"

    hub_details = get_hub_details(faceit_api_key, hub_id)
    if hub_details:
        # Clean up the JSON response for better viewing
        formatted_json = json.dumps(hub_details, indent=2)

        output_path = r"C:\\Users\\bhatn\\Desktop\\anticheat\\src\\data_collection"
        # Create the directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        json_filename = os.path.join(output_path, 'hub_details.json')
        write_json_to_file(hub_details, json_filename)
