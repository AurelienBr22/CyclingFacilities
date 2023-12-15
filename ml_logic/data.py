import numpy as np
import pandas as pd
import os
import requests
import yaml

#### DL, SAVE & CONCAT DATASETS ####
def get_datasets_url(url):
    response = requests.get(url).json()
    return {el['title']: el['latest'] for el in response['resources'] if el['title'].endswith(".csv") and not el['title'].startswith("vehicules-immatricules")}


def download_and_save_datasets(url_dict, save_path):
    for path, url in url_dict.items():
        full_path = os.path.join(save_path, path)
        if not os.path.exists(full_path):
            response = requests.get(url)
            if response.status_code == 200:
                with open(full_path, 'wb') as f:
                    f.write(response.content)


def rename_files(config_path, save_path):
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        rename_config = config.get('rename')

    for old_name, new_name in rename_config.items():
        old_file_path = os.path.join(save_path, old_name)
        new_file_path = os.path.join(save_path, new_name)

        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            print(f"Fichier renommé : {old_name} -> {new_name}")
        else:
            print(f"Fichier non trouvé : {old_name}")

def download_and_process_datasets(base_url='https://www.data.gouv.fr/api/1/datasets/53698f4ca3a729239d2036df/',
                                  config_path='../config.yml',
                                  save_path='../raw_data/'):
    datasets = get_datasets_url(base_url)
    categories = ["lieux", "usagers", "car", "vehicule"]

    categorized_urls = {category: {i: j for i, j in datasets.items() if i.startswith(category)}
                        for category in categories}

    for category, url_dict in categorized_urls.items():
        download_and_save_datasets(url_dict, save_path)

    rename_files(config_path, save_path)

    return categorized_urls

def concat_files(starting_word):

    chemin_fichier_yml = '../config.yml'
    with open(chemin_fichier_yml, 'r') as f:
        config = yaml.safe_load(f)
        config_sep = config.get('sep')
        config_encoding = config.get('encoding')

    chemin_dossier = '../raw_data/'

    df_concat = pd.DataFrame()
    files = [file for file in os.listdir(chemin_dossier) if file.endswith('.csv') and file.startswith(starting_word)]

    print(files)
    for file in files:
        chemin_fichier = os.path.join(chemin_dossier, file)

        if file in config_sep:
            sep = config_sep[file]
        else:
            sep = ','

        if file in config_encoding:
            encoding = config_encoding[file]
        else:
            encoding = 'utf-8'

        df1 = pd.read_csv(chemin_fichier, sep=sep, encoding=encoding)

        df_concat = pd.concat([df_concat, df1])

    return df_concat


#### CLEANING VEHICULES ####
catv_group_named = {
    "Bicycles_ElectricScooters": [1, 80, 50, 60],  # Bicycles, E-bikes, and Personal Mobility Devices
    "Cars": [3, 7, 8, 9],  # Cars including light vehicles, VL + caravane, VL + remorque
    "Motorcycles_Scooters": [2, 30, 31, 32, 33, 34, 41, 42, 43, 4, 5, 6],  # Motorcycles, scooters, scooter immatriculé, motocyclette, side-car
    "HeavyVehicles_Buses": [10, 13, 14, 15, 16, 17, 37, 38, 18, 19],  # Utility vehicles, heavy trucks, buses, transport en commun, tramway
    "Others_SpecialVehicles": [0, 20, 21, 39, 40, 99, 11, 12, 35, 36]  # Special vehicles and others, VU + caravane, VU + remorque
}


obs_group_named = {
    "NoObstacle": [-1, 0],  # Without obstacle
    "WithObstacle": list(range(1, 18))  # With obstacle
}

obsm_group_named = {
    "Pedestrian_Vehicle_Rail": [1, 2, 4],  # Pedestrian, Vehicle, Rail Vehicle
    "Animals": [5, 6],  # Animals
    "Others_NotClassified": [-1, 0, 9]  # Other or Not Classified
}

choc_group_named = {
    "NoImpact": [0],  # No impact
    "Impact": list(range(1, 10))  # Impact
}

