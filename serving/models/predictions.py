import os
import pickle
import dask.dataframe as dd
import pandas as pd
import numpy as np
import torch
import joblib


def load_data(data_dir):
    data = []
    for file in os.listdir(data_dir):
        if file.endswith(".parquet"):
            df = dd.read_parquet(os.path.join(data_dir, file))
            data.append(df)

    data = dd.concat(data)
    columns = data.columns

    return data, columns


def predict(data_dir):

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    data, columns = load_data(data_dir)
    data_array = data.to_dask_array(lengths=True)

    for f in os.listdir(os.getcwd()):
        if f.endswith(".joblib"):
            model = joblib.load(f)
            scores = model.decision_function(data_array.compute())
            anomalies = data_array[scores > 75.0]

    return pd.DataFrame(anomalies, columns=columns)


def show_anomalies(data_dir, md_dir):

    anomalies = predict(data_dir)
    for f in os.listdir(md_dir):
        if f.endswith(".pkl"):
            scaler = joblib.load(os.path.join(md_dir, f))
            steamID_data = anomalies['steamID'].to_numpy().reshape(-1, 1)

            if steamID_data.size == 0:
                pass
            else:
                # Perform the inverse transformation
                steamID_data = scaler.inverse_transform(steamID_data)
                return list(np.unique(steamID_data))
