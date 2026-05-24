import pandas as pd
import os
import sys
import glob
import json
import re

try:
    from korean_romanizer.romanizer import Romanizer
except ImportError:
    Romanizer = None

# Ensure UTF-8 output if running from certain terminals
sys.stdout.reconfigure(encoding='utf-8')

# Definició de rutes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLEAN_DIR = os.path.join(DATA_DIR, "clean")

# Crear carpeta clean si no existeix
os.makedirs(CLEAN_DIR, exist_ok=True)

# Diccionaris de traducció per a les columnes principals de cada arxiu
translations_area = {
    '상권_코드': 'zone_code',
    '상권_코드_명': 'zone_name',
    '엑스좌표_값': 'x_coord',
    '와이좌표_값': 'y_coord',
    '자치구_코드_명': 'gu_name',    # Districte Autònom
    '행정동_코드_명': 'dong_name',  # Barri
    '영역_면적': 'area_size'
}

translations_pop = {
    '기준_년분기_코드': 'year_quarter',
    '상권_코드': 'zone_code',
    '총_유동인구_수': 'total_floating_pop',
    '남성_유동인구_수': 'male_pop',
    '여성_유동인구_수': 'female_pop',
    '연령대_20_유동인구_수': 'pop_20s',
    '연령대_30_유동인구_수': 'pop_30s'
}

translations_stores = {
    '기준_년분기_코드': 'year_quarter',
    '상권_코드': 'zone_code',
    '서비스_업종_코드_명': 'service_type',
    '점포_수': 'total_stores',
    '개업_점포_수': 'opened_stores',
    '폐업_점포_수': 'closed_stores',
    '프랜차이즈_점포_수': 'franchise_stores'
}

translations_sales = {
    '기준_년분기_코드': 'year_quarter',
    '상권_코드': 'zone_code',
    '서비스_업종_코드_명': 'service_type',
    '당월_매출_금액': 'monthly_sales_amount',
    '당월_매출_건수': 'monthly_sales_cases'
}

translations_change = {
    '기준_년분기_코드': 'year_quarter',
    '상권_코드': 'zone_code',
    '상권_변화_지표': 'change_indicator',
    '상권_변화_지표_명': 'change_indicator_name',
    '운영_영업_개월_평균': 'operating_months_avg',
    '폐업_영업_개월_평균': 'closed_months_avg'
}

translations_workplace = {
    '기준_년분기_코드': 'year_quarter',
    '상권배후지_코드': 'zone_code',
    '총_직장_인구_수': 'total_workplace_pop'
}

# Aquí agrupem tots els arxius per categoria. Així si tenim múltiples anys, els llegirà tots i els fusionarà.
file_groups_to_process = {
    'Areas': {
        'patterns': ['서울시 상권분석서비스(영역-상권).csv'],
        'clean_name': 'areas_clean.csv',
        'col_map': translations_area
    },
    'Population': {
        'patterns': ['서울시 상권분석서비스(길단위인구-상권).csv'],
        'clean_name': 'population_clean.csv',
        'col_map': translations_pop
    },
    'Stores': {
        'patterns': [
            '서울시 상권분석서비스(점포-상권).csv', 
            '2019-2024/*점포-상권*.csv'
        ],
        'clean_name': 'stores_clean.csv',
        'col_map': translations_stores
    },
    'Sales': {
        'patterns': [
            '서울시 상권분석서비스(추정매출-상권).csv', 
            '2019-2024/*추정매출-상권*.csv'
        ],
        'clean_name': 'sales_clean.csv',
        'col_map': translations_sales
    },
    'Change Indicators': {
        'patterns': ['서울시 상권분석서비스(상권변화지표-상권).csv'],
        'clean_name': 'change_indicators_clean.csv',
        'col_map': translations_change
    },
    'Workplace Population': {
        'patterns': ['서울시 상권분석서비스(직장인구-상권배후지).csv', '서울시 상권분석서비스(직장인구-상권).csv'],
        'clean_name': 'workplace_pop_clean.csv',
        'col_map': translations_workplace
    }
}

print("--- Iniciant Neteja de Dades ---")