manv_group_named = {
    "BasicManeuvers": [1, 2, 3],  # Standard driving maneuvers
    "DirectionalChanges": [11, 12, 13, 14, 15, 16, 17, 18],  # Maneuvers involving directional changes
    "DefensiveManeuvers": [21, 22],  # Defensive driving maneuvers
    "TrajectoryChanges": [10],  # Significant trajectory changes
    "RiskyManeuvers": [4, 5, 6, 7, 8, 9, 19, 26],  # Unusual or risky maneuvers
    "StationaryParkingManeuvers": [20, 23, 24, 25]  # Stationary or parking related maneuvers
}

def clean_and_transform_data(df, catv_group_inverted, choc_group_inverted, obs_group_inverted, obsm_group_inverted, manv_group_inverted):
    # Drop unnecessary columns
    df_modif = df.drop(["id_vehicule", "motor", "occutc", "senc"], axis=1)

    # CATV: Assign mode to -1 values
    df_modif.loc[df_modif.catv == -1, 'catv'] = df_modif.catv.mode()[0]

    # Define a function for cleaning and imputing values based on distribution
    def clean_and_impute(column):
        # Calculate distribution of values greater than or equal to 0
        values_distribution = df_modif[column][df_modif[column] >= 0].value_counts(normalize=True)

        # Impute NaNs and -1 values
        for condition in [df_modif[column].isna(), df_modif[column] == -1]:
            new_values = np.random.choice(values_distribution.index, size=condition.sum(), p=values_distribution.values)
            df_modif.loc[condition, column] = new_values

    # Apply the cleaning and imputing function to specified columns
    for col in ['obs', 'obsm', 'choc', 'manv']:
        clean_and_impute(col)

    # Mapping to group values
    df_modif['catv'] = df_modif['catv'].map(catv_group_inverted)
    df_modif['choc'] = df_modif['choc'].map(choc_group_inverted)
    df_modif['obs'] = df_modif['obs'].map(obs_group_inverted)
    df_modif['obsm'] = df_modif['obsm'].map(obsm_group_inverted)
    df_modif['manv'] = df_modif['manv'].map(manv_group_inverted)

    return df_modif


#### CLEANING CARACTERISTIQUES ####
def drop_columns(df, columns):
    return df.drop(columns, axis=1, inplace=False)


def process_dates(df, year_col='an', month_col='mois', day_col='jour', time_col='hrmn'):
    # Checking for invalid dates
    invalid_dates = df[(df[day_col] > 31) | ((df[month_col] == 2) & (df[day_col] > 29)) | ((df[month_col].isin([4, 6, 9, 11])) & (df[day_col] > 30))]
    df = df.drop(invalid_dates.index)

    # Creating the 'date' column
    df['date'] = pd.to_datetime(df[year_col].astype(str).str.zfill(2)
                                + df[month_col].astype(str).str.zfill(2)
                                + df[day_col].astype(str).str.zfill(2)
                                + df[time_col].astype(str).str.zfill(4),
                                format='%y%m%d%H%M', errors='coerce')

    df = df.drop(columns=[year_col, month_col, day_col, time_col])
    return df

def drop_nans(df, columns):
    return df.dropna(subset=columns)

def clean_column_distribution(df, column, invalid_value=-1):
    valid_values = df[column][df[column] >= 0].value_counts(normalize=True)
    new_values = np.random.choice(valid_values.index, size=(df[column] == invalid_value).sum(), p=valid_values.values)
    df.loc[df[column] == invalid_value, column] = new_values
    return df

def replace_with_most_frequent(df, column, invalid_value=-1):
    most_frequent = df[column].mode()[0]
    df[column] = df[column].replace(invalid_value, most_frequent)
    return df

def filter_df_on_column(df, column, valid_values):
    return df.loc[df[column].isin(valid_values)]

#### CLEANING LIEUX ###
def clean_column(df, column, replace_dict, fill_value):
    df[column] = df[column].replace(replace_dict)
    df[column].fillna(fill_value, inplace=True)
    return df

