import pandas as pd
import os
import sys

# Windows console encoding workaround for Korean
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(BASE_DIR, "data", "raw")

files = [
    "서울시 상권분석서비스(길단위인구-상권).csv",
    "서울시 상권분석서비스(영역-상권).csv",
    "서울시 상권분석서비스(점포-상권).csv",
    "서울시 상권분석서비스(추정매출-상권).csv"
]

encodings = ['cp949', 'euc-kr', 'utf-8']

for file in files:
    file_path = os.path.join(data_dir, file)
    print(f"\n======================================")
    print(f"FILE: {file}")
    
    if not os.path.exists(file_path):
        print("File not found!")
        continue
        
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, nrows=3)
            print(f"Successfully read with encoding: {enc}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            break
            
    if df is not None:
        print("\n--- SHAPE (of full file, approx) ---")
        try:
           # Read just shapes to avoid memory bloat
           # df_full = pd.read_csv(file_path, encoding=enc, usecols=[0])
           # print(f"Total Rows: {len(df_full)}")
           pass
        except:
            pass
            
        print("\n--- COLUMNS ---")
        for col in df.columns:
            print(col)
        print("\n--- FIRST ROW ---")
        print(df.iloc[0].to_dict())
    else:
        print("Could not read file with standard encodings.")
