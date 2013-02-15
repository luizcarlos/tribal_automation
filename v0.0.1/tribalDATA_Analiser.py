import sys, os, math, random
from PyQt4 import QtCore, QtGui

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
#Mathematicaly, center and undefined are equal, no increment and no decrement,
#but center is intended as program marker for an intended objective, while
#undefined is intended for an error state. Neither situation demands change in
#pixel coordinates. The number values might be increased if this program is ever
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

class CircleCounter:
    def __init__(self, minVal = 0, maxVal = 7, start = 0):
        self.value = start
        self.maxVa = maxVal
        self.minVa = minVal
        self.size = maxVal + 1

    def getV(self): return self.value
    
    def setV(self, nV):
        self.value = nV % self.size
        #while self.value > self.maxVa: self.value -= self.size
        #while self.value < self.minVa: self.value += self.size
        
    def incV(self):
        self.value = (self.value + 1) % self.size
        #if self.value > self.maxVa: self.value = self.minVa
        return self.value
    
    def decV(self):
        self.value =  (self.value - 1) % self.size
        #if self.value < self.minVa: self.value = self.maxVa
        return self.value

    
def dataPreProcess(fileName = None):
    """dataPreProcess(tribal_data_text_file_name_str) -> tribal_point_matrix

    This function takes a string that is the name of a file containing tribal
    data. The data is expected to be in format that tribal analiser writes.
    Each line containing:
    
    |<X-coordinate>|<Y-coordinate>|<direction number>|<direction str>|<point\
    count>|
    
    The matrix is returned as list of lists. each member list is of the form:

    [<X-coordinate str>, <Y-coordinate str>, <direction number str>,\
    <direction str>, <point cunt str>]
    """
    #if fileName == None: fileName = "PaintAnalysisLog_complex_2_red_edited.txt"
    if fileName == None:
        fileName = "PaintAnalysisLog_Tribal_Complex.txt"
    dataFileHandle = open(fileName, 'rt')
    #A more robust vertion would handle IO error here
    tribalPointList = dataFileHandle.readlines()#Return list of all lines
    dataFileHandle.close()#close file, it is no longer needed
    tribalPointMatrix = []#prepare to fill matrix
    for p in tribalPointList: # for all lines
        tribalPointMatrix.append(p.split('|')[ 1 : -1])
        #remove empty first and last fields
    tribalPointMatrix = tribalPointMatrix[ 0 : -1]#Remove empty last line
    return tribalPointMatrix

