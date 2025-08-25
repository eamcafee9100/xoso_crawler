import shap
import numpy as np
from joblib import Memory

# Cache SHAP calculations để tiết kiệm tính toán
memory = Memory('./shap_cache', verbose=0)

@memory.cache
def optimize_shap_calculation(model, background_data, sample):
    """Tính SHAP values với tối ưu hóa bộ nhớ"""
    explainer = shap.TreeExplainer(
        model,
        background_data,
        feature_perturbation="interventional"
    )
    return explainer(sample, check_additivity=False)