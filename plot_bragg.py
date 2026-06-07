import numpy as np
import matplotlib.pyplot as plt

DEPTH = 30.0  # cm
FILENAME = "carbon12_QGSP_BIC_EMZ.csv"

data = np.genfromtxt(FILENAME, comments="#", delimiter=",")

edep = data[:, 3]       # MeV, totale su tutti gli eventi
n_bins = len(edep)
dx = DEPTH / n_bins

depth = (np.arange(n_bins) + 0.5) * dx

plt.plot(depth, edep / edep.max())
plt.xlabel("Depth in water (cm)")
plt.ylabel("Edep normalized")
plt.title("Bragg peak: 12C, 120 MeV/u, QGSP_BIC_EMZ")
plt.grid(True, alpha=0.3)
plt.savefig("carbon12_QGSP_BIC_EMZ.png", dpi=150)
plt.show()

imax = np.argmax(edep)
print(f"Peak depth = {depth[imax]:.2f} cm")
print(f"Peak bin = {imax}")
print(f"Max edep = {edep[imax]:.3e} MeV")