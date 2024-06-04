from typing import List, Tuple

import pandas as pd
import scipy
from sklearn.feature_extraction import DictVectorizer


def export_processed_data(
    df: pd.DataFrame,
    dv: DictVectorizer = None,
    features: List[str] = ["PULocationID", "DOLocationID"],
    target: str = "duration",
) -> Tuple[scipy.sparse.csr_matrix, scipy.sparse.csr_matrix, DictVectorizer]:

    dicts = df[features].to_dict(orient="records")

    if dv is None:
        # Training data, fit and transform
        dv = DictVectorizer()
        X = dv.fit_transform(dicts)
    else:
        # Testing data, just transform
        X = dv.transform(dicts)
    y = df[target]
    return X, y, dv
