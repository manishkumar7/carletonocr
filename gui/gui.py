import cv
import wx
import wx.aui
import os

def wxImageFromCv(image):
    path = "/tmp/image.gif"
    cv.SaveImage(path, image)
    return wx.Image(path)

class TabWindow():

    def beside(self, parent, sizer, contents):
        panel = wx.Panel(parent=parent)
        left, right = contents(panel)
        innerSizer = wx.BoxSizer(wx.HORIZONTAL)
        innerSizer.Add(left, 1, wx.EXPAND)
        innerSizer.Add(right, 1, wx.EXPAND)
        panel.SetSizer(innerSizer)
        if sizer is not None: sizer.Add(panel, 0, wx.EXPAND)
        return panel

    def tab(self, notebook, attr, optionsFunc):
        def contents(panel):
            textPanel = wx.Panel(parent=panel, style=wx.SUNKEN_BORDER)
            setattr(self, attr, textPanel)
            text = wx.StaticText(parent=textPanel, label="No image loaded")
            options = wx.Panel(parent=panel, style=wx.SUNKEN_BORDER)
            optionsSizer = wx.BoxSizer(wx.VERTICAL)
            optionsFunc(options, optionsSizer)
            options.SetSizer(optionsSizer)
            return textPanel, options
        return self.beside(notebook, None, contents)

    def fileOptions(self, parent, sizer):
        def contents(panel):
            button = wx.Button(panel, wx.ID_ANY, "Choose file")
            name = wx.StaticText(panel, label="No file loaded")
            def chooseFile(evt):
                dialog = wx.FileDialog(parent, message="Open an Image", defaultDir=os.getcwd(), style=wx.OPEN)
                if dialog.ShowModal() == wx.ID_OK:
                    self.filename = dialog.GetPath()
                    self.update()
                dialog.Destroy()
            self.app.Bind(wx.EVT_BUTTON, chooseFile, button)
            return button, name
        self.beside(parent, sizer, contents)

    def besideLabel(self, parent, sizer, name, right):
        def contents(panel):
            label = wx.StaticText(panel, label=name+": ")
            control = right(panel)
            return label, control
        self.beside(parent, sizer, contents)

    def dropdown(self, parent, sizer, name, attr, options):
        def contents(panel):
             control = wx.ComboBox(panel, value=options[0], choices=options, style=wx.CB_DROPDOWN)
             def changeOption(*args):
                 setattr(self, attr, control.GetValue())
                 self.update()
             self.app.Bind(wx.EVT_COMBOBOX, changeOption, control)
             return control
        self.besideLabel(parent, sizer, name, contents)

    def entry(self, parent, sizer, name, attr, default):
        def contents(panel):
            entry = wx.TextCtrl(panel)
            def changeText(*args):
                setattr(self, attr, entry.GetValue())
                self.update()
            self.app.Bind(wx.EVT_TEXT_ENTER, changeText, entry)
            return entry
        self.besideLabel(parent, sizer, name, contents)

    def binarizerOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Binarizer', 'binarizer', ['global binarizer', 'adaptive binarizer'])
    
    def segmenterOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Segmenter', 'segmenter', ['connected components', 'bounding box'])
    	
    def typesetterOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Typesetter', 'typesetter', ["linear typesetter", "no typesetter"])
        self.entry(frame, sizer, 'Width of space', 'spaceWidth', '.25')

    def featureExtractorOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Feature extractor', 'featureExtractor', [ "template", "old template", "histogram", "vertical histogram", "horizontal histogram"])

    def matcherOptions(self, frame, sizer):
        self.entry(frame, sizer, 'k nearest neighbors', 'k', '1')

    def linguistOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Linguist', 'linguist', ["n-gram", "no linguist"])
    
    def tabSet(self, frame):
        panel = wx.Panel(parent=frame)
        notebook = wx.aui.AuiNotebook(panel)
        tabParameters = [
            ('image', self.fileOptions, "Original"),
            ('binarized', self.binarizerOptions, "Binary"),
            ('segmented', self.segmenterOptions, "Segmented"),
            ('typesetter', self.typesetterOptions, "Typeset"),
            ('features', self.featureExtractorOptions, "Features"),
            ('matched', self.matcherOptions, "Matched"),
            ('output', self.linguistOptions, "Final output")
        ]
        
        for attr, options, name in tabParameters:
            notebook.AddPage(self.tab(notebook, attr, options), name)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)
    
    def __init__(self):
        self.filename = None
        self.app = wx.PySimpleApp()
        frame = wx.Frame(None, title="Optical Character Recognition", size=(600, 400))
        self.tabSet(frame)
        frame.Show()
        self.app.MainLoop()

    def update(self):
        if self.filename is None:
            print "No file selected"
        else:
            print "The file name is", self.filename

if __name__ == '__main__':
    TabWindow()
