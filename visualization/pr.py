import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


x = np.linspace(-10, 10, 200)  # Sample data.
plt.show()
# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
ax.plot(x, x, label='linear')  # Plot some data on the axes.
ax.plot(x, x**2+x+1, label='quadratic')  # Plot more data on the axes...
ax.plot(x, 23*x**3-50*x**2+32*x+1, label='cubic')  # ... and some more.
ax.set_xlabel('x label')  # Add an x-label to the axes.
ax.set_ylabel('y label')  # Add a y-label to the axes.
ax.set_title("Simple Plot")  # Add a title to the axes.
ax.legend()  # Add a legend.