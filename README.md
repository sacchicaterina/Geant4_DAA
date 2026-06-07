# Geant4_DAA
L'esercizio è stato  svolto tramite la costruzione di una Macro con tutte le specifiche richieste senza però dover toccare detectorconstruction.cc 

Ho  creato la macro chiamata carbon12.ma. Questa macro è la principale da usare in modalità batch.Qua ho definito la geometria nuova e la particella. Si parte dalla geometria del calorimetro di AnaEx01 si annulla il gap e si crea un fantoccio d'acqua di 300 mm lungo la direzione del fascio.  Abbiamo 300 layer da 1 mm ciscuno, questo permette di campionare il deposito energetico con risoluzione 1mm.

Si lancia da dentro build con ./AnaEx01 ../carbon12.mac

Questa macro inizializza la geometria, imposta il fascio di carbonio, crea uno scoring mesh lungo x, esegue 1000 eventi ( che poi diventeranno 10^6 per aavere significato statistico) e salva il deposito energetico nel file:

carbon12_QGSP_BIC_EMZ.csv
questa macro va aggiornata ogni volta con la PhysicsList richiesta. 


Per la visualizzazione grafica non si usa carbon12.mac, perché contiene anche /run/beamOn 1000 e lo scoring. Per la GUI abbiamo usato due macro separate.

La prima è init_vis.mac, dentro build, modificata per inizializzare direttamente la geometria d’acqua prima di aprire la visualizzazione:

/control/verbose 2
/control/saveHistory
/run/verbose 2
/run/numberOfThreads 1

/N03/det/setAbsMat G4_WATER
/N03/det/setGapMat G4_WATER
/N03/det/setAbsThick 1 mm
/N03/det/setGapThick 0 mm
/N03/det/setNbOfLayers 300

/run/initialize

/control/execute vis.mac

Si lancia  con: cd ~/Desktop/AnaEx01/build
./AnaEx01


La seconda macro è beam_carbon12.mac, usata solo in modalità interattiva per caricare il fascio senza reinizializzare la geometria:

/gps/particle ion
/gps/ion 6 12 0
/gps/ene/type Mono
/gps/ene/mono 1440 MeV
/gps/pos/type Point
/gps/pos/centre -16 0 0 cm
/gps/direction 1 0 0

Dentro la GUI si esegue:

/control/execute beam_carbon12.mac
/run/beamOn 1

oppure, per vedere più tracce accumulate:

/run/beamOn 20

La visualizzazione serve solo come controllo qualitativo: si verifica che il fascio entri lungo +x, si arresti intorno a 3.5–3.6 cm e produca secondari vicino alla regione del picco. 

