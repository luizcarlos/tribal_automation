import sys, os, math, random, six
from PyQt4 import QtCore, QtGui
#from tribalMainWindowUi import Ui_TribalMainWindow
from tribalMainLayoutUi import Ui_TribalMainWindow


PYTHON_MAJOR_VERSION = sys.version_info.major
#if PYTHON_MAJOR_VERSION == 3:
# The major version if did not work because the block under that if would still
#be checked by python 2.n
# Instead, the six module provides:
#six.print_(*args, *, file=sys.stdout, end="n", sep=" ")
# This funtion behales like python 3.n native print() even in python 2.n

DEBUG = 1 #Boolean controling debug mode
GEN_LOG = open("GeneralLog.txt",'w')
DIR_LOG = open("DirectionCheckLog.txt",'w')
FOW_LOG = open("FollowDirectionCheckLog.txt",'w')
PNT_LOG = open("PaintEventLog.txt",'w')
#color constants
BACKGROUND = 0XFF000000
PEN_R = 0XFFFF0000
PEN_Y = 0XFFFFFF00
PEN_G = 0XFF00FF00
PEN_T = 0XFF00FFFF
PEN_B = 0XFF0000FF
PEN_V = 0XFFFF00FF
PEN = 0XFFFFFFFF
MIN_GAP = 3
SAFE_FA = 6 # Safety factor used to manipulate other gaps 
MAX_LEN = 100
#Exclusion Flag values:
# 00 : no impediment
# 01 : <  5 pixels to EDGE (too close)
# 10 : <= 5 pixels to another used pixel (too close)
# 11 : <= 5 pixels to seed pixel after
#minimunPixelCount reached 0
CLEAR = 0X00
EDGE  = 0X01
USED  = 0X02
SEED  = 0X03
DIR_STATE = ("CLEAR", "EDGE", "USED", "SEED")
#Constant "unit vectors"
# They are not all mathematical unity vector because the diagonals are realy
#length 2^(1\2)
# The objective is not mathematical correctness, but integer pixel
#manipulation.
# BLOCK contains the increments and decrements to give the coordinates of all 8
#pixels surrounding any given pixel.
# CROSS contains only the increments and decrements to give the coordinates of
#vertical and horizontal adjacent pixels to any given pixel, no diagonals.
# The 4 2D tuples with names ending in REC give the increments and decrements
#used to find the coordinates of the 5 unknown pixels arround a used pixel. This
#5 pixwls are used to test the viabilitlty of continuing in the direction in the
#name of the 2D tuple
#All coordinates relative to the last pixel used are ordered for clockwise
#rotation starting from the right. The  increments and decrements in the RECs
#are relative to the pixel being tested and no such ordering is atempted.
BLOCK = ( ( 1,  0), ( 1,  1), ( 0,  1), (-1,  1),(-1,  0),(-1, -1),\
          ( 0, -1), ( 1, -1) )
CROSS = ( ( 1,  0), ( 0,  1), (-1,  0), ( 0, -1))

RIGHT_REC = (( 0 ,  0), ( 0, -1), ( 0,  1), ( 1 ,  0), ( 1, -1), ( 1,  1))
DOWN__REC = (( 0 ,  0), ( 1,  0), (-1,  0), ( 0 ,  1), ( 1,  1), (-1,  1))
LEFT__REC = (( 0 ,  0), ( 0, -1), ( 0,  1), (-1 ,  0), (-1, -1), (-1,  1))
UP____REC = (( 0 ,  0), ( 1,  0), (-1,  0), ( 0 , -1), ( 1, -1), (-1, -1))

#constant indices for BLOCK. Do NOT use with CROSS
RIGHT_____ = 0
RIGHT_DOWN = 1
DOWN______ = 2
LEFT__DOWN = 3
LEFT______ = 4
LEFT__UP__ = 5
UP________ = 6
RIGHT_UP__ = 7

#constant indices for CROSS. Do NOT use with BLOCK
RIGHT = 0
DOWN_ = 1
LEFT_ = 2
UP___ = 3

DIRECTION = ("RIGHT_____", "RIGHT_DOWN", "DOWN______", "LEFT__DOWN",
             "LEFT______", "LEFT__UP__", "UP________", "RIGHT_UP__",)

class Node():
    """ node(int X, int Y, int Pen, list node_list)
     
    This class implements a linked list of points. Each node object represents
    a point in a graph and has 4 attributes:

    -X: integer X cordinate of the point.
    -Y: integer Y cordinate of the point.
    -C: integer color of the point. The PEN constants are recommended.
    -nodeList: list that should contain node type objects.

    By default, X and Y are initialized to the MIN_GAP constant, C is
    initialized to the PEN constant, and nodeList is initialized to an empty
    list"""
    
    def __init__(self, X = MIN_GAP, Y = MIN_GAP, C = PEN, nodeList = None):
        self.x = X
        self.y = Y
        self.c = C
        if not nodeList: #nodeList will always end up as a list object
            self.nodeList = []
        else:
            self.nodeList = nodeList

        
