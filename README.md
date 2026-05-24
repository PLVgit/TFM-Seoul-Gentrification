# TFM-Seoul-Gentrification

Repositori del Treball Final de Màster **“Anàlisi espacial i socioeconòmica de la gentrificació a la ciutat de Seül”**.

El projecte analitza patrons comercials i espacials associats a processos de transformació urbana a Seül mitjançant dades obertes, anàlisi exploratòria, visualització espacial i modelització predictiva.

## Estructura

```text
TFM-Seoul-Gentrification/
├── codi/       # Scripts Python del projecte
├── data/       # Dades i resultats generats
└── README.md
```

## Execució

Instal·lar les dependències:

```bash
pip install -r requirements.txt
```

Executar els scripts principals en ordre:

```bash
python codi/01_data_cleaning.py
python codi/02_add_translations.py
python codi/03_eda.py
python codi/04_modeling.py
```

Els resultats generats es desen principalment a:

```text
data/eda_outputs/
data/ml_outputs/
```

## Autor

Pol López Vidaller  
Màster en Ciència de Dades — Universitat Oberta de Catalunya
