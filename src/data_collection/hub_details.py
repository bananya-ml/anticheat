<<<<<<< HEAD
version https://git-lfs.github.com/spec/v1
oid sha256:760c01d1df8630f0fde650f84de51090ca0b2d230c5b851803954b3ad228ed2b
size 2239
=======
# Script to retrive hub details from manually retrieved hub IDs stored in hub_details.json

import requests
import json
import os
import configparser


def get_hub_details(api_key, hub_id):
    '''
    Retrieves details about a Faceit hub using the Faceit Open Data API.

    Parameters:
    api_key (str): A valid Faceit API key.
    hub_id (str): The ID of the hub to retrieve details for.

    Returns:
    dict: A dictionary containing details about the hub, or None if the request failed.

    Raises:
    None.
    '''
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
    '''
    Write a JSON-serializable object to a file.

    Args:
        data: A JSON-serializable object to write to the file.
        filename: A string representing the path to the file to write to.

    Returns:
        None.
    '''
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    print("File written: ", filename)


if __name__ == "__main__":
    '''
    Main function that retrieves hub details using the Faceit Open Data API and writes the details to a JSON file.

    Parameters:
    None.

    Returns:
    None.

    Raises:
    None.
    '''
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
>>>>>>> e5036ff1c300019501499a9ba150bdee79f644b8
