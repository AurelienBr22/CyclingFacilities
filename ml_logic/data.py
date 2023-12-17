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
def process_catv(df):
    df.loc[df.catv == -1, 'catv'] = df.catv.mode()[0]
    df = df[df['catv']==1]
    return df

def create_aug(df):
    df['aug'] = df['Num_Acc'].astype(str) + df['num_veh'].astype(str)
    return df

def remove_duplicated_acc(df):
    return df[~df['Num_Acc'].duplicated(keep=False)]


#### CLEANING CARACTERISTIQUES ####
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

def impute_invalid_values(df, columns, invalid_values):
    for column in columns:
        for invalid_value in invalid_values:
            # Separate handling for NaN/NaT values
            if pd.isna(invalid_value) or (isinstance(invalid_value, pd._libs.tslibs.nattype.NaTType) and pd.api.types.is_datetime64_any_dtype(df[column])):
                # calculate distribution excluding NaN and other invalid values
                distribution = df[column][~df[column].isin(invalid_values)].value_counts(normalize=True)

                # assign new values
                new_values = np.random.choice(distribution.index, size=df[column].isna().sum(), p=distribution.values)
                df.loc[df[column].isna(), column] = new_values
            else:
                # calculate distribution for a given value, excluding other invalid values
                distribution = df[column][~df[column].isin(invalid_values)].value_counts(normalize=True)

                # assign new values
                new_values = np.random.choice(distribution.index, size=(df[column] == invalid_value).sum(), p=distribution.values)
                df.loc[df[column] == invalid_value, column] = new_values
    return df

def replace_with_most_frequent(df, columns, invalid_value=-1):
    for column in columns:
        most_frequent = df[column].mode()[0]
        df[column] = df[column].replace(invalid_value, most_frequent)
    return df

def remove_no_location(df):
    df = df[~((df.adr.isna()) & ((df.lat.isna()) & (df.long.isna())) )]
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

def create_dup_count(df):
    df['dup_count'] = df.groupby('aug')['aug'].transform('count')
    df = df.drop_duplicates(subset=['aug'], keep='first')
    return df

def concat_datasets():
    # concat datasets
    carac_df = concat_files("caracteristiques")
    lieux_df = concat_files("lieux")
    usager_df = concat_files("usagers")
    vehi_df = concat_files("vehicules")
    return vehi_df, carac_df, lieux_df, usager_df

def clean_datasets(vehi_df, carac_df, lieux_df, usager_df):
    # clean vehicules
    vehi_df_clean = (vehi_df
                    .pipe(drop_irrelevant_columns, ["id_vehicule", "motor", "occutc", "senc"])
                    .pipe(process_catv)
                    .pipe(create_aug)
                    .pipe(impute_invalid_values, ['obs', 'obsm', 'choc', 'manv'], [-1, np.NaN])
                    .pipe(remove_duplicated_acc))

    # clean caracteristiques
    carac_df_clean = (carac_df
                    .pipe(drop_irrelevant_columns, ['gps', 'Accident_Id'])
                    .pipe(process_dates)
                    .pipe(impute_invalid_values, ['date', 'atm'], [np.NaN])
                    .pipe(drop_nans, ['Num_Acc', 'col', 'com'])
                    .pipe(impute_invalid_values, ['lum', 'int', 'col'], [-1])
                    .pipe(replace_with_most_frequent, ['lum', 'agg', 'atm'])
                    .pipe(remove_no_location))

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
                    .pipe(create_aug)
                    .pipe(create_dup_count)
                    .pipe(drop_irrelevant_columns, columns=['place', 'catu', 'secu1', 'secu2', 'secu3', 'num_veh', 'id_vehicule', 'id_usager']))

    return vehi_df_clean, carac_df_clean, lieux_df_clean, usager_df_clean

def merge_cleaned_datasets(vehi_df_clean, carac_df_clean, lieux_df_clean, usager_df_clean):
    vehi_usa = pd.merge(vehi_df_clean, usager_df_clean, on='aug', how='inner')
    vehi_usa = vehi_usa.drop(columns=['num_veh', 'Num_Acc_y'])
    vehi_usa = vehi_usa.rename(columns={'Num_Acc_x': 'Num_Acc'})

    velo_df = pd.merge(vehi_usa, lieux_df_clean, on='Num_Acc', how='left')
    all_datasets = pd.merge(velo_df, carac_df_clean, on='Num_Acc', how='left')
    all_datasets = remove_no_location(all_datasets)

    return all_datasets
