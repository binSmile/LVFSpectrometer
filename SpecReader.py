import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

bdir = 'C:\\...\\STM-Electroluminescence\\ExpData\\Omicron results\\Specs\\'
name = '2022-05-06_14-48-28_Si-Ag-Mica_4.0V'
spec = name +'.xlsx'

spec = pd.read_excel(bdir+spec)

# - ~818 = 3280 = start windows at 733+12.1 nm
# - ~1840 = 7360 = end window at 468+12.1 nm (start 2nd order )

# ax + b = w
# x = [3280, 7360]
# y = [733+12.1, 468+12.1]
# a, b = np.polyfit(x,y,1)
# spec['W'] = spec['Pos']*a+b
spec = spec.set_index('W')


plt.errorbar(spec.index, 'Int', yerr='Std', data=spec)
plt.xlabel('Wavelength, nm')
plt.ylabel('Counts')