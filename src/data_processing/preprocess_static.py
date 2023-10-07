import gzip
import pickle
import os
import glob
import configparser
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, FunctionTransformer, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin


# Class defining a custom label encoder


class LabelEncoderTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        label_encoder = LabelEncoder()
        X_encoded = np.copy(X)  # Create a copy of the input array
        for col_idx in range(X.shape[1]):  # Iterate through columns
            X_encoded[:, col_idx] = label_encoder.fit_transform(X[:, col_idx])
        return X_encoded


# Function to save the merged dataframe to a csv file


def save_csv(df, output_dir, num):

    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_dir, f"match{num}.csv")

    # Save the merged dataframe to the corresponding directory
    df.to_csv(output_file, index=False)

    print(f"Saved {output_file}")


# Function to save the merged dataframe to a parquet file


def save_file(df, output_dir, num):

    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_dir, f"match{num}.parquet")

    # Save the merged dataframe to the corresponding directory
    df.to_parquet(output_file, index=False)

    print(f"Saved {output_file}")

# Function to save the merged dataframe to a pkl file (if required)


def save_file_compressed(df, output_dir, num):

    # Save as pkl zipped
    output_file = os.path.join(output_dir, f"match{num}.pkl.gz")
    with gzip.open(output_file, 'wb') as f:
        pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Saved {output_file}")


# Function to process the labels


def process_labels(labels):

    # Use the SimpleImputer() to fill missing values with 0
    imputer = SimpleImputer(strategy='constant', fill_value=0)

    labels = imputer.fit_transform(labels.values.reshape(-1, 1))

    # Convert the labels to a list
    labels = list(labels)

    return labels

# Feature engineering


def clean_features(df):

    # Check if 'playerSteamID' and 'steamID' columns have conflicting values
    df['valid_row'] = df['playerSteamID'].notna() & df['steamID'].notna()

    if df['valid_row'].any():
        print("Merging columns 'playerSteamID and steamID is not possible! Continuing without merging...")
        df.drop('valid_row', axis=1, inplace=True)
    else:
        print("Merging columns 'playerSteamID and steamID'...")
        df['steamID'] = df.apply(lambda row: row['playerSteamID'] if not pd.isna(
            row['playerSteamID']) else row['steamID'], axis=1)
        df.drop('playerSteamID', axis=1, inplace=True)
        df.drop('valid_row', axis=1, inplace=True)

    drop_cols = ['matchID', 'matchId', 'isTrade', 'playerTradedName',
                 'playerTradedTeam', 'playerTradedSteamID', 'playerTradedSide']
    df.drop(columns=drop_cols, axis=1, inplace=True)

    return df

# Function to label the data


def label(df, loc):

    for dir in os.listdir(loc):
        if dir.endswith(".parquet"):
            labels = pd.read_parquet(os.path.join(loc, dir))

        merged_df = df.merge(
            labels[['steamID', 'label']], on='steamID', how='left')

    return merged_df

# Convert boolean values to integers


def bool_to_int(data):
    return data.astype(int)

# Function to convert clockTime column to seconds


def convert_clockTime(df):

    df['clockTime'].fillna('0:00', inplace=True)
    df['clockTime'] = df['clockTime'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    return df


# Function to preprocess the data


def preprocessing(df):

    # Reformat clockTime column
    for col in df.columns:
        if col == 'clockTime':
            df = convert_clockTime(df)

    # Define numerical and categorical features
    numerical_features = [
        col for col in df.columns if df[col].dtype in ['int64', 'float64'] and col != 'label']
    categorical_features = [
        col for col in df.columns if df[col].dtype == 'object']

    # Clean categorical features
    for cols in categorical_features:
        unique_column_dtypes = df[cols].apply(type).unique()
        if len(unique_column_dtypes) > 1 and bool in unique_column_dtypes:
            df[cols] = df[cols].fillna('False').astype(bool)

    # Define boolean features
    boolean_features = [
        col for col in df.columns if df[col].dtype == 'bool']

    # Update categorical features
    categorical_features = [
        col for col in categorical_features if col not in boolean_features]

    # Define transformers

    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('label', LabelEncoderTransformer())
    ])
    boolean_transformer = Pipeline(steps=[
        ('bool_to_int', FunctionTransformer(bool_to_int))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features),
            ('bool', boolean_transformer, boolean_features)
        ])

    processed_data = preprocessor.fit_transform(df)

    processed_df = pd.DataFrame(processed_data,
                                columns=numerical_features + categorical_features + boolean_features)

    # Process 'label' column separately
    labels = process_labels(df['label'])

    # Add 'label' column to the processed dataframe
    processed_df['label'] = labels

    # Convert columns to float type
    processed_df = processed_df.astype(float)

    return processed_df

# Function to aggregate the data from each match


def aggregation(match_files):

    merged_data = pd.DataFrame()

    for file in match_files:
        df = pd.read_csv(file)
        if merged_data.empty:
            merged_data = df.copy()
        else:
            merged_data = pd.concat(
                [merged_data, df], ignore_index=True)

    merged_data = merged_data.sort_values(by=['tick'])
    merged_data = merged_data.reset_index(drop=True)

    return merged_data


def main():
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    config.read("config.ini")

    processed_dir = config.get("PATHS", "processed_data_dir")
    csv_dir = config.get("PATHS", "csv_dir")
    labels_dir = config.get("PATHS", "labels_dir")

    num = 1

    for dir in os.listdir(csv_dir):
        if dir.startswith("match"):

            csv_files = glob.glob(os.path.join(csv_dir, dir, "*.csv"))

            csv_files = [file for file in csv_files if not (
                os.path.basename(file).startswith(
                    ("grenades", "info", "rounds"))
            )]

            print(f"Combining files in {dir}...")
            merged_data = aggregation(csv_files)

            print("Cleaning features...")
            cleaned_data = clean_features(merged_data)

            print("Labelling data...")
            labelled_df = label(cleaned_data, labels_dir)

            print("Performing preprocessing...")
            processed_df = preprocessing(labelled_df)

            # save_file(processed_df, processed_dir, num)
            # save_csv(processed_df, processed_dir, num)

            print("\n")
            num += 1

    print("Preprocessing done!")


if __name__ == "__main__":
    main()
