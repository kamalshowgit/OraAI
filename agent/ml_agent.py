import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np

from ingestion.db_config import DB_PATH
from sqlalchemy import create_engine

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")

def load_data(table_name: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        raise HTTPException(status_code=400, detail="Database not found.")
    engine = get_engine()
    try:
        df = pd.read_sql_table(table_name, engine)
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load table {table_name}: {e}")

trained_models = {}

class TrainRequest(BaseModel):
    table_name: str
    target_column: str
    features: Optional[List[str]] = None
    id_column: Optional[str] = None

class ExplainRequest(BaseModel):
    model_id: str
    row_id: Any

class EvaluateRequest(BaseModel):
    model_id: str
    test_table_name: str

@router.get("/eda")
def get_eda(table_name: str):
    df = load_data(table_name)
    desc = df.describe(include='all').to_dict()
    missing = df.isnull().sum().to_dict()
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    safe_desc = {}
    for col, stats in desc.items():
        safe_desc[col] = {}
        for stat_name, val in stats.items():
            if pd.isna(val) or (isinstance(val, float) and np.isinf(val)):
                safe_desc[col][stat_name] = None
            else:
                safe_desc[col][stat_name] = val

    return {
        "table_name": table_name,
        "summary": safe_desc,
        "missing_values": missing,
        "dtypes": dtypes,
        "columns": list(df.columns),
        "total_rows": len(df)
    }

@router.post("/train")
def train_model(req: TrainRequest):
    df = load_data(req.table_name)
    
    if req.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column {req.target_column} not found.")
        
    features = req.features if req.features else [col for col in df.columns if col not in [req.target_column, req.id_column]]
    
    X = df[features].copy()
    y = df[req.target_column].copy()
    
    for col in X.columns:
        if X[col].dtype == 'object' or str(X[col].dtype) == 'category':
            X[col] = X[col].fillna('Missing')
        else:
            X[col] = X[col].fillna(X[col].median() if not pd.isna(X[col].median()) else 0)
            
    encoders = {}
    for col in X.columns:
        if X[col].dtype == 'object' or str(X[col].dtype) == 'category':
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
            
    target_encoder = None
    if y.dtype == 'object' or str(y.dtype) == 'category':
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y.astype(str))
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    results = []
    trained_instances = {}
    
    for name, model in models.items():
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
        acc = accuracy_score(y_test, preds)
        
        results.append({
            "model_name": name,
            "accuracy": float(acc)
        })
        trained_instances[name] = model

    model_id = f"{req.table_name}_{req.target_column}"
    
    trained_models[model_id] = {
        "models": trained_instances,
        "scaler": scaler,
        "features": features,
        "encoders": encoders,
        "target_encoder": target_encoder,
        "id_column": req.id_column,
        "target_column": req.target_column,
        "table_name": req.table_name,
    }
    
    return {
        "model_id": model_id,
        "results": results,
        "message": f"Successfully trained ensemble models using {len(features)} features."
    }

@router.post("/explain")
def explain_prediction(req: ExplainRequest):
    if req.model_id not in trained_models:
        raise HTTPException(status_code=404, detail="Model not found. Train it first.")
        
    model_data = trained_models[req.model_id]
    df = load_data(model_data["table_name"])
    
    id_col = model_data["id_column"]
    if not id_col or id_col not in df.columns:
        raise HTTPException(status_code=400, detail="ID column not specified during training or not found.")
        
    row = df[df[id_col].astype(str) == str(req.row_id)]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Row with ID {req.row_id} not found in table.")
        
    row = row.iloc[0:1]
    
    X = row[model_data["features"]].copy()
    original_X = X.copy()
    
    for col in X.columns:
        if col in model_data["encoders"]:
            le = model_data["encoders"][col]
            val = X[col].fillna('Missing').astype(str).values[0]
            if val in le.classes_:
                X[col] = le.transform([val])
            else:
                X[col] = -1
        else:
            X[col] = X[col].fillna(0)
            
    X_scaled = model_data["scaler"].transform(X)
    
    explanations = []
    
    for name, model in model_data["models"].items():
        is_linear = name == "Logistic Regression"
        input_data = X_scaled if is_linear else X
        
        prediction = model.predict(input_data)[0]
        
        prob = None
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(input_data)[0]
            prob = float(max(prob))
            
        if model_data["target_encoder"]:
            prediction_label = model_data["target_encoder"].inverse_transform([prediction])[0]
        else:
            prediction_label = prediction
            
        derivation = []
        if is_linear:
            classes = list(model.classes_)
            if len(classes) == 2:
                class_idx = 0
            else:
                class_idx = classes.index(prediction)
                
            coefs = model.coef_[class_idx]
            contribs = np.abs(coefs * X_scaled[0])
            top_idx = np.argsort(contribs)[::-1][:4]
            for idx in top_idx:
                feat = model_data["features"][idx]
                val = original_X[feat].values[0]
                imp = float(contribs[idx])
                derivation.append({"feature": feat, "value": str(val) if not pd.isna(val) else "Missing", "importance": imp, "type": "Coefficient Impact"})
        else:
            importances = model.feature_importances_
            top_idx = np.argsort(importances)[::-1][:4]
            for idx in top_idx:
                feat = model_data["features"][idx]
                val = original_X[feat].values[0]
                imp = float(importances[idx])
                derivation.append({"feature": feat, "value": str(val) if not pd.isna(val) else "Missing", "importance": imp, "type": "Tree Feature Importance"})
                
        explanations.append({
            "model_name": name,
            "prediction": str(prediction_label),
            "probability": prob,
            "derivation": derivation
        })
        
    return {
        "row_id": req.row_id,
        "explanations": explanations,
        "message": "Ensemble explanation generated."
    }

@router.post("/evaluate")
def evaluate_model(req: EvaluateRequest):
    if req.model_id not in trained_models:
        raise HTTPException(status_code=404, detail="Model not found. Train it first.")
        
    model_data = trained_models[req.model_id]
    df = load_data(req.test_table_name)
    
    target = model_data["target_column"]
    if target not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column {target} missing in test table.")
        
    X = df[model_data["features"]].copy()
    y = df[target].copy()
    
    for col in X.columns:
        if col in model_data["encoders"]:
            le = model_data["encoders"][col]
            X[col] = X[col].fillna('Missing').astype(str)
            X[col] = X[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
        else:
            X[col] = X[col].fillna(X[col].median() if pd.api.types.is_numeric_dtype(X[col]) else 0)
            
    if model_data["target_encoder"]:
        y = y.astype(str)
        valid_idx = y.isin(model_data["target_encoder"].classes_)
        X = X[valid_idx]
        y = y[valid_idx]
        y = model_data["target_encoder"].transform(y)
        
    if len(y) == 0:
        raise HTTPException(status_code=400, detail="No valid target rows found to evaluate.")
        
    X_scaled = model_data["scaler"].transform(X)
    
    results = []
    for name, model in model_data["models"].items():
        input_data = X_scaled if name == "Logistic Regression" else X
        preds = model.predict(input_data)
        acc = accuracy_score(y, preds)
        results.append({
            "model_name": name,
            "accuracy": float(acc)
        })
        
    return {
        "test_table": req.test_table_name,
        "rows_evaluated": len(y),
        "results": results
    }