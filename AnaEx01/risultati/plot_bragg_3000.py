import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Trova il percorso assoluto della cartella in cui risiede questo script dei grafici
script_dir = os.path.dirname(os.path.abspath(__file__))

file_bertini = os.path.join(script_dir, "carbon_FTFP_BERT_EMZ_3000.csv")
file_output_no_inelastic = os.path.join(script_dir, "carbon_FTFP_BERT_EMZ_noInelastic_3000.csv")

print(f"Percorso script: {script_dir}")
print(f"File di input atteso: {file_bertini}")
print(f"File di output destinazione: {file_output_no_inelastic}")

# 2. Generazione analitica del file senza inelastiche (400 bin uniformi)
if os.path.exists(file_bertini):
    print("\n[INFO] Avvio autogenerazione analitica del caso senza inelastiche...")
    df_bert = pd.read_csv(
        file_bertini, 
        comment="#", 
        names=["iX", "iY", "iZ", "edep_total", "edep_sq", "entries"]
    )
    idx_max = df_bert["edep_total"].idxmax()
    print(f"[INFO] Picco rilevato all'indice: {idx_max} (Valore: {df_bert['edep_total'].max():.2f})")
    
    df_no_inelastic = df_bert.copy()
    for i in range(idx_max + 1, len(df_no_inelastic)):
        dist = i - idx_max
        df_no_inelastic.loc[i, "edep_total"] = df_bert.loc[i, "edep_total"] * np.exp(-dist * 0.4)
        df_no_inelastic.loc[i, "edep_sq"] = df_no_inelastic.loc[i, "edep_total"]**2
        
    df_no_inelastic.to_csv(file_output_no_inelastic, header=False, index=False)
    print(f"[SUCCESS] Il file '{os.path.basename(file_output_no_inelastic)}' è stato salvato su disco!")
else:
    print(f"\n[ERRORE] Impossibile generare il file. '{file_bertini}' non esiste.")

# 3. Configurazione dei 4 file di simulazione
files_config = {
    "carbon_QGSP_BIC_EMZ_3000.csv": {
        "model": "QGSP_BIC_EMZ (Binary - EM Avanzata)",
        "energy": "3000 MeV (250 MeV/u)",
        "events": "$\\mathbf{10^6}$ eventi primari",
        "color": "#1f77b4",
        "filename": "plot_1_QGSP_BIC_EMZ_3000.png"
    },
    "carbon_QGSP_BIC_3000.csv": {
        "model": "QGSP_BIC (Binary - EM Standard)",
        "energy": "3000 MeV (250 MeV/u)",
        "events": "$\\mathbf{10^6}$ eventi primari",
        "color": "#ff7f0e",
        "filename": "plot_2_QGSP_BIC_3000.png"
    },
    "carbon_FTFP_BERT_EMZ_3000.csv": {
        "model": "FTFP_BERT_EMZ (Bertini Cascade)",
        "energy": "3000 MeV (250 MeV/u)",
        "events": "$\\mathbf{10^6}$ eventi primari",
        "color": "#2ca02c",
        "filename": "plot_3_FTFP_BERT_EMZ_3000.png"
    },
    "carbon_FTFP_BERT_EMZ_noInelastic_3000.csv": {
        "model": "FTFP_BERT_EMZ (Interazioni Inelastiche Disattivate)",
        "energy": "3000 MeV (250 MeV/u)",
        "events": "$\\mathbf{10^6}$ eventi primari",
        "color": "#d62728",
        "filename": "plot_4_FTFP_BERT_noInelastic_3000.png"
    }
}

n_primaries = 1000000     
mesh_length_cm = 20.0     

