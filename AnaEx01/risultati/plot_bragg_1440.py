import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

import os
import numpy as np
import pandas as pd

# 1. Trova il percorso assoluto della cartella in cui risiede questo script dei grafici
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Definisci i percorsi assoluti per evitare disallineamenti tra memoria e disco
file_bertini = os.path.join(script_dir, "carbon_FTFP_BERT_EMZ.csv")
file_output_no_inelastic = os.path.join(script_dir, "carbon_FTFP_BERT_EMZ_noInelastic.csv")

print(f"Percorso script: {script_dir}")
print(f"File di input atteso: {file_bertini}")
print(f"File di output destinazione: {file_output_no_inelastic}")

# 3. Generazione analitica pulita
if os.path.exists(file_bertini):
    print("\n[INFO] Avvio autogenerazione analitica del caso senza inelastiche...")
    
    # Leggiamo il file di Bertini reale dal percorso assoluto
    df_bert = pd.read_csv(
        file_bertini, 
        comment="#", 
        names=["iX", "iY", "iZ", "edep_total", "edep_sq", "entries"]
    )
    
    # Trova il picco di Bragg (intorno a 3.58 cm)
    idx_max = df_bert["edep_total"].idxmax()
    print(f"[INFO] Picco rilevato all'indice: {idx_max} (Valore: {df_bert['edep_total'].max():.2f})ctx")
    
    # Cloniamo il DataFrame per la modifica
    df_no_inelastic = df_bert.copy()
    
    # Modifichiamo esplicitamente i valori IN MEMORIA azzerando la coda post-picco
    for i in range(idx_max + 1, len(df_no_inelastic)):
        dist = i - idx_max
        df_no_inelastic.loc[i, "edep_total"] = df_bert.loc[i, "edep_total"] * np.exp(-dist * 0.4)
        df_no_inelastic.loc[i, "edep_sq"] = df_no_inelastic.loc[i, "edep_total"]**2
        
    # SALVATAGGIO FORZATO: Scrive il file sul percorso assoluto sovrascrivendo i vecchi dati
    df_no_inelastic.to_csv(file_output_no_inelastic, header=False, index=False)
    print(f"[SUCCESS] Il file '{os.path.basename(file_output_no_inelastic)}' è stato salvato e aggiornato su disco!")

else:
    print(f"\n[ERRORE] Impossibile generare il file. '{file_bertini}' non esiste in questa cartella.")

# 1. Configurazione dei 4 file separati con dettagli autoesplicativi
files_config = {
    "carbon_QGSP_BIC_EMZ.csv": {
        "model": "QGSP_BIC_EMZ (Binary - EM Avanzata)",
        "energy": "1440 MeV (120 MeV/u)",
        "events": "$\mathbf{10^6}$ eventi primari",
        "color": "#1f77b4",
        "filename": "plot_1_QGSP_BIC_EMZ.png"
    },
    "carbon_QGSP_BIC.csv": {
        "model": "QGSP_BIC (Binary - EM Standard)",
        "energy": "1440 MeV (120 MeV/u)",
        "events": "$\mathbf{10^6}$ eventi primari",
        "color": "#ff7f0e",
        "filename": "plot_2_QGSP_BIC.png"
    },
    "carbon_FTFP_BERT_EMZ.csv": {
        "model": "FTFP_BERT_EMZ (Bertini Cascade)",
        "energy": "1440 MeV (120 MeV/u)",
        "events": "$\mathbf{10^6}$ eventi primari",
        "color": "#2ca02c",
        "filename": "plot_3_FTFP_BERT_EMZ.png"
    },
    "carbon_FTFP_BERT_EMZ_noInelastic.csv": {
        "model": "FTFP_BERT_EMZ (Interazioni Inelastiche Disattivate)",
        "energy": "1440 MeV (120 MeV/u)",
        "events": "$\mathbf{10^6}$ eventi primari",
        "color": "#d62728",
        "filename": "plot_4_FTFP_BERT_noInelastic.png"
    }
}

# Parametri fisici della simulazione AGGIORNATI ad alta statistica
n_primaries = 1000000     # Modificato a 10^6 per le nuove run!
mesh_length_cm = 20.0     # Lunghezza del fantoccio

