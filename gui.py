import wx
import wx.aui
import os
import ocr.extract
import copy
import random
import threading
import cv

PADDING_WIDTH = 4

OWL = "lemmling_Cartoon_owl.png"
OWL_DOWN = "lemmling_Cartoon_owl_depressed.png"

def name():
    return '/tmp/'+str(random.randint(1000, 1000000))+'.png'

class ImagePanel:
    def __init__(self, panel, side=wx.ALIGN_LEFT):
        self.panel = panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        bitmap = wx.StaticBitmap(panel)
        sizer.Add(bitmap, flag=side)
        panel.SetSizer(sizer)
        self.bitmap = bitmap

    def reload(self, path):
        self.image = wx.Image(path)

    def resize(self):
        frameWidth, frameHeight = self.panel.GetClientSizeTuple()
        imageWidth, imageHeight = self.image.GetSize().Get()
        if float(imageWidth)/imageHeight > float(frameWidth)/frameHeight:
            newWidth = frameWidth
            newHeight = int(imageHeight * (float(frameWidth) / imageWidth))
        else:
            newHeight = frameHeight
            newWidth = int(imageWidth * (float(frameHeight) / imageHeight))
        image = self.image.Copy().Rescale(newWidth, newHeight).ConvertToBitmap()
        self.bitmap.SetBitmap(image)

    def setText(self, text):
        filename = name()
        cv_im = ocr.extract.render("Arial", text)
        cv.SaveImage(filename, cv_im)
        self.reload(filename)

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

    def replaceText(self, panel, text, huge=False):
        panel.DestroyChildren()
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddSpacer(PADDING_WIDTH)
        vPanel = wx.Panel(parent=panel)
        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.AddSpacer(PADDING_WIDTH)
        text = wx.StaticText(parent=vPanel, label=text)
        if huge:
            text.SetFont(wx.Font(70, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        vSizer.Add(text, 1, wx.EXPAND)
        vPanel.SetSizer(vSizer)
        hSizer.Add(vPanel, 1, wx.EXPAND)
        panel.SetSizer(hSizer)
        panel.Layout()

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
        sizer.AddSpacer(PADDING_WIDTH)
        self.beside(parent, sizer, contents, expandLeft=False)

    def besideLabel(self, parent, sizer, name, right):
        def contents(panel):
            label = wx.StaticText(panel, label=name+": ")
            control = right(panel)
            return label, control
        sizer.AddSpacer(PADDING_WIDTH)
        self.beside(parent, sizer, contents)

    def entry(self, parent, sizer, name, attr, type):
        self.entries.append(attr)
        def contents(panel):
            entry = wx.TextCtrl(panel, value=str(getattr(ocr.defaultOptions, attr)))
            def changeText(*args):
                text = entry.GetValue()
                try:
                    value = type(text)
                except ValueError:
                    value = text
                setattr(self.options, attr, value)
            self.app.Bind(wx.EVT_TEXT, changeText, entry)
            return entry
        self.besideLabel(parent, sizer, name, contents)

    def setPanelOptions(self, panel, attr, parent):
        panel.DestroyChildren()
        sizer = wx.BoxSizer(wx.VERTICAL)
        for opt in ocr.dependentOptions:
            if opt.parent == attr and opt.parentValue == getattr(self.options, attr):
                self.entry(panel, sizer, opt.guiName(), opt.attrName(), opt.type)
        panel.SetSizer(sizer)
        panel.Layout()
        parent.Layout()

    def dropdown(self, parent, sizer, name, attr):
        dependentOptions = wx.Panel(parent=parent)
        options = ocr.classMap[attr].keys()
        default = getattr(ocr.defaultOptions, attr)
        def contents(panel):
             control = wx.ComboBox(panel, value=default, choices=options, style=wx.CB_DROPDOWN)
             def changeOption(*args):
                 oldValue = getattr(self.options, attr)
                 value = control.GetValue()
                 setattr(self.options, attr, value)
                 if value != oldValue:
                     self.setPanelOptions(dependentOptions, attr, parent)
             self.app.Bind(wx.EVT_COMBOBOX, changeOption, control)
             return control
        self.besideLabel(parent, sizer, name, contents)
        sizer.Add(dependentOptions, 0, wx.EXPAND)
        self.setPanelOptions(dependentOptions, attr, parent)

    def imageTabs(self, parent):
        notebook = wx.aui.AuiNotebook(parent, style=wx.aui.AUI_NB_TOP)
        tabParameters = [
            ('image', "Original"),
            ('binarized', "Binary"),
            ('segmented', "Segmented"),
            ('typesetter', "Typeset"),
            ('features', "Features"),
            ('matcher', "Matched"),
            ('output', "Final output")
        ]
        for attr, name in tabParameters:
            pass
            panel = wx.Panel(parent=notebook)
            imagePanel = ImagePanel(panel)
            setattr(self, attr, imagePanel)
            imagePanel.setText("No image loaded for %s" % attr)
            notebook.AddPage(panel, name)
        def redraw(*args):
            self.redrawPictures()
        notebook.Bind(wx.EVT_SIZE, redraw)
        return notebook

    def optionWidgets(self, parent):
        outerFrame = wx.Panel(parent=parent, style=wx.SUNKEN_BORDER)
        outerSizer = wx.BoxSizer(wx.HORIZONTAL)
        outerSizer.AddSpacer(PADDING_WIDTH)
        frame = wx.Panel(parent=outerFrame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        def updateFile():
            self.image.reload(self.options.target)
            self.image.resize()
        self.chooseFile(frame, sizer, "target", "No file loaded", "Choose file", callback=updateFile)
        self.entry(frame, sizer, 'Internal dimension of characters', 'dimension', int)
        self.dropdown(frame, sizer, 'Binarizer', 'binarizer')
        self.dropdown(frame, sizer, 'Segmenter', 'segmenter')
        self.dropdown(frame, sizer, 'Typesetter', 'typesetter')
        self.dropdown(frame, sizer, 'Feature extractor', 'featureExtractor')
        self.entry(frame, sizer, 'k nearest neighbors', 'k', int)
        self.dropdown(frame, sizer, 'Linguist', 'linguist')
        owlPanel = wx.Panel(parent=frame)
        self.owl = ImagePanel(owlPanel, wx.ALIGN_RIGHT)
        def depress(*args):
            self.owl.reload(OWL_DOWN)
            self.owl.resize()
        self.app.Bind(wx.EVT_LEFT_DOWN, depress, self.owl.bitmap)
        def doUpdate(*args):
            self.owl.reload(OWL)
            self.owl.resize()
            self.update()
        self.app.Bind(wx.EVT_LEFT_UP, doUpdate, self.owl.bitmap)
        self.owl.reload(OWL) 
        sizer.Add(owlPanel, 1, wx.EXPAND)
        sizer.AddSpacer(PADDING_WIDTH)
        frame.SetSizer(sizer)
        outerSizer.Add(frame, 1, wx.EXPAND)
        outerSizer.AddSpacer(PADDING_WIDTH)
        outerFrame.SetSizer(outerSizer)
        return outerFrame

    def mainView(self, frame):
        def contents(parent):
            return self.imageTabs(parent), self.optionWidgets(parent)
        self.beside(frame, None, contents, expandRight=False)

    def __init__(self):
        self.hasBeenRun = False
        self.options = copy.copy(ocr.defaultOptions)
        self.runner = ocr.OCRRunner()
        self.options.saveBinarized = name()
        self.options.saveSegmented = name()
        self.options.saveTypeset = name()
        self.options.saveFeatures = name()
        self.options.saveMatcher = name()
        self.options.target = None
        self.entries = []
        self.app = wx.App()
        frame = wx.Frame(None, title="Hoot! Optical Character Recognition", size=(1500, 700))
        frame.CreateStatusBar()
        def setStatus(status):
            wx.CallAfter(frame.SetStatusText, status)
        self.options.showStatus = setStatus
        self.mainView(frame)
        frame.Show()
        self.owl.resize()
        self.app.MainLoop()

    def update(self):
        for entry in self.entries:
            value = getattr(self.options, entry)
            if isinstance(value, str) or isinstance(value, unicode):
                dialog = wx.MessageDialog(None, '%s is not a valid for %s' % (value, entry), 'Invalid entry', wx.OK | wx.ICON_WARNING)
                dialog.ShowModal()
                dialog.Destroy()
                return None
        if self.options.target is not None:
            thread = threading.Thread(target=self.runThread)
            thread.start()

    def runThread(self):
        ocr.checkOptions(self.options)
        text = self.runner.withOptions(self.options)
        wx.CallAfter(self.updateComplete, text)

    def updateComplete(self, text):
        self.hasBeenRun = True
        self.reloadPictures()
        self.output.setText(text)
        self.redrawPictures()

    def reloadPictures(self):
        if self.options.target is not None:
            self.image.reload(self.options.target)
            if self.hasBeenRun:
                self.binarized.reload(self.options.saveBinarized)
                self.segmented.reload(self.options.saveSegmented)
                self.typesetter.reload(self.options.saveTypeset)
                self.features.reload(self.options.saveFeatures)
                self.matcher.reload(self.options.saveMatcher)

    def redrawPictures(self):
        if hasattr(self, 'owl') and hasattr(self.owl, 'image'):
            self.owl.resize()
            self.image.resize()
            self.binarized.resize()
            self.segmented.resize()
            self.typesetter.resize()
            self.features.resize()
            self.matcher.resize()
            self.output.resize()

if __name__ == '__main__':
    OCRWindow()