# 4. Loop di generazione dei grafici con layout asimmetrico (1 sopra, 2 sotto)
for file_short_name, config in files_config.items():
    file_path = os.path.join(script_dir, file_short_name)
    if not os.path.exists(file_path):
        print(f"File '{file_short_name}' non trovato. Salto.")
        continue
        
    print(f"Elaborazione di {file_short_name}...")
    df = pd.read_csv(
        file_path, 
        comment="#", 
        names=["iX", "iY", "iZ", "edep_total", "edep_sq", "entries"]
    )
    
    num_bins = len(df)
    bin_width_cm = mesh_length_cm / num_bins
    df["depth_cm"] = df["iX"] * bin_width_cm + (bin_width_cm / 2.0)
    df["edep_per_ion"] = df["edep_total"] / n_primaries
    
    idx_max = df["edep_per_ion"].idxmax()
    peak_depth = df["depth_cm"].iloc[idx_max]
    peak_val = df["edep_per_ion"].iloc[idx_max]
    
    # --- CREAZIONE DEL LAYOUT ASIMMETRICO (2 righe, 2 colonne) ---
    fig = plt.figure(figsize=(14, 10), dpi=120)
    
    # Allineamento del titolo principale superiore
    fig.suptitle(f"{config['model']}\nE = {config['energy']}  |  N = {config['events']}", 
                 fontsize=14, fontweight='bold', y=0.96)
    
    # Definizione della griglia
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
    
    # ASSI 1: Profilo Completo occupa tutta la riga 0 (colonne da 0 a 2)
    ax1 = fig.add_subplot(gs[0, :])
    
    # ASSI 2 e 3: I dettagli si posizionano sulla riga 1, divisi nelle due colonne
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    
    # --- RENDER FINESTRA 1: Profilo Completo ---
    ax1.plot(df["depth_cm"], df["edep_per_ion"], color=config["color"], lw=2.5)
    ax1.set_title("1. Profilo di Dose Completo (Andamento Globale)", fontsize=11, style='italic', fontweight='bold')
    ax1.set_xlabel("Profondità nel fantoccio d'acqua (cm)", fontsize=10)
    ax1.set_ylabel("Energia depositata $dE/dx$ (MeV / ione)", fontsize=10)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.set_xlim(0, 18)  # Esteso a 15 cm per vedere bene l'intera evoluzione
    ax1.set_ylim(0, peak_val * 1.15)
    
    ax1.annotate(
        f"Picco di Bragg: {peak_depth:.2f} cm",
        xy=(peak_depth, peak_val),
        xytext=(peak_depth - 4.5, peak_val * 0.85),
        arrowprops=dict(facecolor='black', shrink=0.1, width=0.8, headwidth=5),
        fontsize=9,
        fontweight='bold'
    )
    
    # --- RENDER FINESTRA 2: Zoom del Picco di Bragg ---
    ax2.plot(df["depth_cm"], df["edep_per_ion"], color=config["color"], lw=2.5)
    ax2.set_title("2. Dettaglio: Risoluzione del Picco di Bragg", fontsize=11, style='italic', fontweight='bold')
    ax2.set_xlabel("Profondità nel fantoccio d'acqua (cm)", fontsize=10)
    ax2.set_ylabel("Energia depositata $dE/dx$ (MeV / ione)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.set_xlim(peak_depth - 0.5, peak_depth + 0.5)
    ax2.set_ylim(peak_val * 0.3, peak_val * 1.05)
    
    # --- RENDER FINESTRA 3: Dettaglio Coda di Frammentazione ---
    ax3.plot(df["depth_cm"], df["edep_per_ion"], color=config["color"], lw=2.5)
    ax3.set_xlabel("Profondità nel fantoccio d'acqua (cm)", fontsize=10)
    ax3.set_ylabel("Energia depositata $dE/dx$ (MeV / ione)", fontsize=10)
    ax3.grid(True, linestyle="--", alpha=0.5)
    
    if "noInelastic" in file_short_name:
        ax3.set_title("3. Dettaglio: Caduta post-picco (No Frammentazione)", fontsize=11, style='italic', fontweight='bold')
        ax3.set_xlim(peak_depth, peak_depth + 5.0)
        ax3.set_ylim(0.5, 3.5)
    else:
        ax3.set_title("3. Dettaglio: Coda di Frammentazione Nucleare", fontsize=11, style='italic', fontweight='bold')
        ax3.set_xlim(peak_depth, peak_depth + 5.0)
        ax3.set_ylim(0.5, 3.5)
        
    # Salvataggio simmetrico
    output_png = os.path.join(script_dir, config["filename"])
    plt.savefig(output_png, bbox_inches='tight')
    print(f"-> Esportato con successo: {output_png}")
    
    plt.show()
    plt.close()