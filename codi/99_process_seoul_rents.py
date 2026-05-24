import pandas as pd
import matplotlib.pyplot as plt
import os

def create_chart_from_fred(filename):
    # Llegir el CSV. Aquest arxiu "QKRR628BIS.csv" conté un índex de preus de lloguer a Corea del Sud
    # Columna 1: observation_date
    # Columna 2: QKRR628BIS (L'índex)
    df = pd.read_csv(filename)
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    
    # Filtrar dades més recents, com ara de l'any 2000 fins a l'actualitat, per veure bé la corba
    df_recent = df[df['observation_date'] >= '2000-01-01']
    
    # Configurar l'estil de la gràfica
    plt.figure(figsize=(10, 6))
    
    # Dibuixar la línia
    plt.plot(df_recent['observation_date'], df_recent['QKRR628BIS'], 
             color='#1f77b4', linewidth=2.5, marker='', label='Índex Preus de l\'Habitatge (Corea del Sud)')
    
    # Afegeix el títol i les etiquetes per eixos
    plt.title("Evolució de l'índex de preu real de l'habitatge a Corea del Sud", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Any", fontsize=12)
    plt.ylabel("Índex de preu real ajustat a la inflació (Base 2010=100)", fontsize=12)
    
    # Configurar el grid i la font
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left', fontsize=11)
    
    # Millorar l'aparença dels marges
    plt.tight_layout()
    
    # Desar la figura generada al directori de treball com a imatge (PNG) o PDF
    output_filename = 'grafic_lloguer_corea.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    print(f"Gràfic creat i guardat com '{output_filename}' a la carpeta actual.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(BASE_DIR, "corea_rent_index_bis.csv")
    create_chart_from_fred(csv_file)
