import pandas as pd
import json
import os
import sys
from korean_romanizer.romanizer import Romanizer

# Ensure UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Definició de rutes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
val_map_path = os.path.join(BASE_DIR, 'value_translations.json')
data_clean_path = os.path.join(BASE_DIR, 'data', 'clean', 'areas_clean.csv')

# Read current JSON
with open(val_map_path, 'r', encoding='utf-8') as f:
    val_translations = json.load(f)

# Load data
df = pd.read_csv(data_clean_path, low_memory=False)

def contains_korean(text):
    if not isinstance(text, str):
        return False
    # Check if there's any hangul character in the string
    return any('\uAC00' <= char <= '\uD7A3' for char in text)

def romanize_korean(text):
    if pd.isna(text) or not contains_korean(str(text)):
        return text
    try:
        romanized = Romanizer(str(text)).romanize()
        # Capitalize and make it look clean
        return romanized.title()
    except Exception as e:
        return text

columns_to_translate = ['dong_name', 'zone_name']

for col in columns_to_translate:
    if col in df.columns:
        if col not in val_translations:
            val_translations[col] = {}
        
        unique_vals = df[col].dropna().unique()
        for v in unique_vals:
            if v not in val_translations[col] and contains_korean(v):
                val_translations[col][v] = romanize_korean(v)

# Save back to JSON
with open(val_map_path, 'w', encoding='utf-8') as f:
    json.dump(val_translations, f, ensure_ascii=False, indent=4)

print("S'han afegit les traduccions (romanització) al value_translations.json.")
