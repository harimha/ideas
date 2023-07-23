import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta
import numpy as np

t = np.arange(0.0, 5.0, 0.01)
s = np.cos(2 * np.pi * t)

fig, (ax1, ax3) = plt.subplots(1,2, figsize=(10,5))
l1, = ax1.plot(t,s)
ax2 = ax1.twinx()
l2, = ax2.plot(t, range(len(t)))
ax2.set_yticks(range(0,500,200))
dir(ax2)