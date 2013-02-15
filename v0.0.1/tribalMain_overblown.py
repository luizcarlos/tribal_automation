import sys, os, math, random
from PyQt4 import QtCore, QtGui
#from tribalMainWindowUi import Ui_TribalMainWindow
from tribalMainLayoutUi import Ui_TribalMainWindow

#window = QtGui.QDialog()
#window = QtGui.QMainWindow()
#ui = Ui_TribalMainWindow()
#ui.setupUi(window)
#timer = QtCore.QTimer()

#color constants
BACKGROUND = 0XFF000000
PEN = 0XFFFFFFFF
MIN_GAP = 10
#Exclusion Flag values:
# 00.0000.0000 : no impediment
# 01.0000.0000 : <  5 pixels to EDGE (too close)
# 10.nnnn.nnnn : <= 3 pixels to another used pixel (too close)
# 10.0000.0001 : <= 3 pixels to another used pixel right
# 10.0000.0010 : <= 3 pixels to another used pixel right-down
# 10.0000.0100 : <= 3 pixels to another used pixel down
# 10.0000.1000 : <= 3 pixels to another used pixel left-down
# 10.0001.0000 : <= 3 pixels to another used pixel left
# 10.0010.0000 : <= 3 pixels to another used pixel left-up
# 10.0100.0000 : <= 3 pixels to another used pixel Up
# 10.1000.0000 : <= 3 pixels to another used pixel right-Up
# 11.0000.0000 : <= 3 pixels to seed pixel after
#minimunPixelCount reached 0
CLEAR = 0X0000
EDGE = 0X0100
#Flags for BLOCKed by used pixels are in a sigle data structure
# allow easy looping through directions
BLOCK = ( ( 1,  0, 0X0201), ( 1,  1, 0X0202), ( 0,  1, 0X0204), \
          (-1,  1, 0X0208), (-1,  0, 0X0210), (-1, -1, 0X0220), \
          ( 0, -1, 0X0240), ( 1, -1, 0X0280) )
seed = 0X0300


