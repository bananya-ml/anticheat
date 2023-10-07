# Script to extract match and player IDs from match_details.json stored in match_ids.txt and player_ids.csv

import os
import json
import configparser
import pandas as pd


def save_csv(df, loc):

    df.to_csv(loc, index=False, encoding='utf-8')
    print("File written:", loc)


def save_txt(ids, filename):
    with open(filename, 'w') as file:
        json.dump(ids, file)
    print("File written:", filename)


def extract_player_ids(data):
    player_ids = set()  # Use a set to store unique player IDs
    steam_ids = set()  # Use a set to store unique game player IDs

    if isinstance(data, list):
        for item in data:
            player_ids_set, steam_ids_set = extract_player_ids(item)
            player_ids.update(player_ids_set)
            steam_ids.update(steam_ids_set)
    elif isinstance(data, dict):
        if 'player_id' in data:
            player_ids.add(data['player_id'])
        if 'game_player_id' in data:
            steam_ids.add(data['game_player_id'])
        for _, value in data.items():
            player_ids_set, steam_ids_set = extract_player_ids(value)
            player_ids.update(player_ids_set)
            steam_ids.update(steam_ids_set)

    return list(player_ids), list(steam_ids)


def extract_finished_match_ids(hubs):

    match_ids = []

    for hub in hubs:
        for match in hub['items']:
            match_ids.append(match['match_id'])

    return match_ids


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    config = configparser.ConfigParser()
    config.read('config.ini')

    input_path = config.get('PATHS', 'match_ids_input')
    output_dir = config.get('PATHS', 'ids_output')

    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        match_ids = extract_finished_match_ids(data)
        player_ids, steam_ids = extract_player_ids(data)

        save_txt(match_ids, os.path.join(output_dir, 'match_ids.txt'))

        ids = {'player_ids': player_ids, 'steam_ids': steam_ids}
        df = pd.DataFrame(ids)
        save_csv(df, os.path.join(output_dir, 'player_ids.csv'))

    except Exception as e:
        print("Error:", str(e))
    else:
        print("IDs extracted and written to:", output_dir)


if __name__ == "__main__":
    main()
