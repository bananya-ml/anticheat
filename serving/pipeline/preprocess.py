import os
import pandas as pd
import numpy as np
import joblib
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, LabelEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin


def inverse_scaler(df):

    imputed_df = df['steamID'].fillna(0)

    scaler = StandardScaler()
    scaled_df = scaler.fit_transform(imputed_df.values.reshape(-1, 1))

    return scaler


def bool_to_int(data):
    return data.astype(int)


class LabelEncoderTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        label_encoder = LabelEncoder()
        X_encoded = np.copy(X)  # Create a copy of the input array
        for col_idx in range(X.shape[1]):  # Iterate through columns
            X_encoded[:, col_idx] = label_encoder.fit_transform(X[:, col_idx])
        return X_encoded


def convert_clockTime(df):

    df['clockTime'].fillna('0:00', inplace=True)
    df['clockTime'] = df['clockTime'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    return df


def clean_features(df):

    df['valid_row'] = df['playerSteamID'].notna() & df['steamID'].notna()

    if df['valid_row'].any():
        print("Merging columns 'playerSteamID and steamID is not possible! Continuing without merging...")
        df.drop('valid_row', axis=1, inplace=True)
    else:

        df['steamID'] = df.apply(lambda row: row['playerSteamID'] if not pd.isna(
            row['playerSteamID']) else row['steamID'], axis=1)
        df.drop('playerSteamID', axis=1, inplace=True)
        df.drop('valid_row', axis=1, inplace=True)

    drop_cols = ['attackerSide', 'attackerTeam', 'assisterName', 'assisterTeam', 'assisterSide',
                 'activeWeapon', 'ammoInMagazine', 'ammoInReserve', 'armor', 'armorDamage',
                 'armorDamageTaken', 'assisterSteamID', 'cash', 'cashSpendThisRound',
                 'cashSpendTotal', 'ctEqVal', 'ctTeamName', 'ctUtility', 'equipmentValue',
                 'equipmentValueFreezetimeEnd', 'equipmentValueRoundStart', 'flashThrowerSide',
                 'flashThrowerTeam', 'hasDefuse', 'hasHelmet', 'hp', 'hpDamage', 'hpDamageTaken',
                 'isTrade', 'isInBombZone', 'isInBuyZone', 'matchID', 'playerSide', 'playerTeam',
                 'playerTradedName', 'playerTradedTeam', 'playerTradedSteamID', 'playerTradedSide',
                 'side', 'tAlivePlayers', 'tEqVal', 'tUtility', 'tTeamName', 'team', 'teamName',
                 'throwerSide', 'throwerTeam', 'totalUtility', 'victimTeam', 'victimSide', 'tBuyType',
                 'tRoundSpendMoney', 'tRoundStartEqVal', 'ctBuyType', 'ctRoundSpendMoney',
                 'ctRoundStartEqVal', 'winningTeam', 'losingTeam', 'attackerName', 'victimViewY',
                 'ctFreezeTimeEndEqVal', 'freezeTimeEndTick', 'name', 'spotters', 'tFreezeTimeEndEqVal',
                 'tTeam', 'throwerSteamID', 'hasBomb', 'isBlinded', 'roundNum', 'isWalking', 'noScope',
                 'isScoped', 'endOfficialTick', 'victimZ', 'isWallbang', 'victimBlinded', 'endTScore',
                 'throwerName', 'attackerViewX', 'victimSteamID', 'isPlanting', 'attackerBlinded',
                 'victimViewX', 'endCTScore', 'isDucking', 'victimY', 'isFriendlyFire',
                 'distance', 'victimX', 'isDuckingInProgress', 'isDefusing', 'isTeamkill', 'thruSmoke',
                 'isFirstKill', 'isReloading', 'isUnDuckingInProgress', 'isUnknown']
    df.drop(columns=drop_cols, axis=1, inplace=True)

    return df


def feature_engineering(df):

    coord_cols = []
    changes_dict = {}
    identifiers = []

    for col in df.columns:
        if col.endswith(('x', 'y', 'z', 'X', 'Y', 'Z')):
            coord_cols.append(col)

    for col in coord_cols:
        identifier = col[:-1]
        if len(identifier) == 0:
            continue
        else:
            identifiers.append(identifier)

    identifiers = set(identifiers)

    for identifier in identifiers:
        identifier_columns = [column for column in coord_cols if column.startswith(
            identifier) and column[len(identifier)] in ['X', 'Y', 'Z']]
        changes_dict[identifier] = identifier_columns

    for new_col, old_cols in changes_dict.items():
        df[new_col] = 0
        for i in range(len(old_cols)):
            df[new_col] += df[old_cols[i]] * 10**(-(i+1))

        df.drop(columns=old_cols, inplace=True)

    if 'x' in df.columns and 'y' in df.columns and 'z' in df.columns:
        df['pos'] = df['x'] * 10**(-1) + df['y'] * \
            10**(-2) + df['z'] * 10**(-3)
        df.drop(['x', 'y', 'z'], axis=1, inplace=True)

    return df


def preprocessing(df):

    for col in df.columns:
        if col == 'clockTime':
            df = convert_clockTime(df)

    df = feature_engineering(df)
    print(df.shape)
    numerical_features = [
        col for col in df.columns if df[col].dtype in ['int64', 'float64']]
    categorical_features = [
        col for col in df.columns if df[col].dtype == 'object']

    for cols in categorical_features:
        unique_column_dtypes = df[cols].apply(type).unique()
        if len(unique_column_dtypes) > 1 and bool in unique_column_dtypes:
            df[cols] = df[cols].fillna('False').astype(bool)

    boolean_features = [
        col for col in df.columns if df[col].dtype == 'bool']

    categorical_features = [
        col for col in categorical_features if col not in boolean_features]

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

    processed_df = processed_df.astype(float)

    scaler = inverse_scaler(df)

    return processed_df, scaler


def aggregation(match_files):

    merged_data = pd.DataFrame()

    for file in match_files:
        if os.path.basename(file).startswith("grenades"):
            df = pd.read_csv(file)
            df = df.rename(columns={"throwTick": "tick"})
        else:
            df = pd.read_csv(file)

        if merged_data.empty:
            merged_data = df.copy()
        else:
            merged_data = pd.concat(
                [merged_data, df], ignore_index=True)

    merged_data = merged_data.sort_values(by=['tick'])
    merged_data = merged_data.reset_index(drop=True)

    return merged_data


def save_file(df, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "data.parquet")

    df.to_parquet(output_file, index=False)


def save_metadata(scaler, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "scaler.pkl")

    joblib.dump(scaler, output_file)
