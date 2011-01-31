import wx
import wx.aui
import os
import ocr
import copy
import random

class OCRWindow(object):

    def beside(self, parent, sizer, contents, expandLeft=True, expandRight=True):
        panel = wx.Panel(parent=parent)
        left, right = contents(panel)
        innerSizer = wx.BoxSizer(wx.HORIZONTAL)
        def addExpanding(contents, expand):
            innerSizer.Add(contents, 1 if expand else 0, wx.EXPAND)
        addExpanding(left, expandLeft)
        addExpanding(right, expandRight)
        panel.SetSizer(innerSizer)
        if sizer is not None: sizer.Add(panel, 0, wx.EXPAND)
        return panel

    def replaceImage(self, panel, path):
        panel.DestroyChildren()
        frameWidth, frameHeight = panel.GetClientSizeTuple()
        image = wx.Image(path) 
        imageWidth, imageHeight = image.GetSize().Get()
        if float(imageWidth)/imageHeight > float(frameWidth)/frameHeight:
            newWidth = frameWidth
            newHeight = int(imageHeight * (float(frameWidth) / imageWidth))
        else:
            newHeight = frameHeight
            newWidth = int(imageWidth * (float(frameHeight) / imageHeight))
        wx.StaticBitmap(panel).SetBitmap(image.Rescale(newWidth, newHeight).ConvertToBitmap())

    def replaceText(self, panel, text):
        panel.DestroyChildren()
        wx.StaticText(parent=panel, label=text)

    def chooseFile(self, parent, sizer, attr, defaultLabel, prompt, callback=lambda: None):
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
                    callback()
                dialog.Destroy()
            self.app.Bind(wx.EVT_BUTTON, chooseFile, button)
            return button, namePanel
        self.beside(parent, sizer, contents, expandLeft=False)

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

    def imageTabs(self, parent):
        notebook = wx.aui.AuiNotebook(parent, style=wx.aui.AUI_NB_TOP)
        tabParameters = [
            ('image', "Original"),
            ('binarized', "Binary"),
            ('segmented', "Segmented"),
            ('typesetter', "Typeset"),
            ('features', "Features"),
            ('matched', "Matched"),
            ('output', "Final output")
        ]
        for attr, name in tabParameters:
            textPanel = wx.Panel(parent=notebook)
            setattr(self, attr, textPanel)
            text = wx.StaticText(parent=textPanel, label="No image loaded for %s" % attr)
            notebook.AddPage(textPanel, name)
        return notebook

    def optionWidgets(self, parent):
        frame = wx.Panel(parent=parent, style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        def updateFile():
            print 'called it'
            self.replaceImage(self.image, self.options.target)
        self.chooseFile(frame, sizer, "target", "No file loaded", "Choose file", callback=updateFile)
        self.chooseFile(frame, sizer, "library", self.options.library, "Choose library path")
        self.dropdown(frame, sizer, 'Binarizer', 'binarizer')
        self.dropdown(frame, sizer, 'Segmenter', 'segmenter')
        self.dropdown(frame, sizer, 'Typesetter', 'typesetter')
        self.entry(frame, sizer, 'Width of space', 'spaceWidth', float)
        self.dropdown(frame, sizer, 'Feature extractor', 'featureExtractor')
        self.entry(frame, sizer, 'k nearest neighbors', 'k', int)
        self.dropdown(frame, sizer, 'Linguist', 'linguist')
        spacer = wx.Panel(frame)
        sizer.Add(spacer, 1, flag=wx.EXPAND)
        updateButton = wx.Button(parent=frame, label="Update")
        def doUpdate(*args):
            self.update()
        self.app.Bind(wx.EVT_BUTTON, doUpdate, updateButton)
        sizer.Add(updateButton, flag=wx.ALIGN_RIGHT)
        frame.SetSizer(sizer)
        return frame
    
    def mainView(self, frame):
        def contents(parent):
            return self.imageTabs(parent), self.optionWidgets(parent)
        self.beside(frame, None, contents, expandRight=False)

    def __init__(self):
        self.options = copy.copy(ocr.defaultOptions)
        def name():
        	return '/tmp/'+str(random.randint(1000, 1000000))+'.png'
        self.options.saveBinarized = name()
        self.options.saveSegmented = name()
        self.options.saveTypeset = name()
        self.options.saveFeatures = name()
        self.options.target = None
        self.app = wx.PySimpleApp()
        frame = wx.Frame(None, title="Optical Character Recognition", size=(1200, 700))
        self.mainView(frame)
        frame.Show()
        self.app.MainLoop()

    def update(self):
        if self.options.target is not None:
            self.replaceImage(self.image, self.options.target)
            text = ocr.useOptions(ocr.processOptions(self.options))
            self.replaceImage(self.binarized, self.options.saveBinarized)
            self.replaceImage(self.segmented, self.options.saveSegmented)
            self.replaceImage(self.typesetter, self.options.saveTypeset)
            self.replaceImage(self.features, self.options.saveFeatures)
            self.replaceText(self.matched, "Matcher visualization not yet implemented")
            self.replaceText(self.output, text)

if __name__ == '__main__':
    OCRWindow()
