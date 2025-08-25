import pandas as pd
import lightgbm as lgb
import shap
import matplotlib.pyplot as plt
from memory_profiler import profile
import os

os.environ['SHAP_DISABLE_TQDM'] = '1'  # Tắt progress bar
os.environ['LIGHTGBM_DISABLE_OPENMP'] = '1'  # Tắt đa luồng
@profile
def main():
    # 1. Load và xử lý dữ liệu
    data = pd.read_csv('lottery_data.csv', nrows=5000)  # Giới hạn dòng
    features = data.drop(['date', 'special_prize'], axis=1).select_dtypes(include='number').columns.tolist()[:10]  # Chọn 10 features số đầu tiên
    X = data[features].fillna(0).astype('float32')
    y = data['special_prize'].str[-2:].astype(int)  # Lấy 2 số cuối giải đặc biệt

    # 2. Huấn luyện mô hình đơn giản
    model = lgb.LGBMRegressor(
        num_leaves=15,
        max_depth=3,
        n_estimators=50,
        random_state=42
    )
    model.fit(X, y)

    # 3. Tính SHAP values với tối ưu
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X.iloc[:500])  # Chỉ tính cho 500 mẫu

    # 4. Lưu visualization nhẹ
    plt.figure(figsize=(10,6))
    shap.summary_plot(shap_values, X.iloc[:500], show=False)
    plt.savefig('shap_summary.png', bbox_inches='tight', dpi=100)
    plt.close()

    # 5. Giải thích dự đoán mẫu
    sample_idx = 0
    shap.force_plot(
        explainer.expected_value, 
        shap_values[sample_idx], 
        X.iloc[sample_idx],
        show=False,
        matplotlib=True
    )
    plt.savefig('shap_force.png', bbox_inches='tight', dpi=100)
    plt.close()

if __name__ == "__main__":
    main()