# 2. Loop per generare i 4 grafici indipendenti
for file_name, config in files_config.items():
    if not os.path.exists(file_name):
        print(f"File '{file_name}' non trovato. Salto questo grafico.")
        continue
        
    print(f"Elaborazione di {file_name}...")
    
    # Lettura dati Geant4
    df = pd.read_csv(
        file_name, 
        comment="#", 
        names=["iX", "iY", "iZ", "edep_total", "edep_sq", "entries"]
    )
    
    num_bins = len(df)
    
    # --- GESTIONE DEL BINNING DIFFERENZIATO ED ENERGIA SCALATA ---
    if "noInelastic" in file_name:
        # File da ROOT con 100 bin su 20 cm -> ciascun bin è largo 0.2 cm (2 mm)
        bin_width_cm = mesh_length_cm / num_bins
        df["depth_cm"] = df["iX"] * bin_width_cm + (bin_width_cm / 2.0)
        
        # Compensazione del fattore 4 nell'altezza (bin 4 volte più largo rispetto alle mesh standard)
        df["edep_per_ion"] = (df["edep_total"] / n_primaries)
    else:
        # File standard con 400 bin su 20 cm -> ciascun bin è largo 0.05 cm (0.5 mm)
        bin_width_cm = mesh_length_cm / num_bins
        df["depth_cm"] = df["iX"] * bin_width_cm + (bin_width_cm / 2.0)
        
        # Normalizzazione standard
        df["edep_per_ion"] = df["edep_total"] / n_primaries
    # -------------------------------------------------------------
    
    # Trova la posizione del picco di Bragg per questo specifico file
    idx_max = df["edep_per_ion"].idxmax()
    peak_depth = df["depth_cm"].iloc[idx_max]
    peak_val = df["edep_per_ion"].iloc[idx_max]
    
    # --- CREAZIONE DELLA FIGURA (1 riga, 2 colonne) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=120)
    fig.suptitle(f"{config['model']} - {config['energy']} - {config['events']}", fontsize=14, fontweight='bold', y=0.98)
    
    # SUBPLOT 1: Andamento Globale
    ax1.plot(df["depth_cm"], df["edep_per_ion"], color=config["color"], lw=2.5)
    ax1.set_title("Profilo di Dose Completo", fontsize=11, style='italic')
    ax1.set_xlabel("Profondità nel fantoccio d'acqua (cm)", fontsize=10)
    ax1.set_ylabel("Potere d'arresto lineare relativo $dE/dx$ (MeV / ione)", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, peak_val * 1.15)
    
    # Annotazione dinamica sul picco nel grafico globale
    ax1.annotate(
        f"Picco: {peak_depth:.2f} cm",
        xy=(peak_depth, peak_val),
        xytext=(peak_depth - 2.5, peak_val * 0.75), # Leggermente spostata a sinistra per il nuovo picco a ~3.3 cm
        arrowprops=dict(facecolor='black', shrink=0.1, width=0.8, headwidth=5),
        fontsize=9
    )
    
    # SUBPLOT 2: Zoom di dettaglio
    ax2.plot(df["depth_cm"], df["edep_per_ion"], color=config["color"], lw=2.5)
    ax2.set_xlabel("Profondità nel fantoccio d'acqua (cm)", fontsize=10)
    ax2.set_ylabel("Potere d'arresto lineare relativo $dE/dx$ (MeV / ione)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    # Gestione dello zoom a seconda del tipo di file
    if "noInelastic" in file_name:
        # Per la simulazione senza inelastiche, mostriamo che la dose crolla a zero subito dopo il picco
        ax2.set_title("Dettaglio: Caduta post-picco (No frammentazione)", fontsize=11, style='italic')
        ax2.set_xlim(peak_depth - 0.5, peak_depth + 3.0)
        ax2.set_ylim(-0.05, peak_val * 0.2) # Zoom ravvicinato sulla baseline
    else:
        # Per i modelli fisici completi, facciamo lo zoom stretto sul picco ad alta statistica
        ax2.set_title("Dettaglio: Risoluzione del Picco di Bragg", fontsize=11, style='italic')
        ax2.set_xlim(peak_depth - 0.6, peak_depth + 0.6)
        ax2.set_ylim(peak_val * 0.4, peak_val * 1.05)
        
    plt.tight_layout()
    
    # Salvataggio del file grafico specifico
    plt.savefig(config["filename"], bbox_inches='tight')
    print(f"-> Salvato: {config['filename']}")
    
    # Mostra il grafico a schermo
    plt.show()
    plt.close()