from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

def tune_xgboost_parameters(X, y):
    param_grid = {
        'n_estimators': [100, 150, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0]
    }
    
    model = XGBClassifier()
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        n_jobs=-1,
        verbose=2
    )
    
    grid_search.fit(X, y)
    return grid_search.best_params_