<<<<<<< HEAD
version https://git-lfs.github.com/spec/v1
oid sha256:3b8cde6f7df1a4c3c740175dd1b11152a73e11d1caec0fe0745bd28621d6639b
size 4137
=======
# Script to extract match and player IDs from match_details.json stored in match_ids.txt and player_ids.csv

import os
import json
import configparser
import pandas as pd


def save_csv(df, loc):
    """
    Save a pandas DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to be saved.
        loc (str): The file path to save the CSV file to.

    Returns:
        None
    """
    df.to_csv(loc, index=False, encoding='utf-8')
    print("File written:", loc)


def save_txt(ids, filename):
    '''
    Save a list of IDs to a text file in JSON format.

    Args:
        ids (list): A list of IDs to save.
        filename (str): The name of the file to save the IDs to.

    Returns:
        None
    '''
    with open(filename, 'w') as file:
        json.dump(ids, file)
    print("File written:", filename)


def extract_player_ids(data):
    '''
    Extracts unique player IDs and game player IDs from a nested dictionary or list of dictionaries.

    Args:
        data (list or dict): The data to extract player IDs from.

    Returns:
        tuple: A tuple containing two lists - the first list contains unique player IDs, and the second list contains unique game player IDs.
    '''
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
    '''
    Extracts the match IDs of all finished matches from a list of hubs.

    Args:
        hubs (list): A list of hub dictionaries, each containing an 'items' key
            with a list of match dictionaries. Each match dictionary should have
            a 'match_id' key.

    Returns:
        list: A list of match IDs (strings) of all finished matches in the hubs.
    '''
    match_ids = []

    for hub in hubs:
        for match in hub['items']:
            match_ids.append(match['match_id'])

    return match_ids


def main():
    '''
    Extracts match, player and steam IDs from a JSON file and saves them to text and CSV files.

    Reads the input file path and output directory from a configuration file named 'config.ini'.
    The input file should contain a list of dictionaries, each representing a match and containing
    information about the players and their IDs. The function extracts the IDs from the matches and
    saves them to two files: 'match_ids.txt' (containing the match IDs) and 'player_ids.csv'
    (containing the player and steam IDs).

    Raises:
        Any exception that occurs during the execution of the function.

    Returns:
        None.
    '''
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
>>>>>>> e5036ff1c300019501499a9ba150bdee79f644b8
