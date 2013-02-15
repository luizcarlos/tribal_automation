import sys, os, math, random
from PyQt4 import QtCore, QtGui
#from TribalAnalysisWindowUi import Ui_TribalAnalysisWindow
from tribalMainLayoutUi import Ui_TribalMainWindow

GEN_LOG = open("GeneralAnalysisLog.txt",'w')
DIR_LOG = open("DirectionFindLog.txt",'w')
FOW_LOG = open("FollowDirectionCheckLog.txt",'w')
PNT_LOG = open("PaintAnalysisLog.txt",'w')
#color constants
BACKGROUND  = int(0XFFFFFFFF)
BACKGROUND1 = int(0XFF7F7F7F)
PEN  = int(0XFF000000)
PEN1 = int(0XFFFF0000)
#Constant "unit vectors"
# They are not all mathematical unity vector because the diagonals are realy
#length 2^(1\2)
# The objective is not mathematical correctness, but integer pixel
#manipulation.
#Mathematicaly, center and undefied are equal, no increment and no decrement,
#but center is intended as program marker for an intended objective, while
#undefined is intended for an error state. Neither situation demands change in
# pixel coordinates. Those values might be increased it this proram is ever
#expanded to 3D.
BLOCK = ( ( 1,  0), ( 1,  1), ( 0,  1), (-1,  1),(-1,  0),(-1, -1),\
          ( 0, -1), ( 1, -1), ( 0,  0), ( 0,  0) )
DIRECTION = ("RIGHT_____", "RIGHT_DOWN", "DOWN______", "LEFT__DOWN",\
             "LEFT______", "LEFT__UP__", "UP________", "RIGHT_UP__",\
             "CENTER____", "UNDEFINED_")
RIGHT_____ = 0
RIGHT_DOWN = 1
DOWN______ = 2
LEFT__DOWN = 3
LEFT______ = 4
LEFT__UP__ = 5
UP________ = 6
RIGHT_UP__ = 7
CENTER____ = 8
UNDEFINED_ = 9

