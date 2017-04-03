from __main__ import *
import numpy as np
import math

###Variables to be gotten from main Chtuhlu script
#fileName = 'C:/Users/Robert/Google Drive/3d file shed/8star.ngc'
#comp = 'w' #m=mac or w=win
#scl = 635 #this is set to the amount of steps per inch on motor 635
#ox, oy, oz = 0,0,0 #starting locations
#skip = "no" #Skips the first move so that it just jumps right into path!ONLY LINEAR

def main(fileName,comp,scl,ox,oy,oz,skip,passMessage,where,rpms):
    if comp == 'm':
        openFile = open('/Users/bobmain/Desktop/Google Drive/Cthulhu/bcode.txt', 'w')
    if comp == 'w':
        openFile = open('C:/Users/Robert/Google Drive/Cthulhu/bcode.txt', 'w')

    openFile.write('T'+rpms)
    gcode = open(fileName)
    overArc = 1.1
    gcodeLine = gcode.readlines()
    print  "start at: ", ox, oy, oz, "Lines in file:", len(gcodeLine), "scl:", scl
    bLine,droppedLine,noMoveCut,dpcnt,cnt,zMove,oypix,oxpix,nx,ny,nz="",{},skip,0,0,0,0,0,ox,oy,oz

    strX, strY, strZ = 'empty','empty','empty'
    last = ''

    def lineToBcode(x,y,z,n,c): #want to add z later
        bLine, plotCount,pxSkipCnt,pxNoMove,pxDoubleMove,over2skip="",0,0,0,0,0#!!!not global...

###plot XYZABC does not imclude XYZ arch.
###individual z steps don't take XY weight into account, just if z moves it always go first.
        oldx,oldy,oldz,dbx,dby,dbz = round(x[0]),round(y[0]),round(z[0]),round(x[0]),round(y[0]),round(z[0])
        if c == "purple" and where != "toArd":
            bLine += "p"
        if c == "bl" and where != "toArd":
            bLine += "l"
        for l in range(min(len(x),len(y),len(z))):
            xpx,ypx,zpx = round(x[l]),round(y[l]),round(z[l])
            if abs(zpx-oldz) == 1: #Z linear move. Steps not ordered by weight.
		bLine += "Z" if zpx-oldz > 0 else "C"
            if abs(xpx-oldx) == 0 and abs(ypx-oldy) == 0:# and abs(zpx-oldz) == 0: #No Move Check
                pxNoMove += 1
            if abs(xpx-oldx) == 1 and abs(ypx-oldy) == 1: #Double Move Check
                pxDoubleMove += 1
                if abs(x[l]-dbx) > abs(y[l]-dby):
                    bLine += "X" if xpx-oldx > 0 else "A"
                    bLine += "Y" if ypx-oldy > 0 else "B"
                elif abs(x[l]-dbx) < abs(y[l]-dby):
                    bLine += "Y" if ypx-oldy > 0 else "B"
                    bLine += "X" if xpx-oldx > 0 else "A"
                else:
                    bLine += "X" if xpx-oldx > 0 else "A"
                    bLine += "Y" if ypx-oldy > 0 else "B"
                plotCount += 1
            if abs(xpx - oldx) > 1 or abs(ypx-oldy) > 1:#skiped pix check
                pxSkipCnt += 1
                #print "xpx, oldx, ypx,oldy",xpx, oldx, ypx,oldy
                bLine += "X"*int(abs(xpx-oldx)) if xpx-oldx > 0 else "A"*int(abs(xpx-oldx))
                bLine += "Y"*int(abs(ypx-oldy)) if ypx-oldy > 0 else "B"*int(abs(ypx-oldy))
            if abs(xpx - oldx) > 1 and abs(ypx-oldy) > 1:#skiped pix check
                pxSkipCnt += 1
                print "BOTH SINGLE SKIP ERROR"
                print abs(xpx - oldx), abs(ypx-oldy)
                print "xpx, oldx, ypx,oldy",xpx, oldx, ypx,oldy
            if abs(xpx - oldx) > 2 or abs(ypx-oldy) > 2:#double step ERROR!!!
                over2skip += 1
                print "DOUBLE SKIP ERROR"
                print "xpx, oldx, ypx,oldy",xpx, oldx, ypx,oldy
                blankenter = raw_input("anykey to continue MAY MESS THINGS UP!!!!: ")
            if abs(xpx-oldx) == 1 and abs(ypx-oldy) == 0:
                bLine += "X" if xpx-oldx > 0 else "A"
            if abs(xpx-oldx) == 0 and abs(ypx-oldy) == 1:
                bLine += "Y" if ypx-oldy > 0 else "B"
            oldx, oldy, oldz, dbx, dby, dbz = xpx, ypx, zpx, x[l], y[l], z[l]
            plotCount += 1
        return bLine;

    for i in range(len(gcodeLine)):
        #print gcodeLine[i]
        if gcodeLine[i][0] == "G" or gcodeLine[i][0] == " ":
            gWords = gcodeLine[i].split()
            if gcodeLine[i][0] == "G":
                last = gWords[0]
            for i in range(len(gWords)):
                if gWords[i][0] == "X":
                    nx = float(gWords[i].split("X")[1])
                    ox = nx if strX == 'empty' else ox
                    strX = 'set'
                if gWords[i][0] == "Y":
                    ny = float(gWords[i].split("Y")[1])
                    oy = ny if strY == 'empty' else oy
                    strY = 'set'
                if gWords[i][0] == "I":
                    ix = float(gWords[i].split("I")[1])
                    archType = "rel"
                if gWords[i][0] == "J":
                    jy = float(gWords[i].split("J")[1])
                    archType = "rel"
                if gWords[i][0] == "Z":
                    nz = float(gWords[i].split("Z")[1])
                    oz = nz if strZ == 'empty' else oz
                    strZ = 'set'
                if gWords[i][0] == "R":
                    rc = float(gWords[i].split("R")[1])
                    archType = "rad"
                if gWords[i][0] == "F":
                    feedRate = (gWords[i].split("F")[1])

            #my makeshift speed control
            if gWords[0] == "GRPM":
                xysecin = float(gWords[1])
                openFile.write('r' + str(xysecin) + '\n')
            elif gWords[0] == "GZRPM":
                zsecin = float(gWords[1])
                openFile.write('m' + str(zsecin) + '\n')

            elif gWords[0] == "G01" or gWords[0] == "G00" or last == "G01" or last == "G00" or gWords[0] == "G1" or gWords[0] == "G0" or last == "G1" or last == "G0" :
                color = "purple" if last == "G00" or last == "G0" else "bl" #this is NO CUT XY MOVE
                a,b,x,y = int(round(ox*scl)),int(round(oy*scl)),int(round(nx*scl)),int(round(ny*scl))
