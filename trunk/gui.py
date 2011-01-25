import wx
import wx.aui
import os
import ocr
import copy
import random

class OCRWindow(object):

    def beside(self, parent, sizer, contents, expandLeft=True):
        panel = wx.Panel(parent=parent)
        left, right = contents(panel)
        innerSizer = wx.BoxSizer(wx.HORIZONTAL)
        if expandLeft:
            innerSizer.Add(left, 1, wx.EXPAND)
        else:
            innerSizer.Add(left)
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
            spacer = wx.Panel(options)
            optionsSizer.Add(spacer, 1, flag=wx.EXPAND)
            updateButton = wx.Button(parent=options, label="Update")
            def doUpdate(*args):
                self.update()
            self.app.Bind(wx.EVT_BUTTON, doUpdate, updateButton)
            optionsSizer.Add(updateButton, flag=wx.ALIGN_RIGHT)
            options.SetSizer(optionsSizer)
            return textPanel, options
        return self.beside(notebook, None, contents)

    def replaceImage(self, panel, path):
        panel.DestroyChildren()
        wx.StaticBitmap(panel).SetBitmap(wx.Image(path).ConvertToBitmap())

    def replaceText(self, panel, text):
        panel.DestroyChildren()
        wx.StaticText(parent=panel, label=text)

    def chooseFile(self, parent, sizer, attr, defaultLabel, prompt):
        def contents(panel):
            button = wx.Button(panel, wx.ID_ANY, prompt)
            namePanel = wx.Panel(panel, wx.HORIZONTAL)
            self.replaceText(namePanel, "  "+defaultLabel)
            def chooseFile(evt):
                dialog = wx.FileDialog(parent, message=prompt, defaultDir=os.getcwd(), style=wx.OPEN)
                if dialog.ShowModal() == wx.ID_OK:
                    filename = dialog.GetPath()
                    setattr(self.options, attr, filename)
                    self.replaceText(namePanel, "  "+filename)
                dialog.Destroy()
            self.app.Bind(wx.EVT_BUTTON, chooseFile, button)
            return button, namePanel
        self.beside(parent, sizer, contents, expandLeft=False)
    
    def fileOptions(self, parent, sizer):
        self.chooseFile(parent, sizer, "target", "No file loaded", "Choose file")
        self.chooseFile(parent, sizer, "library", self.options.library, "Choose library path")

    def besideLabel(self, parent, sizer, name, right):
        def contents(panel):
            label = wx.StaticText(panel, label=name+": ")
            control = right(panel)
            return label, control
        self.beside(parent, sizer, contents)

    def dropdown(self, parent, sizer, name, attr):
        options = ocr.classMap[attr].keys()
        default = getattr(ocr.defaultOptions, attr)
        def contents(panel):
             control = wx.ComboBox(panel, value=default, choices=options, style=wx.CB_DROPDOWN)
             def changeOption(*args):
                 setattr(self.options, attr, control.GetValue())
             self.app.Bind(wx.EVT_COMBOBOX, changeOption, control)
             return control
        self.besideLabel(parent, sizer, name, contents)

    def entry(self, parent, sizer, name, attr, type):
        def contents(panel):
            entry = wx.TextCtrl(panel, value=str(getattr(ocr.defaultOptions, attr)))
            def changeText(*args):
                try:
                    text = entry.GetValue()
                    value = type(text)
                except ValueError:
                    wx.MessageBox('Invalid entry', '%s is not a valid %s for %s' % (text, type.__name__, name))
                    return None
                setattr(self.options, attr, value)
            self.app.Bind(wx.EVT_TEXT_ENTER, changeText, entry)
            return entry
        self.besideLabel(parent, sizer, name, contents)

    def binarizerOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Binarizer', 'binarizer')
    
    def segmenterOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Segmenter', 'segmenter')
    	
    def typesetterOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Typesetter', 'typesetter')
        self.entry(frame, sizer, 'Width of space', 'spaceWidth', float)

    def featureExtractorOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Feature extractor', 'featureExtractor')

    def matcherOptions(self, frame, sizer):
        self.entry(frame, sizer, 'k nearest neighbors', 'k', int)

    def linguistOptions(self, frame, sizer):
        self.dropdown(frame, sizer, 'Linguist', 'linguist')
    
    def tabSet(self, frame):
        panel = wx.Panel(parent=frame)
        notebook = wx.aui.AuiNotebook(panel, style=wx.aui.AUI_NB_TOP)
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
        self.options = copy.copy(ocr.defaultOptions)
        def name():
        	return '/tmp/'+str(random.randint(1000, 1000000))+'.png'
        self.options.saveBinarized = name()
        self.options.saveSegmented = name()
        self.options.saveTypeset = name()
        self.options.target = None
        self.app = wx.PySimpleApp()
        frame = wx.Frame(None, title="Optical Character Recognition", size=(1200, 700))
        self.tabSet(frame)
        frame.Show()
        self.app.MainLoop()

    def update(self):
        if self.options.target is not None:
            self.replaceImage(self.image, self.options.target)
            text = ocr.useOptions(ocr.processOptions(self.options))
            self.replaceImage(self.binarized, self.options.saveBinarized)
            self.replaceImage(self.segmented, self.options.saveSegmented)
            self.replaceImage(self.typesetter, self.options.saveTypeset)
            self.replaceText(self.features, "Feature extraction visualization not yet implemented")
            self.replaceText(self.matched, "Matcher visualization not yet implemented")
            self.replaceText(self.output, text)

if __name__ == '__main__':
    OCRWindow()
