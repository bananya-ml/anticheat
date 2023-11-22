from pipeline import parser
from pipeline import preprocess
import models.predictions
import sys
import os


def main():
    '''
    Runs the anti-cheat system on the input file specified as a command line argument.
    The input file is expected to be a directory containing CSV files with data from game matches.
    The function preprocesses the data, detects anomalies using a machine learning model, and prints
    the IDs of any detected anomalies to the console. If no anomalies are detected, it prints a message
    indicating that no unfair means were detected.

    Args:
        None

    Returns:
        None
    '''
    # Extract the argument from the command line
    file_loc = sys.argv[1]

    csv_loc = parser.parser(file_loc)
    output_dataset_dir = os.path.join(os.path.join(os.getcwd(), "data"), os.path.splitext(
        os.path.basename(file_loc))[0], "processed")
    output_metadata_dir = os.path.join(os.path.join(os.getcwd(), "data"), os.path.splitext(
        os.path.basename(file_loc))[0], "metadata")

    file_paths = [os.path.join(csv_loc, file) for file in os.listdir(csv_loc)]
    file_paths = [file for file in file_paths
                  if not os.path.basename(file).startswith(("bomb", "flashes", "info"))]

    merged = preprocess.aggregation(file_paths)
    cleaned_data = preprocess.clean_features(merged)
    processed_df, scaler = preprocess.preprocessing(cleaned_data)
    preprocess.save_file(processed_df, output_dataset_dir)
    preprocess.save_metadata(scaler, output_metadata_dir)
    anomalies = models.predictions.show_anomalies(
        data_dir=output_dataset_dir, md_dir=output_metadata_dir)

    if not anomalies:
        print("No usage of unfair means detected!")
    else:
        for anomaly in anomalies:
            if int(anomaly) != 0:
                print(f"{anomaly:.0f}")


if __name__ == "__main__":
    main()
