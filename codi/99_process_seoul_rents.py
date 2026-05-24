import pandas as pd
import matplotlib.pyplot as plt
import os

def create_chart_from_fred(filename):
    df = pd.read_csv(filename)
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    
    df_recent = df[df['observation_date'] >= '2000-01-01']
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(
        df_recent['observation_date'],
        df_recent['QKRR628BIS'],
        color='#1f77b4',
        linewidth=2.5,
        marker='',
        label="Índex de preus de l'habitatge (Corea del Sud)"
    )
    
    plt.title(
        "Evolució de l'índex de preu real de l'habitatge a Corea del Sud",
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    plt.xlabel("Any", fontsize=12)
    plt.ylabel("Índex de preu real ajustat a la inflació (Base 2010=100)", fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left', fontsize=11)
    plt.tight_layout()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data", "eda_outputs")
    os.makedirs(output_dir, exist_ok=True)

    output_filename = os.path.join(output_dir, "grafic_lloguer_corea.png")
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    print(f"Gràfic creat i guardat a: {output_filename}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(BASE_DIR, "data", "raw", "corea_rent_index_bis.csv")
    create_chart_from_fred(csv_file)