class TribalMainWindow(QtGui.QMainWindow, Ui_TribalMainWindow):
    def __init__(self):
        print("init initialised")
        #initialise parents
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        print("parents initialised")
        #initialise time and space
        self.timer = QtCore.QTimer()
        self.x0 = self.tribalLabel.x()
        self.y0 = self.tribalLabel.y()
        self.x1 = self.tribalLabel.width()
        self.y1 = self.tribalLabel.height()
        print("time and space initialised")
        #initialise image
        self.tribalImage = QtGui.QImage(self.x1, self.y1,
                                        QtGui.QImage.Format_RGB32)
        self.imageWidth  = self.tribalImage.width()
        self.imageHeight = self.tribalImage.height()
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        print("image width:", self.imageWidth, "and height:", self.imageHeight)
        #initialise startPoint
        self.x0 = 0 + MIN_GAP #from now on tey are the boundaries o the tribal
        self.y0 = 0 + MIN_GAP
        self.x1 = self.imageWidth  - MIN_GAP
        self.y1 = self.imageHeight - MIN_GAP
        self.seedX = random.randint(self.x0 + MIN_GAP*2, self.x1 - MIN_GAP*2)
        self.seedY = random.randint(self.y0 + MIN_GAP*2, self.y1 - MIN_GAP*2)
        
        self.lastX = self.seedX
        self.lastY = self.seedY
        self.lC = range(MIN_GAP)#least closeness allowed to avoid self crossing
        self.minimunPixelCount = 9999 #when it gets to 0 we may close the loop
        print("start point = (", self.seedX, self.seedY, ")")
        print("background color = ", hex(BACKGROUND))
        print("pen color = ", hex(PEN))
        #initialize image loop
        self.tribalImage.fill(BACKGROUND)
        self.tribalImage.setPixel(self.seedX, self.seedY, PEN)
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
        self.timer.start(100)
        self.update()

    def chooseDirection(self):
        #Begin with 8 directions
        dirLi = [None] * 8 #hold all directions and usefullness flag
       
        # initialise all directions to CLEAR for choice
        dirLi[0] = [self.lastX+BLOCK[0][0], self.lastY+BLOCK[0][1], CLEAR]
        dirLi[1] = [self.lastX+BLOCK[1][0], self.lastY+BLOCK[1][1], CLEAR]
        dirLi[2] = [self.lastX+BLOCK[2][0], self.lastY+BLOCK[2][1], CLEAR]
        dirLi[3] = [self.lastX+BLOCK[3][0], self.lastY+BLOCK[3][1], CLEAR]
        dirLi[4] = [self.lastX+BLOCK[4][0], self.lastY+BLOCK[4][1], CLEAR]
        dirLi[5] = [self.lastX+BLOCK[5][0], self.lastY+BLOCK[5][1], CLEAR]
        dirLi[6] = [self.lastX+BLOCK[6][0], self.lastY+BLOCK[6][1], CLEAR]
        dirLi[7] = [self.lastX+BLOCK[7][0], self.lastY+BLOCK[7][1], CLEAR]
        #print(dirLi)
        dirIt = range(8) #direction interator
        #Exclude al that are 5 pixels o less from an image EDGE
        for d in dirIt:
            if dirLi[d][0] <= self.x0:
                dirLi[d][2] = EDGE #too close to left   EDGE 
            if dirLi[d][0] >= self.x1:
                dirLi[d][2] = EDGE #too close to right  EDGE
            if dirLi[d][1] <= self.y0:
                dirLi[d][2] = EDGE #too close to top    EDGE
            if dirLi[d][1] >= self.y1:
                dirLi[d][2] = EDGE #too close to botton EDGE
        #Exclude all directions that put a pixel within 3 pixels of another
        # used pixel, except when at least 1000 pixels have been draw and the
        # used pixel is the seed pixel. In the last case, the direction of the
        # seed pixel must be chosen.
        for d in dirIt: # exclude the line crossing itself
            if dirLi[d][2] == CLEAR: #skip the direcions already excluded
                for c in self.lC:
                    p = (dirLi[d][0]+BLOCK[0][0]*c, dirLi[d][1]+BLOCK[0][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[0][2]
                    p = (dirLi[d][0]+BLOCK[1][0]*c, dirLi[d][1]+BLOCK[1][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[1][2]
                    p = (dirLi[d][0]+BLOCK[2][0]*c, dirLi[d][1]+BLOCK[2][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[2][2]
                    p = (dirLi[d][0]+BLOCK[3][0]*c, dirLi[d][1]+BLOCK[3][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[3][2]
                    p = (dirLi[d][0]+BLOCK[4][0]*c, dirLi[d][1]+BLOCK[4][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[4][2]
                    p = (dirLi[d][0]+BLOCK[5][0]*c, dirLi[d][1]+BLOCK[5][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[5][2]
                    p = (dirLi[d][0]+BLOCK[6][0]*c, dirLi[d][1]+BLOCK[6][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[6][2]
                    p = (dirLi[d][0]+BLOCK[7][0]*c, dirLi[d][1]+BLOCK[7][1]*c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                        dirLi[d][2] = dirLi[d][2] | BLOCK[7][2]
            print("direction List: ",dirLi)
        if self.minimunPixelCount == 0: #allow connection with seed pixel
            for d in dirIt: # for all directions
                if dirLi[d][2] in range(0X0201, 0X0300): #if any is BLOCKed
                    #check only potential crossing
                    for bD in range(8): #all directions that can be BLOCKed
                        if bin(dirLi[bD][2])[4::][7 - bD] == '1':
                            #filter specific direction status
                            for c in self.lC: # top through least closeness
                                p = (dirLi[d][0]+BLOCK[bD][0]*c, \
                                     dirLi[d][1]+BLOCK[bD][1]*c)
                                if p[0] == self.seedX and p[1] == self.seedY:
                                    dirLi[d][2] = seed
        return(dirLi)
    
    def paintEvent(self, event):
        dirLi = self.chooseDirection()
        openDirLi = []
        for d in range(8): #for all directions
            if dirLi[d][2] != 0: # chose the ones not flaged as blocked
                openDirLi.append((dirLi[d], d))
        p = random.choice(openDirLi)# chose a random open direction
        self.lastX = p[0][0]
        self.lastY = p[0][1]
        print("point", self.lastX, self.lastY)
        self.tribalImage.setPixel(self.lastX, self.lastY, PEN)
        ext = random.randint(MIN_GAP / MIN_GAP, MIN_GAP - 2)
        for e in range(ext):#try to made random strait line out of 1 point
            self.lastX = self.lastX + BLOCK[p[1]][0] * e
            self.lastY = self.lastY + BLOCK[p[1]][1] * e
            print("point", self.lastX, self.lastY, "EXT")
            self.tribalImage.setPixel(self.lastX, self.lastY, PEN)
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        self.update()

def main():
    app = QtGui.QApplication(sys.argv)
    tmw = TribalMainWindow()
    #connect signals and slots
    #ui.addComponentButton.clicked.connect(addComponent)
    #ui.actionSave_Recipe.triggered.connect(saveRecipe)
    #seed = seedTribal(ui.DrawPanelWidget)
    #print(seedPoint)
    #timer.timeout.connect(paintTribal)
    #window.show()
    tmw.show()
    #paintTribal(ui.DrawPanelWidget, seed)
    sys.exit(app.exec_())

if __name__ == '__main__': main()