###create new linear XYZ moves here
                c,z = int(round(oz*scl)),int(round(nz*scl))
                if ox != nx or oy != ny or oz != nz: #"X,Y: No Change"
                    dx,dy,dz = float(a-x),float(b-y), float(c-z)#...
                    nepox,nepoy,nepoz = (1 if dx <= 0 else -1) , (1 if dy <= 0 else -1), (1 if dz <= 0 else -1)
                    #xarr=np.arange(a,x,abs(dx)/max(abs(dx),abs(dy))*nepox)if a!=x else [a]*max(abs(a-x),abs(b-y))
                    #yarr=np.arange(b,y,abs(dy)/max(abs(dx),abs(dy))*nepoy)if b!=y else [b]*max(abs(a-x),abs(b-y))
                    #zarr=c-z
                    xarr=np.arange(a,x,abs(dx)/max(abs(dx),abs(dy),abs(dz))*nepox)if a!=x else [a]*max(abs(a-x),abs(b-y),abs(c-z))
                    yarr=np.arange(b,y,abs(dy)/max(abs(dx),abs(dy),abs(dz))*nepoy)if b!=y else [b]*max(abs(a-x),abs(b-y),abs(c-z))
                    zarr=np.arange(c,z,abs(dz)/max(abs(dx),abs(dy),abs(dz))*nepoz)if c!=z else [c]*max(abs(a-x),abs(b-y),abs(c-z))

                    xarr, yarr, zarr = np.insert(xarr, len(xarr), x), np.insert(yarr, len(yarr), y), np.insert(zarr, len(zarr), z)
                    cnt += 1
                    bLine = lineToBcode(xarr,yarr,zarr,noMoveCut,color)
                    ox, oy, oz = nx, ny, nz

            elif gWords[0] == "G02" or gWords[0] == "G03" or last == "G02" or last == "G03" or gWords[0] == "G2" or gWords[0] == "G3" or last == "G2" or last == "G3": #CW or CCW

                gDir = -1 if last == "G02" or last == "G2" else 1
                c,z = int(round(oz*scl)),int(round(nz*scl))-int(round(oz*scl))
                if archType == "rad":
                    a,b,x,y,rrc = ox*scl,oy*scl,nx*scl,ny*scl,(rc*scl)
                    bside = math.sqrt((abs(x-a)**2)+(abs(y-b)**2))
                    angToRad = math.degrees(math.acos(((rrc*rrc)+(bside*bside)-(rrc*rrc))/(2*rrc*bside)))
                    cx = (math.sin(math.radians(angToRad-(math.degrees(math.asin((x-a)/bside)))))*rrc)
                    cy = (math.sin(math.radians(90-(angToRad-math.degrees(math.asin((x-a)/bside)))))*rrc)
                    if gDir == 1:
                        cx,cy = a-cx if y > b else cx, b+cy if y > b else cy
                        cx,cy = x+cx if y < b else cx, y+cy if y < b else cy
                    if gDir == -1:
                        cx,cy = x+cx if y > b else cx, y-cy if y > b else cy
                        cx,cy = a-cx if y < b else cx, b-cy if y < b else cy
                else:
                    a,b,x,y,ix,jy = ox*scl,oy*scl,nx*scl,ny*scl,ix*scl,jy*scl

                if ox != nx and oy != ny: #"X,Y: No Change"

                    r = math.sqrt((ix*ix)+(jy*jy)) if archType != "rad" else rrc
                    cx = (a+ix) if archType != "rad" else cx
                    cy = (b+jy) if archType != "rad" else cy

                    sang, nang = np.arctan2(a-cx,cy-b)*180/np.pi, np.arctan2(x-cx,cy-y)*180/np.pi
                    sang = sang+360 if sang < 0 else sang
                    nang = nang+360 if nang < 0 else nang
                    degreeChunk = nang - sang if nang > sang else nang - sang + 360
                    if gDir == -1:
                        degreeChunk = sang - nang if sang > nang else sang - nang + 360
                    ArcRadiantLength = (((math.pi*(r*2))*degreeChunk)/360) *overArc
                    roundArc = int(round(ArcRadiantLength))
                    stepDegree = (degreeChunk/roundArc)
                    stepx, stepy = {},{}

                    stepz = {}                          #CHANGE LATER FOR XYZ
                    stepz[0] = c                        #CHANGE LATER FOR XYZ

                    stepx[0],stepy[0]  = a,b
                    for i in range(abs(roundArc)+1):
                        stepAng = ((gDir*stepDegree)*(i)) + sang
                        stepx[i+1] = ((math.sin(math.radians(stepAng))*(r))/math.sin(math.radians(90))) + cx
                        stepy[i+1] = cy - ((math.sin(math.radians(90-stepAng))*(r))/math.sin(math.radians(90)))
                        stepz[i+1] = c                  #CHANGE LATER FOR XYZ
                        oxpix, oypix = round(stepx[i]), round(stepy[i])
                    stepx[abs(roundArc)+1] = x
                    stepy[abs(roundArc)+1] = y
                    stepz[i+1] = c                      #CHANGE LATER FOR XYZ
                    xarr, yarr = (stepx.values()), (stepy.values())

                    zarr = (stepz.values())             #CHANGE LATER FOR XYZ

                    cnt += 1
                    bLine = lineToBcode(xarr, yarr, zarr, noMoveCut, 'bl')
                    ox, oy, = nx, ny

            elif gWords[0] == "G21" or gWords[0] == "G20" or gWords[0] == "%"or gWords[0] == "G90":
                print "!!!Known Ignored: ", gWords
                dpcnt += 1
            else:
                print "!!!G Error\n!\n!\n!\n", gWords
                blankvar = raw_input("\n\n!!!Error: G command not understood")
            openFile.write(bLine)
            bLine = ""
        else:
            droppedLine[i] = gcodeLine[i]
            dpcnt += 1


    if where == "toArd":
        openFile.write('O')
    else:
        openFile.write('e')
    openFile.close()
    passMessage = "gcode to bcode complete!"
    return fileName,comp,scl,ox,oy,oz,skip,passMessage,rpms
if __name__ == "__main__":
    x = main(fileName,comp,scl,ox,oy,oz,skip,passMessage,rpms)
