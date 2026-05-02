from pathlib import Path

import joblib

from app.ml_training.features import ALL_FEATURES


_APP_DIR = Path(__file__).resolve().parents[1]  # .../app
_MODEL_PATH = _APP_DIR / "ml_training" / "satisfaction_model.pkl"
model = joblib.load(str(_MODEL_PATH))


def predict_satisfaction(feature_dict):
    feature_vector = [feature_dict[f] for f in ALL_FEATURES]
    prediction = model.predict([feature_vector])[0]
    return float(prediction)