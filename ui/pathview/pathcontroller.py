# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from tools.pathtool import PathTool
from tools.looptool import LoopTool
from tools.skiptool import SkipTool
from tools.breaktool import BreakTool
from tools.erasetool import EraseTool
from tools.forcetool import ForceTool
from tools.paintertool import PainterTool

class PathController(QObject):
    """
    Manages the interactions between Path widgets / UI elements and the model
    """
    def __init__(self, win):
        super(PathController, self).__init__()
        self.mainWindow = win
        win.actionPathSelect.triggered.connect(self.chooseSelectTool)
        win.actionPathMove.triggered.connect(self.chooseMoveTool)
        win.actionPathBreak.triggered.connect(self.chooseBreakTool)
        win.actionPathErase.triggered.connect(self.chooseEraseTool)
        win.actionPathForce.triggered.connect(self.chooseForceTool)
        win.actionPathInsertion.triggered.connect(self.chooseInsertTool)
        win.actionPathSkip.triggered.connect(self.chooseSkipTool)
        self.toolset = set((win.actionPathSelect, win.actionPathMove,\
                            win.actionPathBreak, win.actionPathErase,\
                            win.actionPathForce, win.actionPathInsertion,\
                            win.actionPathSkip))
        ag = QActionGroup(win)
        for a in self.toolset:
            ag.addAction(a)
        ag.setExclusive(True)
        self.currentTool = None
        self.chooseSelectTool()
        self.toolUse = False    # flag for using a specfic tool in the scene
        self.toolHoverEnter = None
        self.toolHoverLeave = None
        self.toolHoverMove = None
        self.toolPress = None
        self._activeTool = PainterTool()
        self.insertionTool = LoopTool(pathcontroller=self, parent=None)
        self.skipTool = SkipTool(pathcontroller=self, parent=None)
        self.breakTool = BreakTool(pathcontroller=self, parent=None)
        self.eraseTool = EraseTool(pathcontroller=self, parent=None)
        self.forceTool = ForceTool(pathcontroller=self, parent=None)

    def activeTool(self):
        return self._activeTool

    def chooseSelectTool(self):
        widget = self.mainWindow.actionPathSelect
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        self.toolUse = False
        widget.setChecked(True)

    def chooseMoveTool(self):
        widget = self.mainWindow.actionPathMove
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        widget.setChecked(True)

    def chooseBreakTool(self):
        widget = self.mainWindow.actionPathBreak
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        self.enableTool(self.breakTool)
        widget.setChecked(True)

    def chooseEraseTool(self):
        widget = self.mainWindow.actionPathErase
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        self.enableTool(self.eraseTool)
        widget.setChecked(True)

    def chooseForceTool(self):
        widget = self.mainWindow.actionPathForce
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        self.enableTool(self.forceTool)
        widget.setChecked(True)

    def chooseInsertTool(self):
        widget = self.mainWindow.actionPathInsertion
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        self.enableTool(self.insertionTool)
        widget.setChecked(True)

    def chooseSkipTool(self):
        widget = self.mainWindow.actionPathSkip
        if self.currentTool is widget:
            return
        else:
            self.currentTool = widget
        self.enableTool(self.skipTool)
        widget.setChecked(True)

    def enableTool(self, tool):
        self.toolUse = True
        self.toolPress = tool.toolPress
        self.toolHoverEnter = tool.toolHoverEnter
        self.toolHoverLeave = tool.toolHoverLeave
        self.toolHoverMove = tool.toolHoverMove
    # end def