from sklearn.preprocessing import OneHotEncoder, FunctionTransformer, Col
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
import datetime as dt


def preprocess_features(X: pd.DataFrame) -> np.ndarray:

    def create_sklearn_preprocessor() -> ColumnTransformer:

        ohe_categories = ['obs','obsm','choc','manv','trajet','locp','atp','etatp','catr','circ','vosp','prof','plan','surf','infra','situ','lum','int','col']

        # Création du pipeline ohe

        ohe_pipe = make_pipeline(
            ColumnTransformer(
                transformers=[
                    ('ohe', OneHotEncoder(categories='auto', sparse_output=False, handle_unknown='ignore'), ohe_categories)
                ],
                remainder='passthrough'
            )
        )

        # Création du pipeline grav
        grav_pipe = make_pipeline(
            ColumnTransformer(
                transformers=[
                    ('grav', FunctionTransformer(lambda x: x.map({1: 'Indemne', 2: 'Blessé léger',
                                                                3: 'Blessé hospitalisé', 4: 'Tué'}),
                                                validate=False), ['grav'])
                ],
                remainder='passthrough'
            )
        )



        def calculate_age(df):
            # Extrait les 4 premiers chiffres de 'Num_Acc' comme année de l'accident
            df['annee_accident'] = df['Num_Acc'].astype(str).str[:4]

            # Convertit 'annee_accident' en type entier
            df['annee_accident'] = df['annee_accident'].astype(int)

            # Calcul de l'âge à la date de l'accident
            df['age_at_accident'] = df['annee_accident'] - df['an_nais']

            # Supprime les colonnes intermédiaires si nécessaire
            df = df.drop(['annee_accident'], axis=1)

            return df

        # Création du pipeline
        age_pipe = make_pipeline(
            ColumnTransformer(
                transformers=[
                    ('age', FunctionTransformer(calculate_age, validate=False), ['Num_Acc', 'an_nais'])
                ],
                remainder='passthrough'
            )
        )


        final_pipeline = make_pipeline(
            ohe_pipe,
            grav_pipe,
            age_pipe,
            remainder='passthrough',
        # Garde les colonnes non utilisées
        )

        return final_pipeline

    preprocessor = create_sklearn_preprocessor()
    X_processed = preprocessor.fit_transform(X)

    print("✅ X_processed, with shape", X_processed.shape)

    return X_processed
