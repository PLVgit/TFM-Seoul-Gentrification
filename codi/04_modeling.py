import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import shap
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler


sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
ML_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "ml_outputs")
os.makedirs(ML_OUTPUT_DIR, exist_ok=True)

print("=== INICIANT EL PIPELINE DE MACHINE LEARNING ===")

print("\n[1/6] Carregant datasets...")
try:
    df_areas = pd.read_csv(os.path.join(CLEAN_DIR, "areas_clean.csv"))
    df_pop = pd.read_csv(os.path.join(CLEAN_DIR, "population_clean.csv"))
    df_sales = pd.read_csv(os.path.join(CLEAN_DIR, "sales_clean.csv"))
    df_stores = pd.read_csv(os.path.join(CLEAN_DIR, "stores_clean.csv"))
    df_ci = pd.read_csv(os.path.join(CLEAN_DIR, "change_indicators_clean.csv"))
    print(" -> Tots els arxius CSV carregats correctament.")
except Exception as e:
    print(f"Error carregant dades: {e}")
    sys.exit(1)

print("\n[2/6] Fusionant dades al nivell zona-trimestre...")

sales_agg = (
    df_sales.groupby(["year_quarter", "zone_code"])["monthly_sales_amount"]
    .sum()
    .reset_index()
)

store_cols = (
    ["opened_stores", "closed_stores", "franchise_stores"]
    if "opened_stores" in df_stores.columns
    else ["opened_store_num", "closed_store_num", "franchise_store_num"]
)
stores_agg = (
    df_stores.groupby(["year_quarter", "zone_code"])[store_cols]
    .sum()
    .reset_index()
)
stores_agg.rename(
    columns={
        store_cols[0]: "opened_stores",
        store_cols[1]: "closed_stores",
        store_cols[2]: "franchise_stores",
    },
    inplace=True,
)

pop_agg = (
    df_pop.groupby(["year_quarter", "zone_code"])["total_floating_pop"]
    .mean()
    .reset_index()
)

ci_agg = df_ci[
    ["year_quarter", "zone_code", "change_indicator_name"]
].drop_duplicates()

df_master = pd.merge(ci_agg, pop_agg, on=["year_quarter", "zone_code"], how="inner")
df_master = pd.merge(df_master, sales_agg, on=["year_quarter", "zone_code"], how="inner")
df_master = pd.merge(df_master, stores_agg, on=["year_quarter", "zone_code"], how="inner")

areas_spatial = df_areas[["zone_code", "x_coord", "y_coord"]].drop_duplicates()
df_master = pd.merge(df_master, areas_spatial, on="zone_code", how="left")
df_master = df_master.dropna()
df_master["year_quarter"] = df_master["year_quarter"].astype(int)

print(f" -> Matriu contemporania construida: {df_master.shape[0]} registres.")

print("\n[3/6] Creant el Target temporal t+1...")
target_mapping = {
    "Expansion": 1,
    "Dynamic": 1,
    "Stagnation": 0,
    "Contraction": 0,
}

df_master["commercial_change_class"] = df_master["change_indicator_name"].map(
    target_mapping
)
df_master = df_master.sort_values(["zone_code", "year_quarter"])
df_master["target_commercial_change_next"] = df_master.groupby("zone_code")[
    "commercial_change_class"
].shift(-1)
df_model = df_master.dropna(subset=["target_commercial_change_next"]).copy()
df_model["target_commercial_change_next"] = df_model[
    "target_commercial_change_next"
].astype(int)

print(" -> Distribucio de classes del Target t+1:")
print(
    df_model["target_commercial_change_next"]
    .value_counts(normalize=True)
    .sort_index()
    .map(lambda x: f"{x:.2%}")
)

print("\n[4/6] Aplicant divisio temporal...")
SPLIT_THRESHOLD = 20233

train_df = df_model[df_model["year_quarter"] <= SPLIT_THRESHOLD]
test_df = df_model[df_model["year_quarter"] > SPLIT_THRESHOLD]

print(f" -> Dades entrenament (t <= {SPLIT_THRESHOLD}): {train_df.shape[0]} registres.")
print(f" -> Dades test (t > {SPLIT_THRESHOLD}): {test_df.shape[0]} registres.")

# Model principal sense variables provinents directament de Change Indicators.
features = [
    "total_floating_pop",
    "monthly_sales_amount",
    "opened_stores",
    "closed_stores",
    "franchise_stores",
    "x_coord",
    "y_coord",
]

X_train = train_df[features]
y_train = train_df["target_commercial_change_next"]
X_test = test_df[features]
y_test = test_df["target_commercial_change_next"]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n[5/6] Entrenant XGBoost Classifier...")
positive_count = int(y_train.sum())
negative_count = int(len(y_train) - positive_count)
scale_pos_weight = negative_count / positive_count if positive_count else 1

xgb_model = xgb.XGBClassifier(
    n_estimators=150,
    learning_rate=0.05,
    max_depth=6,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric="auc",
)
xgb_model.fit(X_train_scaled, y_train)
xgb_preds = xgb_model.predict(X_test_scaled)
xgb_probs = xgb_model.predict_proba(X_test_scaled)[:, 1]

print("\n[6/6] Avaluant resultats i generant SHAP...")
print("\n--- Resultats XGBoost (Target t+1) ---")
report = classification_report(
    y_test,
    xgb_preds,
    target_names=["Sense patro t+1", "Patro comercial t+1"],
)
print(report)
auc_score = roc_auc_score(y_test, xgb_probs)
print(f"ROC-AUC Score: {auc_score:.4f}")

plt.figure(figsize=(6, 5))
cm = confusion_matrix(y_test, xgb_preds)
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Sense patro", "Patro comercial"],
    yticklabels=["Sense patro", "Patro comercial"],
)
plt.title("Matriu de confusio (XGBoost) - Target t+1")
plt.ylabel("Valor real t+1")
plt.xlabel("Valor predit t+1")
cm_path = os.path.join(ML_OUTPUT_DIR, "confusion_matrix_xgb.png")
plt.savefig(cm_path, dpi=150, bbox_inches="tight")
plt.close()

print(" -> Calculant Valors SHAP...")
X_test_df = pd.DataFrame(X_test_scaled, columns=features)
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test_df)

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test_df, show=False)
plt.title("Impacte de les variables en la classificacio comercial t+1")
shap_path = os.path.join(ML_OUTPUT_DIR, "shap_summary_xgb.png")
plt.savefig(shap_path, dpi=150, bbox_inches="tight")
plt.close()

print("\n=== PROCES FINALITZAT ===")
print(f" -> Resultats guardats a: {ML_OUTPUT_DIR}")
