from pipeline import parser
from pipeline import preprocess
import models.predictions
from dashboard import app
import json
import sys
import os


def main():

    # Extract the argument from the command line
    file_loc = sys.argv[1]

    csv_loc = parser.parser(file_loc)
    output_dataset_dir = os.path.join("D:\\anticheat\\serving\\data", os.path.splitext(
        os.path.basename(file_loc))[0], "processed")
    output_metadata_dir = os.path.join("D:\\anticheat\\serving\\data", os.path.splitext(
        os.path.basename(file_loc))[0], "metadata")

    file_paths = [os.path.join(csv_loc, file) for file in os.listdir(csv_loc)]
    file_paths = [file for file in file_paths
                  if not os.path.basename(file).startswith(("grenades", "info", "rounds"))]

    merged = preprocess.aggregation(file_paths)
    cleaned_data = preprocess.clean_features(merged)
    processed_df, scaler = preprocess.preprocessing(cleaned_data)
    preprocess.save_file(processed_df, output_dataset_dir)
    preprocess.save_metadata(scaler, output_metadata_dir)
    anomalies = models.predictions.show_anomalies(
        data_dir=output_dataset_dir, md_dir=output_metadata_dir)

    if anomalies.size == 0:
        print("No usage of unfair means detected!")
    else:
        for anomaly in anomalies:
            print(f"{anomaly:.0f}")


if __name__ == "__main__":
    main()
