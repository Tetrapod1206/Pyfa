# noinspection PyPackageRequirements
import wx

from service.fit import Fit
from .attributeSlider import AttributeSlider, EVT_VALUE_CHANGED

import gui.mainFrame
from gui.contextMenu import ContextMenu
from gui.bitmap_loader import BitmapLoader
import gui.globalEvents as GE
import gui.mainFrame

class ItemMutator(wx.Panel):

    def __init__(self, parent, stuff, item):
        wx.Panel.__init__(self, parent)
        self.stuff = stuff
        self.item = item
        self.timer = None
        self.activeFit = gui.mainFrame.MainFrame.getInstance().getActiveFit()
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.goodColor = wx.Colour(96, 191, 0)
        self.badColor = wx.Colour(255, 64, 0)

        self.event_mapping = {}

        for m in sorted(stuff.mutators.values(), key=lambda x: x.attribute.displayName):
            slider = AttributeSlider(self, m.baseValue, m.minMod, m.maxMod, not m.highIsGood)
            slider.SetValue(m.value, False)
            slider.Bind(EVT_VALUE_CHANGED, self.changeMutatedValue)
            self.event_mapping[slider] = m
            headingSizer = wx.BoxSizer(wx.HORIZONTAL)

            # create array for the two ranges
            min_t = [round(m.minValue, 3), m.minMod, None]
            max_t = [round(m.maxValue, 3), m.maxMod, None]

            # Then we need to determine if it's better than original, which will be the color
            min_t[2] = min_t[1] < 1 if not m.highIsGood else 1 < min_t[1]
            max_t[2] = max_t[1] < 1 if not m.highIsGood else 1 < max_t[1]

            # Lastly, we need to determine which range value is "worse" (left side) or "better" (right side)
            if (m.highIsGood and min_t[1] > max_t[1]) or (not m.highIsGood and min_t[1] < max_t[1]):
                better_range = min_t
            else:
                better_range = max_t

            if (m.highIsGood and max_t[1] < min_t[1]) or (not m.highIsGood and max_t[1] > min_t[1]):
                worse_range = max_t
            else:
                worse_range = min_t

            print("{}: \nHigh is good: {}".format(m.attribute.displayName, m.attribute.highIsGood))
            print("Value {}".format(m.baseValue))

            print(min_t)
            print(max_t)
            print(better_range)
            print(worse_range)

            font = parent.GetFont()
            font.SetWeight(wx.BOLD)

            headingSizer.Add(BitmapLoader.getStaticBitmap(m.attribute.icon.iconFile, self, "icons"), 0, wx.RIGHT, 10)

            displayName = wx.StaticText(self, wx.ID_ANY, m.attribute.displayName)
            displayName.SetFont(font)

            headingSizer.Add(displayName, 3, wx.ALL | wx.EXPAND, 0)

            range_low = wx.StaticText(self, wx.ID_ANY, "{} {}".format(worse_range[0], m.attribute.unit.displayName))
            range_low.SetForegroundColour(self.goodColor if worse_range[2] else self.badColor)

            range_high = wx.StaticText(self, wx.ID_ANY, "{} {}".format(better_range[0], m.attribute.unit.displayName))
            range_high.SetForegroundColour(self.goodColor if better_range[2] else self.badColor)

            headingSizer.Add(range_low, 0, wx.ALL | wx.EXPAND, 0)
            headingSizer.Add(wx.StaticText(self, wx.ID_ANY, " ── "), 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
            headingSizer.Add(range_high, 0, wx.RIGHT | wx.EXPAND, 10)

            mainSizer.Add(headingSizer, 0, wx.ALL | wx.EXPAND, 5)

            mainSizer.Add(slider, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
            mainSizer.Add(wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL), 0, wx.ALL | wx.EXPAND, 5)

        mainSizer.AddStretchSpacer()

        self.m_staticline = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        mainSizer.Add(self.m_staticline, 0, wx.EXPAND)

        bSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.saveBtn = wx.Button(self, wx.ID_ANY, "Save Attributes", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer.Add(self.saveBtn, 0, wx.ALIGN_CENTER_VERTICAL)

        mainSizer.Add(bSizer, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)

        self.SetSizer(mainSizer)
        self.Layout()

    def changeMutatedValue(self, evt):
        m = self.event_mapping[evt.Object]
        value = evt.Value
        sFit = Fit.getInstance()

        sFit.changeMutatedValue(m, value)
        if self.timer:
            self.timer.Stop()
            self.timer = None
        self.timer = wx.CallLater(1000, self.callLater)

    def callLater(self):
        self.timer = None
        print("recalc fit")
        sFit = Fit.getInstance()
        sFit.refreshFit(self.activeFit)
        # todo BUG: if fit is not currently active, this causes the changed fit to show...?
        wx.PostEvent(gui.mainFrame.MainFrame.getInstance(), GE.FitChanged(fitID=self.activeFit))