def changeReport(pointMatrix):
    """STRAIT____________000"""
    pointMatrix[0].append("BEGIN_____________000")# nothing to comapare yet
    pointMatrix[0].append("000")# nothing to comapare yet
    localIt = range(1, len(pointMatrix), 1)#the first item was aready covered

    #angle strings.
    strait__000_str = "STRAIT____________000"
    clock___045_str = "CLOCKWISE_________045"
    clock___090_str = "CLOCKWISE_________090"
    clock___135_str = "CLOCKWISE_________130"
    strait__180_str = "STRAIT____________180"
    counter_135_str = "COUNTER_CLOCKWISE_130"
    counter_090_str = "COUNTER_CLOCKWISE_090"
    counter_045_str = "COUNTER_CLOCKWISE_045"
    
    # general counters record how many times the angle between 2 pixels has
    #been in each direction.
    strait__000_General_Count = 0
    clock___045_General_Count = 0
    clock___090_General_Count = 0
    clock___135_General_Count = 0
    strait__180_General_Count = 0
    counter_135_General_Count = 0
    counter_090_General_Count = 0
    counter_045_General_Count = 0
    
    #temporary counters record how many times a particular angle was repeated
    #without change and reset then direction changes. They can be seen as
    #r components in vectors
    strait__000_Count = 0
    clock___045_Count = 0
    clock___090_Count = 0
    clock___135_Count = 0
    strait__180_Count = 0
    counter_135_Count = 0
    counter_090_Count = 0
    counter_045_Count = 0

    #8-direction circular counters
    curCount = CircleCounter(0, 7, 0)
    preCount = CircleCounter(0, 7, 0)
    
    for i in localIt: # for all points but the first one
        curD = int(pointMatrix[i    ][2], 10)#current  line direction value
        preD = int(pointMatrix[i - 1][2], 10)#previous line direction value
        if curD == preD: #if we are in a strait line
            strait__000_General_Count += 1
            strait__000_Count += 1
            clock___045_Count = 0
            clock___090_Count = 0
            clock___135_Count = 0
            strait__180_Count = 0
            counter_135_Count = 0
            counter_090_Count = 0
            counter_045_Count = 0
            pointMatrix[i].append(strait__000_str)
            pointMatrix[i].append(str(strait__000_Count).zfill(2))
            pointMatrix[i].append(str(strait__000_General_Count).zfill(5))
        elif curD == ((preD + 1) % 8): # clock wise    045 degrees
            clock___045_General_Count += 1
            strait__000_Count = 0
            clock___045_Count += 1
            clock___090_Count = 0
            clock___135_Count = 0
            strait__180_Count = 0
            counter_135_Count = 0
            counter_090_Count = 0
            counter_045_Count = 0
            pointMatrix[i].append(clock___045_str)
            pointMatrix[i].append(str(clock___045_Count).zfill(2))
            pointMatrix[i].append(str(clock___045_General_Count).zfill(5))
        elif curD == ((preD + 2) % 8): # clock wise    090 degrees 
            clock___090_General_Count += 1
            strait__000_Count = 0
            clock___045_Count = 0
            clock___090_Count += 1
            clock___135_Count = 0
            strait__180_Count = 0
            counter_135_Count = 0
            counter_090_Count = 0
            counter_045_Count = 0
            pointMatrix[i].append(clock___090_str)
            pointMatrix[i].append(str(clock___090_Count).zfill(2))
            pointMatrix[i].append(str(clock___090_General_Count).zfill(5))
        elif curD == ((preD + 3) % 8): # clock wise    135 degrees
            clock___135_General_Count += 1
            strait__000_Count = 0
            clock___045_Count = 0
            clock___090_Count = 0
            clock___135_Count += 1
            strait__180_Count = 0
            counter_135_Count = 0
            counter_090_Count = 0
            counter_045_Count = 0
            pointMatrix[i].append(clock___135_str)
            pointMatrix[i].append(str(clock___135_Count).zfill(2))
            pointMatrix[i].append(str(clock___135_General_Count).zfill(5))
        elif curD == ((preD + 4) % 8): # undefined     180 degrees
            strait__180_General_Count += 1
            strait__000_Count = 0
            clock___045_Count = 0
            clock___090_Count = 0
            clock___135_Count = 0
            strait__180_Count += 1
            counter_135_Count = 0
            counter_090_Count = 0
            counter_045_Count = 0
            pointMatrix[i].append(strait__180_str)
            pointMatrix[i].append(str(strait__180_Count).zfill(2))
            pointMatrix[i].append(str(strait__180_General_Count).zfill(5))
        elif curD == ((preD + 5) % 8): # counter clock 135 degrees
            counter_135_General_Count += 1
            strait__000_Count = 0
            clock___045_Count = 0
            clock___090_Count = 0
            clock___135_Count = 0
            strait__180_Count = 0
            counter_135_Count += 1
            counter_090_Count = 0
            counter_045_Count = 0
            pointMatrix[i].append(counter_135_str)
            pointMatrix[i].append(str(counter_135_Count).zfill(2))
            pointMatrix[i].append(str(counter_135_General_Count).zfill(5))
        elif curD == ((preD + 6) % 8): # counter clock 090 degrees
            counter_090_General_Count += 1
            strait__000_Count = 0
            clock___045_Count = 0
            clock___090_Count = 0
            clock___135_Count = 0
            strait__180_Count = 0
            counter_135_Count = 0
            counter_090_Count += 1
            counter_045_Count = 0
            pointMatrix[i].append(counter_090_str)
            pointMatrix[i].append(str(counter_090_Count).zfill(2))
            pointMatrix[i].append(str(counter_090_General_Count).zfill(5))
        elif curD == ((preD + 7) % 8): # counter clock 045 degrees
            counter_045_General_Count += 1
            strait__000_Count = 0
            clock___045_Count = 0
            clock___090_Count = 0
            clock___135_Count = 0
            strait__180_Count = 0
            counter_135_Count = 0
            counter_090_Count = 0
            counter_045_Count += 1
            pointMatrix[i].append(counter_045_str)
            pointMatrix[i].append(str(counter_045_Count).zfill(2))
            pointMatrix[i].append(str(counter_045_General_Count).zfill(5))

    print(" strait__000_General_Count =",strait__000_General_Count, "\n",\
          "clock___090_General_Count =",clock___090_General_Count, "\n",\
          "clock___135_General_Count =",clock___135_General_Count, "\n",\
          "clock___135_General_Count =",clock___135_General_Count, "\n",\
          "strait__180_General_Count =",strait__180_General_Count, "\n",\
          "counter_135_General_Count =",counter_135_General_Count, "\n",\
          "counter_090_General_Count =",counter_090_General_Count, "\n",\
          "counter_045_General_Count =",counter_045_General_Count, "\n")
    return pointMatrix


def main():
    pMatrix = dataPreProcess()
    pMatrix = changeReport(pMatrix)
    fileName = "PaintAnalysisLog_Tribal_Vector.txt"
    dataFileHandle = open(fileName, 'wt')
    #A more robust vertion would handle IO error here
    for p in pMatrix:
        print("|".join(p), file=dataFileHandle)
    sys.exit()

if __name__ == '__main__': main()