class TribalAnalysisWindow(QtGui.QMainWindow, Ui_TribalMainWindow):
    def __init__(self):
        print("init initialised", file = GEN_LOG)
        #initialise parents
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        print("parents initialised", file = GEN_LOG)
        #initialise time and image space
        self.timer = QtCore.QTimer()
        self.tribalImage = QtGui.QImage("tribal_complex_2_re_edited.bmp")
        #                               QtGui.QImage.Format_RGB32)
        self.imageWidth  = self.tribalImage.width()
        self.imageHeight = self.tribalImage.height()
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        print("image width:", self.imageWidth, "and height:",self.imageHeight,\
              file = GEN_LOG)
        #initialise startPoint and direction variables
        self.startX = 0 #X coordinate of the first point foundin the loop tribal
        self.startY = 0 #Y coordinate of the first point foundin the loop tribal
        self.done = False #Flag used to denote a completed loop 
        self.curD = 0 #current direction where the next pixel will be found.
        self.auxD = UNDEFINED_ #used with diagonals only
        #thisis not a direct representaton of a direction but an index that
        #corresponds to the same direction in the 2 constant lists, BLOCK and
        #DIRECTION
        self.dirLi = [None] * 8 #direction list holds colors of all surronding
        #pixels
        self.dirIt = range(8) #direction interator
        self.adjacentIt = range(0, 8, 2) #adjacent direction iterator
        self.diagonalIt = range(1, 8, 2) #diagonal direction iterator
        self.pointCount = 1 # count the first valid point below
        #Find find first valid tribal point in row major order
        while (not self.tribalImage.pixel(self.startX, self.startY) == PEN)\
          and (self.startY < self.imageHeight):
            self.startX += 1
            if self.startX >= self.imageWidth:
                self.startX = 0
                self.startY += 1
            print("(", self.startX, ",", self.startY, ") :",\
                  hex(self.tribalImage.pixel(self.startX, self.startY)), file = GEN_LOG)        
        self.curX = self.startX
        self.curY = self.startY
        print("start point = (", self.startX, self.startY, ")",
              file = GEN_LOG)
        print("background color = ", hex(BACKGROUND), file = GEN_LOG)
        print("pen color = ", hex(PEN), file = GEN_LOG)
        self.tribalImage.setPixel(self.startX, self.startY, PEN1)
        print("|", str(self.curX).zfill(4), "|", str(self.curY).zfill(4),\
              "|", self.curD,"|",DIRECTION[self.curD],\
              "|", str(self.pointCount).zfill(6), "|",\
              sep = '', file = PNT_LOG)
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
        self.timer.start(1)
        self.update()

    def checkSurrounding(self, x = -1 , y = -1):
        if x < 0: x = self.curX
        if y < 0: y = self.curY
        surroundLi = [None] * 8 #list holds colors of all surronding pixels
        #Begin by reading all 8 directions
        print("from P:(", str(x).zfill(4), ",", str(y).zfill(4), ")",
              sep = '', file = DIR_LOG)
        #A local d is used to avoid conflict, but self.dirIt is never changed
        for d in self.dirIt:
            surroundLi[d] =\
               self.tribalImage.pixel(x + BLOCK[d][0],y + BLOCK[d][1])
            print("surroundLi[", d, "] =", hex(surroundLi[d]), file = DIR_LOG)
        return surroundLi #self.dirLi contains

    def findDirection(self):
        self.dirLi = self.checkSurrounding()
        found = False
        for self.curD in self.adjacentIt: #check all non-diagonals
            if self.dirLi[self.curD] == PEN:
                self.auxD = UNDEFINED_ #Not needed now
                found = True
                break
        if not found: #if no adjacent pixel was found
            for self.curD in self.diagonalIt: #check all diagonals
                if self.dirLi[self.curD] == PEN:
                    self.auxD = self.curD - 1 # get the previous non-diagonal
                    localLi = self.checkSurrounding(\
                                   self.curX + BLOCK[self.auxD][0],\
                                   self.curY + BLOCK[self.auxD][1])
                    if PEN in localLi:
                        self.auxD += 2
                        if self.auxD == 8:
                            self.auxD = 0
                    found = True
                    break
        #if found: #if a diagonal pixel was found
        #    self.auxD = self.curD - 1 # get the previous non-diagonal
        #    localLi = self.checkSurrounding(self.curX + BLOCK[self.auxD][0],
        #                                    self.curY + BLOCK[self.auxD][1])
        #    if PEN in localLi:
        #        self.auxD += 2
        #        if self.auxD == 8:
        #            self.auxD = 0
        #        #self.curX = self.curX + BLOCK[d][0]
        #        #self.curY = self.curY + BLOCK[d][1]
        #        #self.tribalImage.setPixel(self.curX, self.curY, PEN)
        #        #self.tribalLabel.setPixmap(\
        #        #    QtGui.QPixmap.fromImage(self.tribalImage))
        #        #self.update()
                
        if not found: # no diredtion found, did we cover the entire line?
            for self.curD in self.dirIt: 
                if  self.curX + BLOCK[self.curD][0] == self.startX\
                and self.curY + BLOCK[self.curD][1] == self.startY:
                    self.curD = CENTER____
                    break
            if not self.curD == CENTER____:#The bad news case
                # if we are here the tribal is not a closed loop
                self.curD = UNDEFINED_
                print("isolated colored pixel! at: (", self.curX, ", ",\
                      self.curY, ")", file = DIR_LOG)
        return None #d has the direction of the next pixel
               
    def paintEvent(self, event):
        if self.curD < CENTER____:#if we got a meaningful direction
            self.findDirection()
            if self.auxD < CENTER____:
                self.tribalImage.setPixel(self.curX + BLOCK[self.auxD][0],
                                          self.curY + BLOCK[self.auxD][1], PEN1)
                
            self.curX = self.curX + BLOCK[self.curD][0]
            self.curY = self.curY + BLOCK[self.curD][1]
            self.pointCount = self.pointCount + 1
            print("|", str(self.curX).zfill(4), "|", str(self.curY).zfill(4),\
                  "|", self.curD,"|",DIRECTION[self.curD],\
                  "|", str(self.pointCount).zfill(6), "|",\
                  sep = '', file = PNT_LOG)
            self.tribalImage.setPixel(self.curX, self.curY, PEN1)
            
            self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
            self.update()
        else:
            if not self.done:
                print("TRIBAL DONE!!!!!!!", file = PNT_LOG)
                self.tribalImage.save("tribal_complex_2_red_edited.bmp")
                self.done = True
        

def main():
    app = QtGui.QApplication(sys.argv)
    tmw = TribalAnalysisWindow()
    tmw.show()
    sys.exit(app.exec_())

if __name__ == '__main__': main()
