import pandas as pd
import os
import sys
import json

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
EDA_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "eda_outputs")

os.makedirs(EDA_OUTPUT_DIR, exist_ok=True)

# List of files to analyze
files = {
    'Areas': 'areas_clean.csv',
    'Population': 'population_clean.csv',
    'Stores': 'stores_clean.csv',
    'Sales': 'sales_clean.csv',
    'Change Indicators': 'change_indicators_clean.csv',
    'Workplace Population': 'workplace_pop_clean.csv'
}

dataframes = {}

print("--- Iniciant Exploratory Data Analysis (EDA) ---")

# 1. Carregar dades
for name, filename in files.items():
    file_path = os.path.join(CLEAN_DIR, filename)
    if os.path.exists(file_path):
        dataframes[name] = pd.read_csv(file_path, encoding='utf-8')
        print(f"[{name}] Carregat correctament. Forma: {dataframes[name].shape}")
    else:
        print(f"[AVÍS] No s'ha trobat l'arxiu {filename} a {CLEAN_DIR}")

# 2. Comprovació de periodes temporals (Any i Trimestre)
print("\n--- Anàlisi de Periodes Temporals (year_quarter) ---")
temporal_ranges = {}
for name, df in dataframes.items():
    if 'year_quarter' in df.columns:
        # year_quarter normalment té format YYYYQ, e.g., 20231 (primer trimestre del 2023)
        min_period = df['year_quarter'].min()
        max_period = df['year_quarter'].max()
        temporal_ranges[name] = (min_period, max_period)
        print(f"{name:25s} | Min: {min_period} | Max: {max_period} | Total Registres Temporals Unics: {df['year_quarter'].nunique()}")
        
# 3. Exploració de valors únics per a columnes categòriques (per a la traducció!)
print("\n--- Extracció de categories per a la traducció ---")
categorical_cols_to_extract = {
    'gu_name': 'Areas',
    'dong_name': 'Areas',
    'service_type': ['Stores', 'Sales'],
    'change_indicator_name': 'Change Indicators'
}

unique_values = {}

for col, src in categorical_cols_to_extract.items():
    if isinstance(src, list):
        sources = src
    else:
        sources = [src]
        
    combined_uniques = set()
    for s in sources:
        if s in dataframes and col in dataframes[s].columns:
            combined_uniques.update(dataframes[s][col].dropna().unique().tolist())
            
    unique_values[col] = sorted(list(combined_uniques))
    print(f"Columna '{col}': {len(unique_values[col])} valors únics (Extrets de {sources})")

# Desem els valors únics per poder construir els diccionaris de traducció
dict_output_path = os.path.join(EDA_OUTPUT_DIR, 'unique_categorical_values.json')
with open(dict_output_path, 'w', encoding='utf-8') as f:
    json.dump(unique_values, f, ensure_ascii=False, indent=4)
print(f"-> S'han desat els valors únics a: {dict_output_path}")
print("-> Recomanació: Obre aquest arxiu JSON per crear els diccionaris de reemplaçament per al script de Neteja.")

# 4. Verificació de Nulls i Qualitat de Dades (Data Quality)
print("\n--- Verificació de Valors Nuls (Data Quality) ---")
for name, df in dataframes.items():
    total_nulls = df.isnull().sum().sum()
    if total_nulls == 0:
        print(f"[{name}]: 0 Nuls. Integritat del 100%.")
    else:
        print(f"[{name}]: S'han detectat {total_nulls} nuls repartits en les columnes.")

# 5. Estadístiques descriptives bàsiques per a columnes numèriques
print("\n--- Estadístiques Bàsiques i Generació de Figures (Plots) ---")
import matplotlib.pyplot as plt

if 'Population' in dataframes:
    print("\n[Població (Population)]")
    print(dataframes['Population'][['total_floating_pop']].describe().map(lambda x: f"{x:,.0f}"))

if 'Sales' in dataframes:
    print("\n[Vendes (Sales)]")
    print(dataframes['Sales'][['monthly_sales_amount']].describe().map(lambda x: f"{x:,.0f}"))

