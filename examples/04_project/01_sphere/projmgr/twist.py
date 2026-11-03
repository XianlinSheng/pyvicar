import numpy as np
import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl


pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())

x = np.linspace(0, 1, 100)
T1 = x
T2 = 4 * x**3 - 3 * x
T3 = 16 * x**5 - 20 * x**3 + 5 * x
D1 = 5.2788
D2 = -4.1069
D3 = -1.8684

y = D1 * T1 + D2 * T2 + D3 * T3

fig = plt.figure()
yopt = 0.5 * np.degrees(np.atan(np.pi * 0.2 * x))
yopt2 = 0.5 * np.degrees(np.atan(np.pi * 0.12 * x))
plt.plot(x, y, "r-", label="Seagull")
plt.plot(x, yopt, "b-", label="Optimal Amp St=0.2")
plt.plot(x, yopt2, "g-", label="Optimal Amp St=0.12")
plt.legend()
plt.grid(True)


plt.show()