def clean_nbv(df):
    df['nbv'] = pd.to_numeric(df['nbv'], errors='coerce')
    df = clean_column(df, 'nbv', {-1: 2}, 2)
    df['nbv'] = df['nbv'].where(df['nbv'] <= 10, 2)
    return df

def clean_catr(df):
    df['catr'].fillna(4, inplace=True)
    return df

#### CLEANING USAGERS ####
def process_grav_sexe(df, column):
    df[column] = df[column].replace({-1: 1}).fillna(1)
    return df

def process_secu(df):
    df['secu'].fillna(df['secu1'], inplace=True)
    df['secu'] = df['secu'].where(df['secu'] <= 0, 1)
    return df

def process_actp(df):
    df['actp'] = pd.to_numeric(df['actp'], errors='coerce').fillna(0).astype(int)
    return df

def process_locp_etatp(df, columns):
    for column in columns:
        df[column] = df[column].replace({-1: 0}).fillna(0).astype(int)
    return df

def process_an_nais(df):
    df.dropna(subset=['an_nais'], inplace=True)
    mean_an_nais = df['an_nais'].mean()
    df['an_nais'] = df['an_nais'].replace({0: mean_an_nais})
    return df

def drop_irrelevant_columns(df, columns):
    return df.drop(columns=columns)

def process_trajet(df):
    trajet_impute = df['trajet'].fillna(5)
    distribution = trajet_impute[~trajet_impute.isin([0, -1])].value_counts(normalize=True)
    missing_values = trajet_impute.isin([0, -1])
    trajet_impute[missing_values] = np.random.choice(distribution.index, size=missing_values.sum(), p=distribution.values)
    df['trajet'] = trajet_impute.astype(int).replace({-1: 1})
    return df


# dl, save datasets
download_and_process_datasets()

# concat datasets
carac_df = concat_files("caracteristiques")
lieux_df = concat_files("lieux")
usager_df = concat_files("usagers")
vehi_df = concat_files("vehicules")

# clean vehicules
vehi_df_clean = clean_and_transform_data(vehi_df, catv_group_inverted, choc_group_inverted, obs_group_inverted, obsm_group_inverted, manv_group_inverted)

# clean caracteristiques
carac_df_clean = (carac_df
                  .pipe(drop_columns, ['gps', 'Accident_Id'])
                  .pipe(process_dates)
                  .pipe(drop_nans, ['Num_Acc'])
                  .pipe(clean_column_distribution, 'lum')
                  .pipe(filter_df_on_column, 'int', valid_values=[value for value in carac_df['int'].unique() if value != -1])
                  .pipe(drop_nans, ['col', 'atm', 'com'])
                  .pipe(replace_with_most_frequent, 'col')
                  .pipe(replace_with_most_frequent, 'atm'))

# clean lieux
lieux_df_clean = (lieux_df
                  .pipe(clean_column, 'situ', {-1: 1, 0: 1}, 1)
                  .pipe(clean_column, 'circ', {0: 2, -1: 2}, 2)
                  .pipe(clean_nbv)
                  .pipe(clean_column, 'vosp', {-1: 0}, 0)
                  .pipe(clean_column, 'prof', {-1: 1, 0: 1}, 1)
                  .pipe(clean_column, 'plan', {-1: 1, 0: 1}, 1)
                  .pipe(clean_column, 'surf', {-1: 1, 0: 1, 9: 1}, 1)
                  .pipe(clean_column, 'infra', {-1: 1}, 1)
                  .pipe(clean_catr)
                  .pipe(drop_irrelevant_columns, ['voie', 'v1', 'v2', 'pr', 'pr1', 'lartpc', 'larrout', 'vma', 'env1']))

# clean usagers
usager_df_clean = (usager_df
                .pipe(process_grav_sexe, column='grav')
                .pipe(process_grav_sexe, column='sexe')
                .pipe(process_trajet)
                .pipe(process_secu)
                .pipe(process_actp)
                .pipe(process_locp_etatp, columns=['locp', 'etatp'])
                .pipe(process_an_nais)
                .pipe(drop_irrelevant_columns, columns=['place', 'catu', 'secu1', 'secu2', 'secu3', 'num_veh', 'id_vehicule', 'id_usager']))
