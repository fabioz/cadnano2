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

import util, sys
util.qtWrapImport('QtCore', globals(), ['QObject'])
from model.normalstrand import NormalStrand
from operation import Operation
from model.vbase import VBase

class SelectToolOperation(Operation):
    """
    Handles interactive strand creation / destruction in the manner of the
    SelectTool.
    """
    logger = None
    imposeDragBounds = True

    def __init__(self, startVBase, undoStack):
        """ Begin a session of select-tool interaction """
        Operation.__init__(self, undoStack)
        self.newStrand = NormalStrand(startVBase, startVBase)
        self.newVStrand = self.newStrand.vStrand()
        self.startVBase = startVBase
        self.lastDestVBase = startVBase
        self.newStrandInVfbPool = False
        if self.imposeDragBounds:  # calculate drag boundaries
            self.dragBoundL, self.dragBoundR = 0, startVBase.part().dimensions()[2]-1
            strandBeforeIdx, strandAtIdx, strandAfterIdx = \
                            self.newVStrand.strandsNearVBase(self.startVBase)
            if strandBeforeIdx != None:
                self.dragBoundL = strandBeforeIdx.idxs()[1]
            if strandAfterIdx != None:
                self.dragBoundR = strandAfterIdx.idxs()[0]-1
        self.updateDestination(startVBase)
        if self.logger: self.logger.write('SelectToolOperation.init(%s)\n'%startVBase)

    def updateDestination(self, newDestVBase):
        """ Looks at self.startVBase and newDestVBase then calls the appropriate
        actionWhatever method on self. """
        if isinstance(newDestVBase, (int, long)):
            newDestVBase = VBase(self.startVBase.vStrand, newDestVBase)
        if newDestVBase == self.lastDestVBase:
            return
        else:
            self.lastDestVBase = newDestVBase
        self.rewind()
        dragStartBase, dragEndBase = self.startVBase, newDestVBase
        dragStartExposedEnds = dragStartBase.exposedEnds()
        dragStartStrand = dragStartBase.strand()
        dragEndStrand = dragEndBase.strand()
        startIdx, endIdx = dragStartBase.vIndex(), dragEndBase.vIndex()
        vStrand = dragStartBase.vStrand()

        if not isinstance(newDestVBase, VBase):
            print "not instance VBase"
            return

        if self.imposeDragBounds:
            if endIdx < self.dragBoundL:
                endIdx = self.dragBoundL
            elif endIdx > self.dragBoundR:
                endIdx = self.dragBoundR

        if 'R' in dragStartExposedEnds:
            if endIdx < startIdx:
                # Dragging a right-facing endpoint left
                vStrand.clearStrand(endIdx + 1, startIdx + 1,\
                                    useUndoStack=True, undoStack=self.undoStack)
            elif startIdx < endIdx:
                # Dragging a right-facing endpoint right
                vStrand.connectStrand(startIdx, endIdx,\
                                    useUndoStack=True, undoStack=self.undoStack)
            else:
                pass  # Click on an endpoint
        elif 'L' in dragStartExposedEnds:
            if endIdx < startIdx:
                # Dragging a left-facing endpoint left
                vStrand.connectStrand(endIdx, startIdx,\
                                    useUndoStack=True, undoStack=self.undoStack)
            elif startIdx < endIdx:
                # Dragging a left-facing endpoint right
                vStrand.clearStrand(startIdx, endIdx,\
                                    useUndoStack=True, undoStack=self.undoStack)
            else:
                pass  # Click on an endpoint
        else:
            vStrand.connectStrand(startIdx, endIdx,\
                                  useUndoStack=True, undoStack=self.undoStack)

    def end(self):
        """ Make the changes displayed by the last call to
        updateDestination permanent """
        if self.logger:
            self.logger.write('SelectToolOperation.end\n')
        del self.newStrand
        del self.startVBase
        del self.newStrandInVfbPool

    def actionNone(self):
        if self.logger:
            self.logger.write('SelectToolOperation.actionNone\n')

    def actionAddStrand(self, lConnection, startBase, endBase, rConnection):
        if self.logger:
            self.logger.write('SelectToolOperation.actionAddStrand\n')
        newStrand, undoStack = self.newStrand, self.undoStack
        undoStack.beginMacro('actionAddStrand')
        newStrand.changeRange(startBase, endBase, undoStack)
        startBase.vStrand.addStrand(newStrand, useUndoStack=True, undoStack=undoStack)
        newStrand.setConnL(lConnection, useUndoStack=True, undoStack=undoStack)
        newStrand.setConnR(rConnection, useUndoStack=True, undoStack=undoStack)
        undoStack.endMacro()

    def actionJustConnect(self, lStrand, rStrand):
        """ Just connect the right exposed end of lStrand to the left exposed
        end of rStrand """
        if self.logger:
            self.logger.write('SelectToolOperation.actionJustConnect\n')
        lStrand.setConnR(rStrand, useUndoStack=True, undoStack=self.undoStack)

    def actionResizeStrand(self, strand, newL, newR):
        if self.logger:
            self.logger.write('SelectToolOperation.actionResizeStrand\n')
        newL.vStrand.resizeStrandAt(strand.vBaseL, newL, newR, useUndoStack=True, undoStack=self.undoStack)

    def actionClearRange(self, firstIdx, afterLastIdx, keepLeft=True):
        if self.logger:
            self.logger.write('SelectToolOperation.actionClearRange\n')
        self.startVBase.vStrand.clearRange(firstIdx,\
                                           afterLastIdx,\
                                           useUndoStack=True,\
                                           undoStack=self.undoStack,\
                                           keepLeft=keepLeft)