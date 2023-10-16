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
    '''
    A transformer that applies LabelEncoder to each column of a 2D array.

    This transformer applies scikit-learn's LabelEncoder to each column of a 2D
    array independently. The input array is not modified, and a new array with
    the same shape is returned. The transformer can be used in a scikit-learn
    pipeline to preprocess categorical features before feeding them to a model.

    Parameters
    ----------
    None

    Attributes
    ----------
    None

    Methods
    -------
    fit(X, y=None)
        Do nothing and return self.
    transform(X)
        Apply LabelEncoder to each column of X and return the transformed array.
    '''

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        label_encoder = LabelEncoder()
        X_encoded = np.copy(X)  # Create a copy of the input array
        for col_idx in range(X.shape[1]):  # Iterate through columns
            X_encoded[:, col_idx] = label_encoder.fit_transform(X[:, col_idx])
        return X_encoded


def save_csv(df, output_dir, num):
    '''
    Save a pandas DataFrame to a CSV file in the specified output directory.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to be saved.
    output_dir : str
        The path to the directory where the CSV file will be saved.
    num : int
        A number to be included in the CSV file name.

    Returns:
    --------
    None
    '''
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_dir, f"match{num}.csv")

    # Save the merged dataframe to the corresponding directory
    df.to_csv(output_file, index=False)

    print(f"Saved {output_file}")


def save_file(df, output_dir, num):
    '''
    Saves a pandas DataFrame to a parquet file in the specified output directory.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to be saved.
    output_dir : str
        The path to the directory where the file will be saved.
    num : int
        A number to be included in the file name.

    Returns:
    --------
    None
    '''
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_dir, f"match{num}.parquet")

    # Save the merged dataframe to the corresponding directory
    df.to_parquet(output_file, index=False)

    print(f"Saved {output_file}")


def save_file_compressed(df, output_dir, num):
    '''
    Save a pandas DataFrame as a compressed pickle file.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to be saved.
    output_dir : str
        The directory where the output file will be saved.
    num : int
        A number to be included in the output file name.

    Returns:
    --------
    None
    '''
    # Save as pkl zipped
    output_file = os.path.join(output_dir, f"match{num}.pkl.gz")
    with gzip.open(output_file, 'wb') as f:
        pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Saved {output_file}")


def process_labels(labels):
    '''
    Fill missing values in the input labels with 0 using SimpleImputer.

    Parameters:
    -----------
    labels : pandas.DataFrame or pandas.Series
        The input labels to be processed.

    Returns:
    --------
    list
        The processed labels as a list.
    '''
    # Use the SimpleImputer() to fill missing values with 0
    imputer = SimpleImputer(strategy='constant', fill_value=0)

    labels = imputer.fit_transform(labels.values.reshape(-1, 1))

    # Convert the labels to a list
    labels = list(labels)

    return labels

# Feature engineering


def clean_features(df):
    '''
    Cleans the input DataFrame by performing the following operations:
    - Merges the 'playerSteamID' and 'steamID' columns, if possible, by replacing missing values in 'steamID' with the corresponding values in 'playerSteamID'.
    - Drops the 'playerSteamID' and 'valid_row' columns, if they exist.
    - Drops several other columns that are not needed for further analysis.

    Parameters:
    df (pandas.DataFrame): The input DataFrame to be cleaned.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    '''
    # Check if 'playerSteamID' and 'steamID' columns have conflicting values
    df['valid_row'] = df['playerSteamID'].notna() & df['steamID'].notna()

    if df['valid_row'].any():
        print("Merging columns 'playerSteamID' and 'steamID' is not possible! Continuing without merging...")
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
    '''
    Merge the given DataFrame `df` with the labels DataFrame found in the directory `loc`.
    The labels DataFrame should have columns 'steamID' and 'label'.
    The merge is performed on the 'steamID' column, using a left join.
    Returns the merged DataFrame.
    '''
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
    '''
    Converts the 'clockTime' column of the given DataFrame to a numerical value in seconds.

    The 'clockTime' column is expected to contain strings in the format 'MM:SS', where MM is the minute
    (00-59) and SS is the second (00-59). Missing values are replaced with '0:00'. The function
    converts each string to a numerical value equal to the number of seconds. For example, '9:30' 
    is converted to 570 (9*60 + 30).

    Parameters:
    df (pandas.DataFrame): The DataFrame to process. It must contain a 'clockTime' column.

    Returns:
    pandas.DataFrame: The processed DataFrame, with the 'clockTime' column replaced by the
    corresponding numerical values.
    '''
    df['clockTime'].fillna('0:00', inplace=True)
    df['clockTime'] = df['clockTime'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    return df


# Function to preprocess the data


def preprocessing(df):
    '''
    Preprocesses a pandas DataFrame for machine learning.

    Parameters:
    -----------
    df : pandas DataFrame
        The input DataFrame to preprocess.

    Returns:
    --------
    processed_df : pandas DataFrame
        The preprocessed DataFrame, with numerical and categorical features transformed
        and the 'label' column processed separately.
    '''
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
    '''
    Aggregate data from multiple CSV files into a single DataFrame.

    Parameters:
    -----------
    match_files : list of str
        List of file paths to CSV files containing data to be aggregated.

    Returns:
    --------
    merged_data : pandas.DataFrame
        DataFrame containing the aggregated data from all input files.
        The rows are sorted by the 'tick' column and the index is reset.
    '''
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
    '''
    This function reads configuration from a config file, processes data from CSV files, cleans the features, labels the data, performs preprocessing, and saves the processed data to a directory. It loops through all the directories in the CSV directory and combines the CSV files in each directory, excluding certain files. It then performs the necessary data processing steps and saves the processed data to the processed data directory.

    Args:
        None

    Returns:
        None
    '''
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