for group_name, info in file_groups_to_process.items():
    clean_filename = info['clean_name']
    col_map = info['col_map']
    
    print(f"\n>> Processant Grup: {group_name} -> {clean_filename}")
    
    df_list = []
    
    # Buscar tots els arxius que coincideixin amb els patrons
    for pattern in info['patterns']:
        search_path = os.path.join(DATA_DIR, pattern)
        matched_files = glob.glob(search_path)
        
        for file_path in matched_files:
            print(f"   Llegint: {os.path.basename(file_path)}...")
            try:
                # LLegim amb cp949 que és l'estàndard dels CSV coreans públics
                df_temp = pd.read_csv(file_path, encoding='cp949', low_memory=False)
                df_list.append(df_temp)
            except Exception as e:
                print(f"   [ERROR] No s'ha pogut processar {file_path}: {e}")
                
    if not df_list:
        print(f"   [AVÍS] No s'ha trobat cap arxiu per a {group_name}. Es salta.")
        continue
        
    # Concatenem tots els dataframes de l'any i descartem index antic
    df_combined = pd.concat(df_list, ignore_index=True)
    orig_rows, orig_cols = df_combined.shape
    print(f"   Mida combinada (abans de netejar): {orig_rows} files, {orig_cols} columnes.")
    
    # Filtrem i traduïm columnes per quedar-nos només amb les necessàries
    cols_to_keep = list(col_map.keys())
    existing_cols = [c for c in cols_to_keep if c in df_combined.columns]
    
    df_clean = df_combined[existing_cols].copy()
    df_clean.rename(columns=col_map, inplace=True)
    
    # Apliquem les traduccions de valors a les columnes si existeix el diccionari
    val_map_path = os.path.join(BASE_DIR, 'value_translations.json')
    if os.path.exists(val_map_path):
        with open(val_map_path, 'r', encoding='utf-8') as f:
            val_translations = json.load(f)
        for col, mapping in val_translations.items():
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].replace(mapping)
                
    # ---------------------------------------------------------
    # Auto-romanitzem columnes restants que tinguin text en coreà
    # ---------------------------------------------------------
    if Romanizer is not None:
        target_cols = ['dong_name', 'zone_name', 'gu_name']
        for col in target_cols:
            if col in df_clean.columns:
                unique_vals = df_clean[col].dropna().unique()
                romanize_dict = {}
                for val in unique_vals:
                    # Comprovem si té caràcters Hangul
                    if isinstance(val, str) and re.search(r'[\uAC00-\uD7A3]', val):
                        try:
                            # Romanitzem i adaptem el format (ex: Yeoksam1Dong)
                            romanized = Romanizer(val).romanize().title()
                            romanize_dict[val] = romanized
                        except Exception:
                            pass
                
                if romanize_dict:
                    print(f"   Romanitzant {len(romanize_dict)} valors únics a la columna '{col}'...")
                    df_clean[col] = df_clean[col].replace(romanize_dict)
    elif 'dong_name' in df_clean.columns or 'zone_name' in df_clean.columns:
        print("   [AVÍS] 'korean_romanizer' no està instal·lat. Instal·la'l amb 'pip install korean_romanizer' per romanitzar-ho automàticament.")

    # Comprovar Valors Nuls (Missing Values)
    null_counts = df_clean.isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls > 0:
        print(f"   S'han trobat {total_nulls} valors nuls en total.")
    else:
        print("   No hi ha valors nuls detectats a les columnes seleccionades.")
        
    # Neteja de duplicats
    # Important: Alguns registres es poden solapar si els CSV anuals i el de 2025 contenen dades duplicades d'un trimestre
    dups = df_clean.duplicated().sum()
    if dups > 0:
        print(f"   S'han eliminat {dups} files duplicades (creuament d'arxius).")
        df_clean = df_clean.drop_duplicates()
        
    # Guardem l'arxiu net a data/clean/ 
    out_path = os.path.join(CLEAN_DIR, clean_filename)
    df_clean.to_csv(out_path, index=False, encoding='utf-8')
    print(f"   Arxiu desat correctament com a: {clean_filename} amb {len(df_clean)} files finals.")

print("\n--- Finalitzat ! ---")
print("S'han concatenat, traduït els noms de les columnes i netejat els arxius clau.")
print("Pots procedir a executar el script d'EDA (02) ! ")
