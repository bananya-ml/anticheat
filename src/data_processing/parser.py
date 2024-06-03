import os
import json
import configparser
import gzip
import pandas as pd
from awpy import DemoParser


def write_to_json(data, filename):
    '''
    Write the given data to a JSON file with the given filename.

    Args:
        data: The data to be written to the file.
        filename: The name of the file to write the data to.

    Returns:
        None
    '''
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


def process_demo(demo_filename, dnum, csv_dir, json_dir, in_path):
    '''
    Parse a demo file and save its data as CSV files and an info file.

    Args:
        demo_filename (str): The name of the demo file to parse.
        dnum (int): The number of the demo, used to create a unique ID.
        csv_dir (str): The directory where to save the CSV files.
        json_dir (str): The directory where to save the JSON files.
        in_path (str): The path where to find the demo file.

    Returns:
        None
    '''
    file_loc = os.path.join(in_path, demo_filename)
    demo_id = f"match{dnum}"

    # Create a directory for the current demo
    demo_dir = os.path.join(csv_dir, demo_id)
    os.makedirs(demo_dir, exist_ok=True)

    demo_parser = DemoParser(
        demofile=file_loc, demo_id=demo_id, parse_rate=128, outpath=json_dir)
    print(f"Parsing demo {demo_filename} ({demo_id})")

    data = demo_parser.parse(return_type='df')

    for df_name, df in data.items():
        if isinstance(df, pd.core.frame.DataFrame):
            csv_filename = os.path.join(demo_dir, f"{df_name}.csv")
            df.to_csv(csv_filename, index=False)

    # Create a dataframe with the remaining items from the 'data' dictionary
    remaining_data = {k: v for k, v in data.items(
    ) if not isinstance(v, pd.core.frame.DataFrame)}
    info_df = pd.DataFrame.from_dict(
        remaining_data, orient='index', columns=['Value'])
    info_csv_filename = os.path.join(demo_dir, f"info{dnum}.csv")
    info_df.to_csv(info_csv_filename, index=True, header=True)


def main():
    '''
    Extracts data from demo files in a given directory and saves it as CSV and JSON files.

    Reads configuration from a file named 'config.ini' in the same directory as this script.
    The configuration file should contain the following sections and options:

    [PATHS]
    csv_dir, json_dir, demo_path

    The 'csv_dir' and 'json_dir' directories will be created if they don't exist.
    The 'demo_path' directory should contain one or more '.dem' or '.dem.gz' files.

    For each demo file found in 'demo_path', the function calls the 'process_demo' function
    to extract data and save it as CSV and JSON files in the 'csv_dir' and 'json_dir' directories.

    If an error occurs while processing a demo file, the function prints an error message and
    continues with the next demo file.

    Returns:
    None
    '''
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # Read configuration from config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    csv_dir = config.get('PATHS', 'csv_dir')
    json_dir = config.get('PATHS', 'json_dir')
    in_path = config.get('PATHS', 'demo_path')

    # Create output directories if they don't exist
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    demo_files = []

    # Iterate through the files and unzip .dem.gz files
    for f in os.listdir(in_path):
        if f.endswith(".dem.gz"):
            gz_file_path = os.path.join(in_path, f)
            # Remove the '.gz' extension
            dem_file_path = os.path.join(in_path, f[:-3])
            with gzip.open(gz_file_path, 'rb') as gz_file, open(dem_file_path, 'wb') as dem_file:
                dem_file.write(gz_file.read())
            os.remove(gz_file_path)
            demo_files.append(dem_file_path)
        elif f.endswith(".dem"):
            demo_files.append(os.path.join(in_path, f))

    for dnum, demo_filename in enumerate(demo_files, start=1):
        try:
            process_demo(demo_filename, dnum, csv_dir, json_dir, in_path)
        except Exception as e:
            print(f"An error occurred while processing {demo_filename}: {e}")
            print(
                f"Skipping {demo_filename} and continuing with the next demo.")
            continue

    print("Parsing complete!")


if __name__ == "__main__":
    main()
