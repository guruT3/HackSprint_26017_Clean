"""
preprocessing.py
-----------------
Builds the shared preprocessing pipeline (ColumnTransformer) used for both
training and inference. Saving this pipeline together with the model
guarantees Flask applies EXACTLY the same transformation at prediction time
that was used during training - avoiding train/serve skew.
"""

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Feature groups used by the yield & price models
CATEGORICAL_FEATURES = ["crop", "soil_type", "irrigation", "season", "region"]

NUMERIC_FEATURES = [
    "farm_area", "rainfall", "temperature", "soil_ph", "soil_moisture",
    "seed_cost", "fertilizer_cost", "pesticide_cost", "labour_cost",
    "irrigation_cost", "machinery_cost", "other_cost",
    "previous_yield", "farming_experience",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def build_preprocessor():
    """Returns an unfitted ColumnTransformer combining OneHotEncoder for
    categorical columns and StandardScaler for numeric columns."""
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")
    numeric_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("num", numeric_transformer, NUMERIC_FEATURES),
        ]
    )
    return preprocessor