class TribalMainWindow(QtGui.QMainWindow, Ui_TribalMainWindow):
    def __init__(self):
        if DEBUG:
            six.print_("init initialised", file = GEN_LOG)
        #initialise parents
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        if DEBUG:
            six.print_("parents initialised", file = GEN_LOG)
        #initialise time and space
        self.timer = QtCore.QTimer()
        self.x0 = self.tribalLabel.x()
        self.y0 = self.tribalLabel.y()
        self.x1 = self.tribalLabel.width()
        self.y1 = self.tribalLabel.height()
        if DEBUG:
            six.print_("time and space initialised", file = GEN_LOG)
        #initialise image
        self.tribalImage = QtGui.QImage(self.x1, self.y1,
                                        QtGui.QImage.Format_RGB32)
        self.imageWidth  = self.tribalImage.width()
        self.imageHeight = self.tribalImage.height()
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        if DEBUG:
            six.print_("image width:", self.imageWidth, "and height:",
                  self.imageHeight, file = GEN_LOG)
        #initialise startPoint
        self.x0 = 0 + MIN_GAP # From now on,
        self.y0 = 0 + MIN_GAP #they are the boundaries of the tribal
        self.x1 = self.imageWidth  - MIN_GAP
        self.y1 = self.imageHeight - MIN_GAP
        self.p = 0 #count the number of iterations
        self.seedX = random.randint(self.x0 + MIN_GAP*2, self.x1 - MIN_GAP*2)
        self.seedY = random.randint(self.y0 + MIN_GAP*2, self.y1 - MIN_GAP*2)
        self.curD = 8 #currentDirection. No valid direction set yet.
        self.pointList = [(self.seedX, self.seedY)]#points to be drawn
        self.node = None #points that have been drawn
        self.curX = self.seedX
        self.curY = self.seedY
        random.seed()#this version tries to directly favor the last direction
        self.strait = random.randint(47, 53)#to favor a trait line
        self.turn = 100 - self.strait
        #least closeness allowed to avoid self crossing
        self.lC = range(MIN_GAP * SAFE_FA)
        self.minimunPixelCount = 9999 #when it gets to 0 we may close the loop
        if DEBUG:
            six.print_("start point = (", self.seedX, self.seedY, ")",
                  file = GEN_LOG)
            six.print_("background color = ", hex(BACKGROUND), file = GEN_LOG)
            six.print_("pen color = ", hex(PEN), file = GEN_LOG)
        #initialize image loop
        self.tribalImage.fill(BACKGROUND)
        six.print_("seed X", self.seedX, "seed Y", self.seedY)
        six.print_("cur X", self.curX, "cur Y", self.curY)
        self.tribalImage.setPixel(self.seedX, self.seedY, PEN_B)
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
        self.timer.start(100)
        self.update()
        
    """ The old first tempt at cheking directions
    def checkDirection(self):
        #Begin with 8 directions
        dirLi = [None] * 8 #hold all directions and blocking flags
        dirIt = range(8) #direction interator
        # initialise non-diagonal directions to CLEAR for choice
        for d in dirIt:
            if d % 2 == 0:
                dirLi[d] = [self.curX+BLOCK[d][0], self.curY+BLOCK[d][1], CLEAR]
            else:
                dirLi[d] = [self.curX+BLOCK[d][0], self.curY+BLOCK[d][1], USED]
        #Exclude al that are 5 pixels or less from an image EDGE
        for d in dirIt:
            for c in self.lC:
                if dirLi[d][0] + BLOCK[d][0] * c <= self.x0 + MIN_GAP:
                    dirLi[d][2] = EDGE #too close to left   EDGE 
                if dirLi[d][0] + BLOCK[d][0] * c >= self.x1 - MIN_GAP:
                    dirLi[d][2] = EDGE #too close to right  EDGE
                if dirLi[d][1] + BLOCK[d][1] * c <= self.y0 + MIN_GAP:
                    dirLi[d][2] = EDGE #too close to top    EDGE
                if dirLi[d][1] + BLOCK[d][1] * c >= self.y1 - MIN_GAP:
                    dirLi[d][2] = EDGE #too close to botton EDGE
        #Exclude all directions that put a pixel within 3 pixels of another
        # used pixel, except when at least 10000 pixels have been draw and the
        # used pixel is the seed pixel. In the cur case, the direction of the
        # seed pixel must be chosen.
        
        for d in dirIt: # exclude the line crossing itself
            if dirLi[d][2] == CLEAR: #skip the direcions already excluded
                for c in self.lC:
                    p = (dirLi[d][0] + BLOCK[d][0] * c,\
                         dirLi[d][1] + BLOCK[d][1] * c)
                    if self.tribalImage.pixel(p[0], p[1]) == PEN:
                                dirLi[d][2] = USED
        if self.minimunPixelCount <= 0: #allow connection with seed pixel
            for d in dirIt: # for all directions
                if dirLi[d][2] == USED: #if any is blocked
                    #check only potential crossing
                    for c in self.lC: # top through least closeness
                        p = (dirLi[d][0]+BLOCK[d][0]*c,\
                             dirLi[d][1]+BLOCK[d][1]*c)
                        if p[0] == self.seedX and p[1] == self.seedY:
                            dirLi[d][2] = SEED
        if DEBUG:
            for d in dirIt: # for all directions
                six.print_("direction: ", DIRECTION[d], DIR_STATE[dirLi[d][2]],
                      file = DIR_LOG)
            six.print_(file = DIR_LOG)
        return(dirLi)
    """

    def checkPoint(self, X, Y):
        """TribalMainWindow.checkPoint(self, int X, int Y) --> int point_state

        Thismethod of TribalMainWindow takes a pair of coordinates as integers,
        and returns the state of the point as an integer. which is one of the
        state state constants."""
        if X <= self.x0 or X >= self.x1: return EDGE #is X in range?
        if Y <= self.y0 or Y >= self.y1: return EDGE #is Y in range?
        #six.print_("pisxel color:",hex(self.tribalImage.pixel(X, Y)))
        if self.tribalImage.pixel(X, Y) != BACKGROUND:#is the non-edge used?
            if self.minimunPixelCount <= 0: # do we have enough points?
                if X == self.seedX and Y == self.seedY: #did we hit the seed?
                    return SEED
                else: return USED #no seed
            else: return USED #not enough points
        return CLEAR # found no sing that the point is taken
    
    def checkDirection(self):
        #Begin with 4 non-diagonal directions
        dirLi = [None] * 4 #hold non-diagonal directions and blocking flags
        dirIt = range(4) #direction interator
        recIt = range(6) #surrounding rectangle interator
        # Initialise non-diagonal directions to CLEAR and ckeck them
        # Note that unlike the previous version of this function, dirLi is
        #now based on CROSS not BLOCK.
        for d in dirIt:
             dirLi[d] = [self.curX+CROSS[d][0], self.curY+CROSS[d][1], CLEAR]
             
        for r in recIt: #check right
            state = self.checkPoint(self.curX+CROSS[RIGHT][0]+RIGHT_REC[r][0],
                                    self.curY+CROSS[RIGHT][1]+RIGHT_REC[r][1] )
            if not (state == CLEAR or state == SEED):
                dirLi[RIGHT][2] = state
                break # we proved that this direction cannot be used
        for r in recIt: #check down
            state = self.checkPoint(self.curX+CROSS[DOWN_][0]+DOWN__REC[r][0],
                                    self.curY+CROSS[DOWN_][1]+DOWN__REC[r][1] )
            if not (state == CLEAR or state == SEED):
                dirLi[DOWN_][2] = state
                break # we proved that this direction cannot be used
        for r in recIt: #check left
            state = self.checkPoint(self.curX+CROSS[LEFT_][0]+LEFT__REC[r][0],
                                    self.curY+CROSS[LEFT_][1]+LEFT__REC[r][1] )
            if not (state == CLEAR or state == SEED):
                dirLi[LEFT_][2] = state
                break # we proved that this direction cannot be used
        for r in recIt: #check up
            state = self.checkPoint(self.curX+CROSS[UP___][0]+UP____REC[r][0],
                                    self.curY+CROSS[UP___][1]+UP____REC[r][1] )
            if not (state == CLEAR or state == SEED):
                dirLi[UP___][2] = state
                break # we proved that this direction cannot be used
        
        if DEBUG:
            for d in dirIt: # for all directions
                six.print_("direction: ", DIRECTION[d], DIR_STATE[dirLi[d][2]],
                      file = DIR_LOG)
            six.print_(file = DIR_LOG)
        return(dirLi)

    
    def followDirection(self):
        if DEBUG:
            six.print_("direction:", self.curD, file = FOW_LOG)
        blocked = False
        e = 0 # line extention
        p =(self.curX + BLOCK[self.curD][0] * (e + MIN_GAP),\
            self.curY + BLOCK[self.curD][1] * (e + MIN_GAP))
        length = random.randint(0, MAX_LEN)
        while not blocked:
            if DEBUG:
                six.print_("while not blocked: point:", p, file = FOW_LOG)
            if p[0] not in range(self.x0, self.x1)\
            or p[1] not in range(self.y0, self.y1):
                if DEBUG:
                    six.print_("point out of bounds,", p, file = FOW_LOG)
                blocked = True
                break;
            elif self.tribalImage.pixel(p[0], p[1]) == PEN:
                if DEBUG:
                    six.print_("point bloked by a nother line,", p, file = FOW_LOG)
                blocked = True
                break;
            elif e >= length:
                if DEBUG:
                    six.print_("resulting line too long,", p, file = FOW_LOG)
                blocked = True
                break;
            else:
                e = e + 1
                p =(self.curX + BLOCK[self.curD][0] * (e + MIN_GAP),\
                    self.curY + BLOCK[self.curD][1] * (e + MIN_GAP) )
                if DEBUG:
                    six.print_("extention:", e, file = FOW_LOG)
        return e
        
    def chooseDirection(self):
        dirLi = self.checkDirection()
        openDirLi = []
        for d in range(4): #for all directions
            if dirLi[d][2] == SEED:
                openDirLi.append((dirLi[d], d))
                six.print_("TRIBAL DONE!!!!!!!")
                break; #ignore other potential open diretions and go to seed
            if dirLi[d][2] == CLEAR: # chose the ones not flaged as blocked
                openDirLi.append((dirLi[d], d))
                if d == self.curD: #favor last dirrection used
                    for l in range(self.strait):
                        openDirLi.append((dirLi[d], d))
                elif ((d + 2) % 8) == self.curD or ((d - 2) % 8) == self.curD:
                    for l in range(self.turn):
                        openDirLi.append((dirLi[d], d))
        if DEBUG:
            for d in range(len(openDirLi)): # for open all directions
                six.print_("direction: ", DIRECTION[openDirLi[d][1]],
                      DIR_STATE[openDirLi[d][0][2]], file = PNT_LOG)
        p = random.choice(openDirLi)# chose a random open direction
        self.curX = p[0][0]
        self.curY = p[0][1]
        self.curD = p[1]
        if DEBUG:
            six.print_("point = (", self.curX, ",", self.curY, ")",
                  "Direction = ", DIRECTION[self.curD], "minimum count = ",
                  self.minimunPixelCount, file = PNT_LOG)
        #I spent over an hour looking for this line. It was making the code
        #behave strangely because it is a Qt pre drawing command in what is now
        #completely an algorithmic function.
        #self.tribalImage.setPixel(self.curX, self.curY, PEN)
        if self.minimunPixelCount > 0:
            self.minimunPixelCount = self.minimunPixelCount - 1
        #c = self.followDirection() #c = number of points to be added
        #if DEBUG:
        #    six.print_("point(", self.curX, self.curY, ") c:", c, file = PNT_LOG)
        #for n in range(c):
        #    six.print_("add to X:", BLOCK[self.curD][0] * n, file = PNT_LOG)
        #    six.print_("add to Y:", BLOCK[self.curD][1] * n, file = PNT_LOG)
        #    self.curX = self.curX + BLOCK[self.curD][0]
        #    self.curY = self.curY + BLOCK[self.curD][1]
        #    six.print_("point(", self.curX, self.curY, ") n:", n, "in extention",
        #              file = PNT_LOG)


    def paintEvent(self, event):
        """This method of class Tribal main window is called by timeout event.

          It calls the chooseDirection method of the same class and uses the
        attributes curX and curY to draw a pixel in the internal image. Drawing
        is seting the color of that pixel to the constant PEN. This method
        directly handles the Qt aspect of drawing a pixel, not the algorith that
        choses where to draw the pixel."""
        self.p = self.p + 1
        six.print_("cur X", self.curX, "cur Y", self.curY)
        self.chooseDirection()
        self.tribalImage.setPixel(self.x0+self.p,self.y0+self.p, PEN_R)
        self.tribalImage.setPixel(self.x0+self.p,self.y1-self.p, PEN_Y)
        self.tribalImage.setPixel(self.x1-self.p,self.y0+self.p, PEN_G)
        self.tribalImage.setPixel(self.x1-self.p,self.y1-self.p, PEN_T)
        for point in self.pointList:
            #self.tribalImage.setPixel(point[0],point[1], PEN_R)
            """
            NPN = self.node #New Point Node
            while NPN != None:
                children = self.node.nodeList
                for c in children:
                    NPN = c
            """
        self.tribalImage.setPixel(self.curX, self.curY, PEN_B)
        self.tribalLabel.setPixmap(QtGui.QPixmap.fromImage(self.tribalImage))
        self.update()

def main():
    app = QtGui.QApplication(sys.argv)
    tmw = TribalMainWindow()
    tmw.show()
    sys.exit(app.exec_())

if __name__ == '__main__': main()
