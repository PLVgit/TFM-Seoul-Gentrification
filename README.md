# TFM: Anàlisi Espacial i Predicció de Gentrificació a Seül

## 📊 Descripció General

Treball Final de Màster en Ciència de Dades que analitza els indicadors comercials associats a processos de gentrificació a la ciutat de Seül (Corea del Sud) mitjançant **Machine Learning** (XGBoost) i **Sistemes d'Informació Geogràfica (SIG)**.

### Objectius Principals
- ✅ Avaluar estadísticament patrons de transformació comercial a Seül (2019-2024)
- ✅ Entrenar un model XGBoost per predir canvis comercials trimestrals amb AUC=0.88
- ✅ Cartografiar territorialment indicadors associats a gentrificació comercial
- ✅ Proporcionar resultats interpretables mitjançant anàlisi SHAP

---

## 🗂️ Estructura del Repositori

```
TFM-Seoul-Gentrification/
│
├── codi/                          # Scripts Python per processar dades i entrenar model
│   ├── 00_analyze_csv.py         # Exploració inicial
│   ├── 01_data_cleaning.py       # Neteja i preprocessament
│   ├── 02_add_translations.py    # Traducció de categories (Hangul → Anglès)
│   ├── 03_eda.py                 # Anàlisi Exploratòria (EDA)
│   └── 04_modeling.py            # Model XGBoost + SHAP
│
├── data/                          # Dades en diversos estadis
│   ├── raw/                       # Fitxers originals (Seoul Open Data Plaza)
│   ├── clean/                     # Dades processades i harmonitzades
│   ├── eda_outputs/               # Gràfics EDA (heatmaps, distribucions)
│   └── ml_outputs/                # Resultats model (matriu confusió, SHAP)
│
├── memoria/                       # Documentació acadèmica
│   └── M1_Proposta_Pol.tex       # Memòria en LaTeX
│
├── README.md                      # Aquest fitxer
└── .gitignore                     # Fitxers a excloure del repo
```

---

## 🧮 Metodologia Resumida

### Font de Dades
- **Seoul Open Data Plaza** (Seoul Credit Guarantee Foundation)
- **Variables comercials**: Afluència, vendes estimades, obertures/tancaments, franquícies (2019-2024)

### Model Predictiu
- **Algorisme**: XGBoost (eXtreme Gradient Boosting)
- **Target**: Classificació binària de canvi comercial (Dynamic/Expansion vs altres)
- **Validació temporal**: Train ≤ 2023Q3 | Test > 2023Q3
- **Mètriques**: AUC-ROC = **0.8835**, Accuracy = **80%**, F1 = 0.77
- **Interpretabilitat**: Valors SHAP

### Variables Incloses (7 predictors + 1 Target)
1. `total_floating_pop` - Afluència de vianants
2. `monthly_sales_amount` - Vendes mensuals
3. `opened_stores` - Obertures noves
4. `closed_stores` - Tancaments
5. `franchise_stores` - Franquícies corporatives
6. `x_coord, y_coord` - Localització espacial
7. **Target (t+1)**: `change_indicator` (binaritzat)

---

## 📦 Requisits i Instal·lació

### Dependències Python
```bash
pip install pandas numpy scikit-learn xgboost shap geopandas folium matplotlib seaborn
```

### Versions Recomanades
```
pandas >= 1.3.0
numpy >= 1.20.0
xgboost >= 1.5.0
scikit-learn >= 0.24.0
shap >= 0.40.0
geopandas >= 0.9.0
```

---

## 🚀 Com Executar

### 1. Preparar l'Entorn
```bash
cd TFM-Seoul-Gentrification
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Executar els Scripts en Ordre
```bash
python codi/01_data_cleaning.py    # Neteja dades
python codi/02_add_translations.py # Traducció de categories
python codi/03_eda.py              # Anàlisi exploratòria
python codi/04_modeling.py         # Entrenar model XGBoost
```

### 3. Revisar Resultats
- **Gràfics EDA**: `data/eda_outputs/`
- **Model outputs**: `data/ml_outputs/` (confusió matrix, SHAP)

---

## 🔍 Resultats Clau

### Performance del Model
| Métrica | Valor |
|---------|-------|
| AUC-ROC | 0.8835 |
| Accuracy | 80% |
| Precision (Class 1) | 0.83 |
| Recall (Class 1) | 0.71 |
| F1-Score | 0.77 |

### Variables més Importants (SHAP)
1. **Vendes mensuals** (`monthly_sales_amount`) - Predictor més fort
2. **Franquícies** (`franchise_stores`) - Penetració corporativa
3. **Obertures** (`opened_stores`) - Dinamisme comercial
4. **Localització** (`x_coord, y_coord`) - Component espacial

---

## 📝 Autor i Context

**Autor**: Pol López Vidaller  
**Directora del TFM**: Anna Muñoz Bollas  
**Programa**: Màster en Ciència de Dades (UOC)  
**Data de Lliurament**: Juny 2026  

### Alineació ODS
- **ODS 11** - Ciutats i comunitats sostenibles
- **ODS 10** - Reducció de les desigualtats

---

## ⚠️ Limitacions i Futures Línies de Recerca

### Limitacions Actuals
- No s'incorporen dades directes de preus de lloguer comercial
- Falta informació de canvi demogràfic residencial
- COVID-19 afecta les tendències (disrupció 2020-2021)

### Millores Futures
- Integrar dades de mercat hipotecari residencial
- Implementar **Graph Neural Networks** (GNNs) per modelar effectes d'spillover
- Replicar metodologia a altres ciutats coreanes (Busan, Daegu)

---

## 📄 Llicència

Aquest projecte es distribueix sota llicència **Creative Commons Attribution 4.0** (CC-BY 4.0).

---

## 📞 Contacte i Dubtes

Per a dubtes sobre el codi, dades o metodologia, contacta via:
- 📧 Email: pol.lopez@uoc.edu
- 🔗 GitHub: @PLVgit

---

**Darrera actualització**: 24 de maig de 2026
