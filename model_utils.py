import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

def train_model_by_country(df_data, country_name, model_path='models/random_forest_model.pkl', features_path='models/model_features.pkl'):
    filtered_df = df_data[df_data['country'] == country_name]

    if filtered_df.empty:
        raise ValueError(f"Tidak ada data untuk negara: {country_name}")

    X = filtered_df.drop(columns=['country', 'iso_code', 'total_ghg', 'Unnamed: 0', 'year'])
    y = filtered_df['total_ghg']

    X = pd.get_dummies(X)
    X = X[y.notna()]
    y = y.dropna()
    X = X.reset_index(drop=True)
    y = y.reset_index(drop=True)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, model_path)
    joblib.dump(X.columns.tolist(), features_path)

    importances = model.feature_importances_
    importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances})
    importance_df = importance_df.sort_values(by='Importance', ascending=False)

    return importance_df
