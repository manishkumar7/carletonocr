from Tkinter import *
from notebook import notebook
import tkFileDialog
import cv

def tkImageFromCv(image):
    path = "/tmp/image.gif"
    cv.SaveImage(path, image)
    return PhotoImage(file=path)

class OCRWindow:
    def addTab(self, imageName, optionFunc):
        tab = Frame(self.tabs())
        imageFrame = Frame(tab)
        imageLabel = Label(imageFrame, text="No image loaded")
        imageLabel.pack(fill=X)
        setattr(self, imageName, imageLabel)
        imageFrame.pack(side=LEFT, fill=X)
        Frame(tab, width=2, background="#000000").pack(side=LEFT, fill=BOTH)
        optionsFrame = Frame(tab)
        optionFunc(optionsFrame)
        optionsFrame.pack(side=LEFT, fill=X)
        return tab
    
    def fileOptions(self, frame):
        fileChooser = Button(frame, text="Choose file", command=self.chooseFile)
        fileChooser.pack(side=TOP)
        self.fileLabel = Label(frame)
        self.fileLabel.pack(side=TOP)
    
    def dropdown(self, frame, name, attr, options):
    	innerFrame = Frame(frame)
    	Label(innerFrame, text=name+": ").pack(side=LEFT)
    	var = StringVar()
    	var.set(options[0])
    	var.trace('w', self.somethingChanged)
    	OptionMenu(innerFrame, var, *options).pack(side=LEFT)
    	setattr(self, attr, var)
    	innerFrame.pack(side=TOP)
    
    def entry(self, frame, name, attr, default):
        innerFrame = Frame(frame)
    	Label(innerFrame, text=name+": ").pack(side=LEFT)
    	var = StringVar()
    	var.set(default)
    	var.trace('w', self.somethingChanged)
    	Entry(innerFrame, textvariable=var).pack(side=LEFT)
    	setattr(self, attr, var)
    	innerFrame.pack(side=TOP)
    
    def binarizerOptions(self, frame):
        self.dropdown(frame, 'Binarizer', 'binarizer', ['global binarizer', 'adaptive binarizer'])
    
    def segmenterOptions(self, frame):
        self.dropdown(frame, 'Segmenter', 'segmenter', ['connected components', 'bounding box'])
    	
    def typesetterOptions(self, frame):
        self.dropdown(frame, 'Typesetter', 'typesetter', ["linear typesetter", "no typesetter"])
        self.entry(frame, 'Width of space', 'spaceWidth', '.25')

    def featureExtractorOptions(self, frame):
        self.dropdown(frame, 'Feature extractor', 'featureExtractor', [ "template", "old template", "histogram", "vertical histogram", "horizontal histogram"])

    def matcherOptions(self, frame):
        self.entry(frame, 'k nearest neighbors', 'k', '1')

    def linguistOptions(self, frame):
        self.dropdown(frame, 'Linguist', 'linguist', ["n-gram", "no linguist"])

    def __init__(self):
        self.application = Tk()
        #self.application.geometry("600x400+0+0")
        self.tabs = notebook(self.application, TOP)
        
        tabParameters = [
            ('image', self.fileOptions, "Original"),
            ('binarized', self.binarizerOptions, "Binary"),
            ('segmented', self.segmenterOptions, "Segmented"),
            ('typesetter', self.typesetterOptions, "Typeset"),
            ('features', self.featureExtractorOptions, "Features"),
            ('matched', self.matcherOptions, "Matched"),
            ('output', self.linguistOptions, "Final output")
        ]
        
        tabs = [(self.addTab(attr, options), name) for attr, options, name in tabParameters]
        for tab, name in tabs:
        	self.tabs.add_screen(tab, name)
        
        self.filename = None
        self.update()
        
    def run(self):
        self.application.mainloop()
        
    def chooseFile(self):
        self.filename = tkFileDialog.askopenfilename()
        self.update()
    
    def somethingChanged(self, *args): #What are the args?
        self.update()
    
    def update(self):
        self.fileLabel.config(text=self.filename if self.filename is not None else "No file selected")
        if self.filename:
            photo = tkImageFromCv(cv.LoadImage(self.filename))
            self.image.config(image=photo, text=None)
            self.image.photo = photo
        
if __name__ == "__main__":
    gui = OCRWindow()
    gui.run()
