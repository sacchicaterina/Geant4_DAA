import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. Configurazione dei file esportati da Geant4 (10.000 eventi ciascuno)
files_config = {
    "carbon_QGSP_BIC_EMZ_3000.csv": {"label": "QGSP_BIC_EMZ (Riferimento)", "color": "#1f77b4", "ls": "-"},
    "carbon_QGSP_BIC_3000.csv": {"label": "QGSP_BIC (EM Standard)", "color": "#ff7f0e", "ls": "--"},
    "carbon_FTFP_BERT_EMZ_3000.csv": {"label": "FTFP_BERT_EMZ (Bertini)", "color": "#2ca02c", "ls": "-."},
    "carbon_FTFP_BERT_EMZ_noInelastic_3000.csv": {"label": "FTFP_BERT_EMZ (Senza Inelastiche)", "color": "#d62728", "ls": ":"}
}

# Parametri della simulazione attuale
n_primaries = 10**6  # Numero di ioni di Carbonio lanciati
mesh_length_cm = 20.0  # Lunghezza totale della mesh (20 cm)

plt.figure(figsize=(10, 6), dpi=150)

# Variabili di supporto per l'annotazione del picco di riferimento
ref_peak_depth = 0
ref_peak_val = 0

# 2. Loop di lettura, elaborazione e plotting
for file_name, config in files_config.items():
    if not os.path.exists(file_name):
        print(f"Attenzione: file '{file_name}' non trovato nella cartella corrente. Salto.")
        continue
        
    # Carica il file saltando i commenti iniziali (#)
    # Geant4 esporta: iX, iY, iZ, total_val, total_val^2, entries
    df = pd.read_csv(
        file_name, 
        comment="#", 
        names=["iX", "iY", "iZ", "edep_total", "edep_sq", "entries"]
    )
    
    # Calcoliamo il numero di bin (es. 200 o 400) per gestire la conversione in cm
    num_bins = len(df)
    bin_width_cm = mesh_length_cm / num_bins
    
    # Trasformiamo l'indice del bin (iX) in profondità reale (cm) al centro del bin
    df["depth_cm"] = df["iX"] * bin_width_cm + (bin_width_cm / 2.0)
    
    # Normalizziamo l'energia depositata per singolo ione incidente (MeV / ione)
    df["edep_per_ion"] = df["edep_total"] / n_primaries
    
    # Disegnamo la curva
    plt.plot(
        df["depth_cm"], 
        df["edep_per_ion"], 
        color=config["color"], 
        linestyle=config["ls"], 
        lw=2.5, 
        label=config["label"]
    )
    
    # Se è la curva di riferimento, salviamo le coordinate del picco per l'annotazione
    if "QGSP_BIC_EMZ" in config["label"]:
        idx_max = df["edep_per_ion"].idxmax()
        ref_peak_depth = df["depth_cm"].iloc[idx_max]
        ref_peak_val = df["edep_per_ion"].iloc[idx_max]

# 3. Personalizzazione estetica e annotazione del picco
plt.title("Profilo di Profondità-Dose per Fascio di Ioni $^{12}$C (1440 MeV) in Acqua", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Profondità nel fantoccio d'acqua (cm)", fontsize=11)
plt.ylabel("Energia depositata per ione incidente (MeV / ione)", fontsize=11)

# Aggiunge la freccia sul picco di Bragg se la curva di riferimento è stata caricata
if ref_peak_val > 0:
    plt.annotate(
        f"Picco di Bragg (~{ref_peak_depth:.2f} cm)",
        xy=(ref_peak_depth, ref_peak_val),
        xytext=(ref_peak_depth + 0.8, ref_peak_val * 0.75),
        arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
        fontsize=10,
        fontweight='bold'
    )

plt.grid(True, linestyle="--", alpha=0.5)
plt.xlim(0, 18)  # Il picco fisicamente è attorno ai 3.3 cm (in acqua pura) o 12.8 cm (nel vecchio sandwich)
plt.ylim(0, max(ref_peak_val * 1.15, 10)) # Gestisce dinamicamente l'altezza dell'asse Y
plt.legend(loc="upper left", frameon=True, shadow=True, fontsize=10)

# 4. Salvataggio del grafico definitivo
output_plot_name = "confronto_bragg_carbonio_3000MeV.png"
plt.savefig(output_plot_name, bbox_inches='tight')
print(f"\nGrafico salvato con successo come '{output_plot_name}'!")

plt.show()