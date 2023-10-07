# Script to label player IDs based on bans

import requests
import os
import pandas as pd
import configparser

# Functions to save file


def save_csv(df, loc):

    os.makedirs(loc, exist_ok=True)

    df.to_csv(os.path.join(loc, 'labels.csv'), index=False)


def save_parquet(df, loc):

    os.makedirs(loc, exist_ok=True)

    df.to_parquet(os.path.join(loc, 'labels.parquet'), engine='pyarrow')

    print(f'Labels saved to {loc}!')


# Function to retrieve player ban history


def player_label(player_id, api_key):

    # player_id = 'bf460108-a8cb-42ff-9a0a-0f1e6a6858d9' # Test player ID
    base_url = 'https://open.faceit.com/data/v4/players/{player_id}/bans?offset=0&limit=20'
    headers = {
        "Authorization": f'Bearer {api_key}',
    }

    labels = []
    response = requests.get(base_url.format(
        player_id=player_id), headers=headers)

    if response.status_code == 200:

        labels.append(response.json())
    else:
        print(
            f'Error for player_id {player_id}: {response.status_code} - {response.text}')

    print(f"Retrieved {player_id}'s player history!")

    return labels

# Function to extract player IDs from txt file


def read_player_ids(input_path):

    df = pd.read_csv(input_path)

    return df


if __name__ == '__main__':

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config.get('API_KEYS', 'api_key_1')
    labels_input = config.get('PATHS', 'labels_input')
    output = config.get('PATHS', 'labels_output')

    data = read_player_ids(labels_input)

    output_df = []

    for player_id, steam_id in zip(data['player_ids'].tolist(), data['steam_ids'].tolist()):

        temp = []

        labels = player_label(player_id, api_key)

        if labels[0]['items']:
            temp.append([steam_id, 1])
        else:
            temp.append([steam_id, 0])

        output_df.extend(temp)

    df = pd.DataFrame(output_df, columns=['steamID', 'label'])

    # Typecast 'steamID' column to float and 'label' column to int
    df['steamID'] = df['steamID'].astype(float)
    df['label'] = df['label'].astype(int)

    df = df.sort_values(by=['steamID'], ascending=True)
    df = df.reset_index(drop=True)

    # save_csv(df, output)
    save_parquet(df, output)
