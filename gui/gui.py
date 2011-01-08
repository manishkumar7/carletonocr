from Tkinter import *
from notebook import notebook
import tkFileDialog

class OCRWindow:
    def __init__(self):
		self.application = Tk()
		self.application.geometry("600x400+0+0")
		self.tabs = notebook(self.application, TOP)
		
		# uses the notebook's frame
		self.original = Frame(self.tabs())
		imageFrame = Frame(self.original, borderwidth=1, relief=RIDGE)
		self.image = Label(imageFrame, text="No image loaded")
		self.image.pack(fill=X)
		imageFrame.pack(side=LEFT, fill=X)
		Frame(self.original, width=2, background="#000000").pack(side=LEFT, fill=BOTH)
		originalOptionsFrame = Frame(self.original)
		fileChooser = Button(originalOptionsFrame, text="Choose file", command=self.chooseFile)
		fileChooser.pack(side=TOP)
		self.fileLabel = Label(originalOptionsFrame)
		self.fileLabel.pack(side=TOP)
		originalOptionsFrame.pack(side=LEFT, fill=X)
		
		self.binary = Frame(self.tabs())
		self.segmented = Frame(self.tabs())
		self.features = Frame(self.tabs())
		self.matched = Frame(self.tabs())
		self.output = Frame(self.tabs())
		
		# keeps the reference to the radiobutton (optional)
		self.tabs.add_screen(self.original, "Original")
		self.tabs.add_screen(self.binary, "Binary")
		self.tabs.add_screen(self.segmented, "Segmented")
		self.tabs.add_screen(self.features, "Features")
		self.tabs.add_screen(self.matched, "Matched")
		self.tabs.add_screen(self.output, "Final output")
		
		self.filename = None
		self.update()
		
    def run(self):
    	self.application.mainloop()
    	
    def chooseFile(self):
    	self.filename = tkFileDialog.askopenfilename()
    	self.update()
    
    def update(self):
    	self.fileLabel.config(text=self.filename if self.filename is not None else "No file selected")
    	if self.filename:
    		photo = PhotoImage(file=self.filename)
    		self.image.config(image=photo, text=None)
    		self.image.photo = photo
    	
if __name__ == "__main__":
	gui = OCRWindow()
	gui.run()
