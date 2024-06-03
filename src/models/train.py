from deepod.models.tabular import DeepSAD
import dask.dataframe as dd
import pandas as pd
from sklearn.model_selection import train_test_split
import configparser
from deepod.metrics import tabular_metrics
import os
import joblib


# Semi-supervised learning


def dsad(X_train, y_train, X_test, y_test, save_path_src, save_path_ser, columns):

    model = DeepSAD()

    model.fit(X_train, y_train)

    joblib.dump(model, os.path.join(save_path_src, "dsad_trained.joblib"))
    joblib.dump(model, os.path.join(save_path_ser, "dsad_trained.joblib"))

    scores = model.decision_function(X_test)

    anomalies = X_test[scores > 0.5]

    auc, ap, f1 = tabular_metrics(y_test, scores)
    print("Results for DeepSAD:\n",
          f"auc: {auc:.2f}, average precision: {ap:.2f}, f1: {f1:.2f}")

    return pd.DataFrame(anomalies, columns=columns)


def load_data(data_dir):

    data = []
    # Change this value to load more data
    for file in os.listdir(data_dir)[:10]:
        if file.endswith(".parquet"):
            df = dd.read_parquet(os.path.join(data_dir, file))
            data.append(df)

    data = dd.concat(data)

    columns = [col for col in data.columns if col != "label"]

    return data, columns


if __name__ == "__main__":

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    config = configparser.ConfigParser()
    config.read("config.ini")
    data_dir = config.get("PATHS", "data_dir")
    save_dir_src = config.get("PATHS", "save_path_src")
    save_dir_ser = config.get("PATHS", "save_path_ser")

    data, columns = load_data(data_dir)

    X = data.drop(["label"], axis=1)
    y = data["label"]

    X = X.to_dask_array(lengths=True)
    y = y.to_dask_array(lengths=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X.compute(), y.compute(), test_size=0.2)

    anomalies = dsad(X_train, y_train, X_test, y_test,
                     save_dir_src, save_dir_ser, columns)

    print(anomalies['steamID'])