if 'Change Indicators' in dataframes:
    print("\n[Indicadors de Canvi Comercials (Change Indicators)]")
    print(">> Distribució de categories d'estat:")
    print(dataframes['Change Indicators']['change_indicator_name'].value_counts())
    
    # Generar distribució de mortalitat comercial (Histogrames tancament/operativitat)
    plt.figure(figsize=(10, 6))
    plt.hist(dataframes['Change Indicators']['operating_months_avg'].dropna(), bins=50, color='royalblue', label='Mesos Operatius', alpha=0.6)
    plt.hist(dataframes['Change Indicators']['closed_months_avg'].dropna(), bins=50, color='crimson', label='Mesos al Tancar', alpha=0.6)
    plt.title('Distribució Bimodal: Temps Vida Comercial a Seül (Mesos)')
    plt.xlabel('Mesos')
    plt.ylabel('Freqüència (Zones/Registres)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    out_hist = os.path.join(EDA_OUTPUT_DIR, 'business_lifespan_dist.png')
    plt.savefig(out_hist, dpi=150)
    plt.close()
    print(f" -> Gràfic de temps de vida desat a: {out_hist}")

    # Idea 2: Evolució temporal d'obertures i clausures
    if 'Stores' in dataframes and 'year_quarter' in dataframes['Stores'].columns:
        df_stores = dataframes['Stores']
        open_col = 'opened_stores' if 'opened_stores' in df_stores.columns else ('opened_store_num' if 'opened_store_num' in df_stores.columns else None)
        close_col = 'closed_stores' if 'closed_stores' in df_stores.columns else ('closed_store_num' if 'closed_store_num' in df_stores.columns else None)
        
        if open_col and close_col:
            df_trend = df_stores.groupby('year_quarter')[[open_col, close_col]].sum().reset_index()
            df_trend['year_quarter'] = df_trend['year_quarter'].astype(str)
            df_trend = df_trend.sort_values('year_quarter')
            
            plt.figure(figsize=(12, 6))
            plt.plot(df_trend['year_quarter'], df_trend[open_col], marker='o', color='forestgreen', label='Noves Obertures', linewidth=2)
            plt.plot(df_trend['year_quarter'], df_trend[close_col], marker='o', color='firebrick', label='Clausures', linewidth=2)
            
            plt.title("Evolució Temporal de la Dinàmica Comercial a Seül", fontsize=14)
            plt.xlabel("Any i Trimestre", fontsize=12)
            plt.ylabel("Nombre Total de Comerços", fontsize=12)
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            
            out_trend = os.path.join(EDA_OUTPUT_DIR, 'stores_temporal_trend.png')
            plt.savefig(out_trend, dpi=150)
            plt.close()
            print(f" -> Gràfic d'evolució temporal desat a: {out_trend}")

    # Idea 3: Contrast de Supervivència segons l'Estat del Barri
    if 'Change Indicators' in dataframes:
        df_ci = dataframes['Change Indicators'].dropna(subset=['operating_months_avg', 'change_indicator_name'])
        if not df_ci.empty:
            plt.figure(figsize=(10, 6))
            sns.kdeplot(data=df_ci, x='operating_months_avg', hue='change_indicator_name', 
                        fill=True, common_norm=False, palette='Set1', alpha=0.5, linewidth=2)
            
            plt.title("Mortalitat Comercial: Mesos Operatius segons Estat de Gentrificació", fontsize=14)
            plt.xlabel("Mesos Operatius Mitjans", fontsize=12)
            plt.ylabel("Densitat de Probabilitat", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            
            out_kde = os.path.join(EDA_OUTPUT_DIR, 'survival_kde_by_indicator.png')
            plt.savefig(out_kde, dpi=150)
            plt.close()
            print(f" -> Gràfic de densitat per indicador desat a: {out_kde}")

# 6. Representació Espacial Bàsica (SIG) - Mapes de recintes amb Contextily
if 'Areas' in dataframes and 'x_coord' in dataframes['Areas'].columns and 'y_coord' in dataframes['Areas'].columns:
    print("\n[Representació Espacial (SIG)]")
    try:
        import geopandas as gpd
        import contextily as cx
        
        df_areas_map = dataframes['Areas'].dropna(subset=['x_coord', 'y_coord'])
        
        # Geopandas directament amb coordenades TM coreanes
        gdf_areas = gpd.GeoDataFrame(
            df_areas_map, 
            geometry=gpd.points_from_xy(df_areas_map['x_coord'], df_areas_map['y_coord']),
            crs="EPSG:5181"
        )
        
        # Conversió Web Mercator
        gdf_wm_areas = gdf_areas.to_crs(epsg=3857)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        gdf_wm_areas.plot(ax=ax, color='darkorange', alpha=0.6, markersize=25, edgecolor='black', linewidth=0.1)
        
        try:
            cx.add_basemap(ax, crs=gdf_wm_areas.crs.to_string(), source=cx.providers.CartoDB.Positron)
        except Exception as basemap_e:
            print(f" [Avís] No s'ha pogut afegir el fons del mapa a la distribució: {basemap_e}")
            
        plt.title('Mapa General: Distribució de Zones Comercials Actives a Seül', fontsize=15)
        plt.xlabel('Longitud (Web Mercator)')
        plt.ylabel('Latitud (Web Mercator)')
        plt.axis('equal')
        
        out_map = os.path.join(EDA_OUTPUT_DIR, 'spatial_distribution_map.png')
        plt.savefig(out_map, dpi=300, bbox_inches='tight')
        plt.close()
        print(f" -> Mapa geoespacial (SIG sobre cartografia) generat i desat a: {out_map}")
    except Exception as e:
        print(f" [Error] Fallida processant l'arxiu genèric SIG: {e}")

# 7. Representació Espacial Multi-Variable (Mapa de Calor) amb Folium i Pyproj
if 'Areas' in dataframes and 'Population' in dataframes:
    print("\n[Representació Espacial Interactiva SIG (Folium)]")
    try:
        import folium
        from folium.plugins import HeatMap
        from pyproj import Transformer
        
        # Obtenim les àrees amb coordenades viables
        df_areas = dataframes['Areas'].dropna(subset=['x_coord', 'y_coord', 'zone_code'])
        
        # Agrupem la població mitjana per a cada zona comercial
        pop_avg = dataframes['Population'].groupby('zone_code')['total_floating_pop'].mean().reset_index()
        
        # Creuem àrees amb població
        df_geo = pd.merge(df_areas, pop_avg, on='zone_code', how='inner')
        
        # Sistema de coordenades coreà EPSG:5181 -> WGS84 (Lat/Lon EPSG:4326)
        transformer = Transformer.from_crs("epsg:5181", "epsg:4326", always_xy=True)
        
        lats, lons, weights = [], [], []
        
        for idx, row in df_geo.iterrows():
            # pyproj rep (x, y) i retorna (lon, lat) amb always_xy=True
            lon, lat = transformer.transform(row['x_coord'], row['y_coord'])
            lats.append(lat)
            lons.append(lon)
            weights.append(row['total_floating_pop'])
            
        df_geo['lat'] = lats
        df_geo['lon'] = lons
        
        # Normalitzem el pes (perquè HeatMap no es saturet amb valors de milions)
        max_pop = df_geo['total_floating_pop'].max()
        df_geo['weight_norm'] = df_geo['total_floating_pop'] / max_pop
        
        # Creem el mapa centrat a Seül
        map_seoul = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="cartodb positron")
        
        # Afegim el HeatMap
        heat_data = [[row['lat'], row['lon'], row['weight_norm']] for index, row in df_geo.iterrows()]
        HeatMap(heat_data, radius=12, blur=15, max_zoom=13).add_to(map_seoul)
        
        out_html = os.path.join(EDA_OUTPUT_DIR, 'seoul_population_heatmap.html')
        map_seoul.save(out_html)
        print(f" -> Mapa HTML Geoespacial interactiu generat a: {out_html}")
        
        # Generem la versió fotogràfica (PNG) per a la memòria Latex amb Matplotlib + Contextily (Basemap de Seül)
        import geopandas as gpd
        import contextily as cx
        
        # Creem un GeoDataFrame a partir de les latituds i longituds (EPSG:4326)
        gdf = gpd.GeoDataFrame(
            df_geo, 
            geometry=gpd.points_from_xy(df_geo['lon'], df_geo['lat']),
            crs="EPSG:4326"
        )
        
        # Contextily requereix mapes en format Web Mercator (EPSG:3857)
        gdf_wm = gdf.to_crs(epsg=3857)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        import seaborn as sns
        
        # Pintem un mapa de calor continu usant KDE de Seaborn
        sns.kdeplot(
            x=gdf_wm.geometry.x, 
            y=gdf_wm.geometry.y, 
            weights=gdf_wm['total_floating_pop'], 
            cmap='YlOrRd', 
            fill=True, 
            alpha=0.6, 
            ax=ax, 
            levels=50,
            bw_adjust=0.5,
            cbar=True,
            cbar_kws={'fraction': 0.046, 'pad': 0.04, 'label': 'Densitat Mitjana Població Flotant'}
        )
        
        # Afegim el fons de mapa de Seül gràcies a Contextily
        try:
            cx.add_basemap(ax, crs=gdf_wm.crs.to_string(), source=cx.providers.CartoDB.Positron)
        except Exception as basemap_e:
            print(f" [Avís] No s'ha pogut afegir el fons del mapa: {basemap_e}")
            
        plt.title('Mapa de Calor Continu: Concentració de Població Comercial a Seül', fontsize=16)
        plt.xlabel('Longitud (Web Mercator)')
        plt.ylabel('Latitud (Web Mercator)')
        
        out_png = os.path.join(EDA_OUTPUT_DIR, 'seoul_population_heatmap_static.png')
        plt.savefig(out_png, dpi=300, bbox_inches='tight')
        plt.close()
        print(f" -> Imatge (PNG) gràfica estàtica sobre mapa cartogràfic real generada a: {out_png}")
        
        # Validació i auditoria de dades
        print("\n--- Validació del Creuament Geogràfic ---")
        print(f" - Zones Comercials úniques carregades: {len(df_areas)}")
        print(f" - Zones creuades amb èxit amb les dades de població: {len(df_geo)}")
        if len(df_areas) == len(df_geo):
            print(" - [OK] Totes les coordenades s'han creuat perfectament (0% pèrdues de merge).")
        else:
            print(f" - [INFO] S'han perdut {len(df_areas) - len(df_geo)} zones per falta de dades de població.")
        
    except ImportError:
        print(" [Error] Les llibreries folium i pyproj són necessàries. Usa 'pip install folium pyproj'")
    except Exception as e:
        print(f" [Error] Fallida processant l'arxiu geogràfic: {e}")

# 8. Matriu de Correlació Multivariant (Correlation Heatmap)
print("\n--- Generació de la Matriu de Correlació (Correlation Heatmap) ---")
try:
    if 'Areas' in dataframes:
        merged_data = dataframes['Areas'][['zone_code']].copy()
        
        # Afegim Població (Mitjana)
        if 'Population' in dataframes:
            pop_avg = dataframes['Population'].groupby('zone_code')['total_floating_pop'].mean().reset_index()
            merged_data = pd.merge(merged_data, pop_avg, on='zone_code', how='left')
            
        # Afegim Vendes (Mitjana mensual)
        if 'Sales' in dataframes:
            sales_avg = dataframes['Sales'].groupby('zone_code')['monthly_sales_amount'].mean().reset_index()
            merged_data = pd.merge(merged_data, sales_avg, on='zone_code', how='left')
            
        # Afegim Botigues (Mitjana total_stores i franchise_stores)
        if 'Stores' in dataframes:
            stores_avg = dataframes['Stores'].groupby('zone_code')[['total_stores', 'franchise_stores']].mean().reset_index()
            merged_data = pd.merge(merged_data, stores_avg, on='zone_code', how='left')
            
        # Afegim Indicadors de Canvi (Temps de vida i clausura)
        if 'Change Indicators' in dataframes:
            change_avg = dataframes['Change Indicators'].groupby('zone_code')[['operating_months_avg', 'closed_months_avg']].mean().reset_index()
            merged_data = pd.merge(merged_data, change_avg, on='zone_code', how='left')
            
        # Eliminem Nuls que hagin pogut quedar i zone_code per la matriu
        corr_df = merged_data.drop(columns=['zone_code']).dropna()
        
        # Generem la matriu de correlació de Pearson
        corr_matrix = corr_df.corr(method='pearson')
        
        # Modifiquem noms columnes gràfic
        corr_matrix.columns = ['Pobl. Flotant', 'Vendes Mensuals', 'Botigues Totals', 'Franquícies', 'Mesos Operatius', 'Mesos Clausura']
        corr_matrix.index = corr_matrix.columns
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, square=True, linewidths=.5, cbar_kws={"shrink": .8})
        plt.title('Matriu de Correlació: Demografia vs Mortalitat Comercial', fontsize=14, pad=20)
        
        out_corr = os.path.join(EDA_OUTPUT_DIR, 'correlation_matrix.png')
        plt.savefig(out_corr, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f" -> Matriu de correlació multivariant generada amb èxit i desada a: {out_corr}")

except Exception as e:
    print(f" [Error] Fallida processant la matriu de correlació: {e}")

print("\n--- EDA Completat amb Èxit ! ---")
