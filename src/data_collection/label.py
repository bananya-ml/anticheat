<<<<<<< HEAD
version https://git-lfs.github.com/spec/v1
oid sha256:7b727e100eee9be467403a94cac5511d0700cd3410a2221b57a3c329656870a0
size 4108
=======
import requests
import os
import pandas as pd
import configparser

# Functions to save file


def save_csv(df, loc):
    '''
    Saves a pandas DataFrame as a CSV file in the specified location.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be saved.
    loc (str): The directory where the CSV file will be saved.

    Returns:
    None
    '''
    os.makedirs(loc, exist_ok=True)

    df.to_csv(os.path.join(loc, 'labels.csv'), index=False)


def save_parquet(df, loc):
    '''
    Saves a pandas DataFrame as a Parquet file in the specified location.

    Parameters:
    df (pandas.DataFrame): The DataFrame to save.
    loc (str): The directory where the Parquet file will be saved.

    Returns:
    None
    '''
    os.makedirs(loc, exist_ok=True)

    df.to_parquet(os.path.join(loc, 'labels.parquet'), engine='pyarrow')

    print(f'Labels saved to {loc}!')


# Function to retrieve player ban history


def player_label(player_id, api_key):
    '''
    Retrieves the ban history of a Faceit player with the given ID.

    Args:
        player_id (str): The ID of the player to retrieve the ban history for.
        api_key (str): The API key to use for authentication.

    Returns:
        list: A list containing the ban history of the player, as returned by the Faceit API.

    Raises:
        None.
    '''
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
    '''
    Reads a CSV file containing player IDs and returns a pandas DataFrame.

    Args:
        input_path (str): Path to the input CSV file.

    Returns:
        pandas.DataFrame: A DataFrame containing the player IDs.
    '''
    df = pd.read_csv(input_path)

    return df


def main():
    '''
    Collects player labels using the Steam API and saves them to a file.

    Reads player IDs from a CSV file specified in the 'labels_input' field of the
    'PATHS' section in the 'config.ini' file. For each player ID, retrieves their
    labels using the Steam API key specified in the 'api_key_1' field of the
    'API_KEYS' section in the 'config.ini' file. If the player has at least one
    label, assigns a label of 1 to their Steam ID, otherwise assigns a label of 0.

    Saves the resulting DataFrame to a file specified in the 'labels_output' field
    of the 'PATHS' section in the 'config.ini' file, in the Parquet format.

    Returns:
        None
    '''
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


if __name__ == "__main__":
    main()
>>>>>>> e5036ff1c300019501499a9ba150bdee79f644b8
