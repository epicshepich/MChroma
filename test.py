"""import tkinter as tk
import tkinter.filedialog


windows = {"main":tk.Tk()}

data = []
with open(tk.filedialog.askopenfilename()) as reader:
    line = reader.readline()
    while line != '':  # The EOF char is an empty string
        print(line, end='')
        try:
            data.append(int(line))
        except ValueError:
            pass
        line = reader.readline()

print(data)


windows["main"].mainloop()
"""
"""a=[1,2,2,345,6,1000,1000]

a_maxima = [index for index in range(len(a)) if a[index]==max(a)]
print(a_maxima)
#i_maxima = [index for index in range(len(self.time_series)) if self.signal_series[index] == self.height]
i_max=int(np.floor((len(i_maxima)-1)/2)"""
from modules import install
install("icecream")
