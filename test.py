import tkinter as tk
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
