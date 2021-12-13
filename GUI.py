import tkinter as tk

root = tk.Tk()
root.title("Distortion Detector")

Plate1Frame =tk.Frame(root, borderwidth = l1)
Plate2Frame =tk.Frame(root)
Plate3Frame =tk.Frame(root)
Plate4Frame =tk.Frame(root)
Plate5Frame =tk.Frame(root)
SliceDistanceFrame =tk.Frame(root)

PlateFrames = [Plate1Frame,Plate2Frame,Plate3Frame,Plate4Frame,Plate5Frame]

count = 1
for frame in PlateFrames:
    label= tk.Label(frame,text="Plate " + str(count),justify=tk.CENTER)
    label.grid(row = 0, column = 1, sticky = tk.N)
    B1 = tk.Button(frame, text ="<-")
    B2 = tk.Button(frame, text ="->")
    B1.grid(row = 2, column = 0, sticky = tk.S)
    B2.grid(row = 2, column = 2, sticky = tk.S)
    count+=1


Plate1Frame.grid(row = 0, column = 0, sticky = "nsew")
Plate2Frame.grid(row = 0, column = 1, sticky = "nsew")
Plate3Frame.grid(row = 0, column = 2, sticky = "nsew")
Plate4Frame.grid(row = 1, column = 0, sticky = "nsew")
Plate5Frame.grid(row = 1, column = 1, sticky = "nsew")


SliceDistanceFrame.grid(row = 1, column = 2, sticky = tk.N)
label= tk.Label(SliceDistanceFrame,text="Slice Distance",justify=tk.CENTER)
label.grid(row = 0, column = 0, sticky = "nsew")


root.mainloop()