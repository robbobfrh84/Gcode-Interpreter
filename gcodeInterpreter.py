from __main__ import *
from Tkinter import *
import tkFileDialog
import serial
import time
from functools import partial        
from PIL import Image, ImageTk

comp = 'm' #'w' Windows or 'm' Mac
workOffLine = 'y'
bcode = ('/Users/bobmain/Desktop/Google Drive/Cthulhu/bcode.txt' if comp == 'm' else
       'C:/Users/Robert/Google Drive/Cthulhu/bcode.txt')
sW, sH, xg, yg = 792, 528, 18, 12
xgs, ygs = sW/xg, sH/yg 
passMessage = ""
scl = 635

if workOffLine == 'n':
    import send_path #hastage out to work offline

class Cthuhlu(Frame): #test taking frame out 
    def __init__(s,p):
        s.xC,s.yC,s.zC,s.pbutt,s.saveGo = sW/2, sH/2, 0,  "no", "nogo"#this var tells the plot location to use the click or the XYZ entrys
        s.oxc,s.oyc,s.ozc,s.newx,s.newy,s.newz,s.oldstartx,s.oldstarty,s.lx,s.ly = s.xC, s.yC, s.zC,0,0,0,s.xC, s.yC,s.xC,s.yC
        
        s.p = p      
        Frame.__init__(s,p)
        s.foundation = Frame(p,padx=5, pady=5, bg='tomato')
        s.foundation.pack()
        s.banner = Frame(s.foundation, bg='tomato')
        s.banner.grid(row=0,column=0,sticky=W)
        s.buildGUI()
        s.drawGrid() 
        s.initUI()
        
    def onOpen(s):
        ftypes = [('All files', '*'),('gcode files', '*.ngc'), ('text files', '*.txt'),('text files', '*.cnc')]
        dlg = tkFileDialog.Open(s, filetypes = ftypes)
        s.fileName = dlg.show()
        s.gGrid(xgs,"intoGrid")
        s.gText.delete(1.0,END)
        fl = open(s.fileName)
        reText = fl.readlines()
        print fl.readlines()
        for i in range(len(reText)):
            s.gText.insert(END,reText[i])
        
    def gGrid(s,scl,where):
        s.drawGrid()
        skip,ox,oy,oz,where = ("no",0,0,0,"intoGrid")
        import gcode_to_bcode
        dataBack = gcode_to_bcode.main(s.fileName,comp,scl,ox,oy,oz,skip,passMessage,where,'50')
        print dataBack
        x,y = s.xC,s.yC
        ox,oy = x,y
        bC = open(bcode)
        st = bC.read(1)
        color = 'blue'
        start = "yes"
        while st != 'e':
            if st == "C":
                s.surf.create_oval(ox-2,oy-2,x+2,y+2, outline="red", fill="black", width=1)
            if st == "Z":
                s.surf.create_oval(ox-2,oy-2,x+2,y+2, outline="red", fill="yellow", width=1)
            color = 'violet' if st == "p" else color
            color = 'blue' if st == "l" else color
            x = x+1 if st == "B" else x
            x = x-1 if st == "Y" else x
            y = y+1 if st == "A" else y  
            y = y-1 if st == "X" else y
            s.surf.create_line(ox,oy,x,y, fill=color)
            if start == "yes":
                s.surf.create_oval(ox-6,oy-6,x+6,y+6, outline="sea green", fill="green", width=2)
            start = "no" 
            ox,oy = x,y
            st = bC.read(1)
        s.surf.create_oval(ox-4,oy-4,x+4,y+4, outline="black", fill="red", width=1)
        s.oxc, s.oyc = ox,oy
        
    def initUI(s):
        menubar = Menu(s.p)
        s.p.config(menu=menubar)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=s.onOpen)
        menubar.add_cascade(label="File", menu=fileMenu)        
        s.txt = Text(s)
        s.txt.pack(fill=BOTH, expand=1)
        
    def OnMouseMotion(s, event):
        if s.fLast.get() == 0:
            s.cordx.set(str(round((float(event.x)/xgs),2)))
            s.cordy.set(str(round((float(event.y)/xgs),2)))
        else:
            s.cordx.set(str(round((float(s.oxc-event.x)/xgs),2)))
            s.cordy.set(str(round((float(s.oyc-event.y)/xgs),2)))      

    def OnMouseDown(s, event):
        s.locEntryx.delete(0, END)
        s.locEntryy.delete(0, END)
        s.locEntryx.insert(0, float(event.x)/xgs)
        s.locEntryy.insert(0, float(event.y)/xgs)
        s.fLast.set(0)
        if s.TBvar.get() == 3:
            s.notes = Label(s.notefound, bg='tomato', text="Gotta click BUILD PATH to draw again, dork...ALSO <From Last> disabled" ,anchor=W)
            s.notes.grid(row=0, column=0,sticky=W+E)
            s.xC, s.yC = int(round(float(s.locEntryx.get())*xgs)), int(round(float(s.locEntryy.get())*xgs))
            s.oxc,s.oyc = event.x-(s.oldstartx-s.oxc) ,event.y-(s.oldstarty-s.oyc)
            s.oldstarty, s.oldstartx = event.y, event.x 
            s.saveUpdate()
        else:
            s.lx,s.ly = event.x, event.y
            s.drawGrid()
            s.saveUpdate()
            s.surf.create_oval(s.lx-4,s.ly-4,s.lx+4,s.ly+4, outline="red2", width=1)
            s.surf.create_oval(s.lx-1,s.ly-1,s.lx+1,s.ly+1, fill="black")
            
            
    def plotloc(s):
        s.drawGrid()
        if s.TBvar.get() != 3:
            if s.fLast.get() == 1:
                x,y = float(s.locEntryx.get())*xgs,float(s.locEntryy.get())*xgs
                s.newx, s.newy = round(s.newx+x), round(s.newy+y)
                s.oxc, s.oyc = s.oxc-round(y), s.oyc-round(x)
            else:    
                s.lx,s.ly  = round(float(s.locEntryx.get())*xgs), round(float(s.locEntryy.get())*xgs) 
                s.newx,s.newy= s.newx+(s.oyc-s.ly),s.newy+(s.oxc-s.lx)
                s.surf.create_line(s.oxc, s.oyc,s.lx,s.ly,fill="black")
                s.oxc, s.oyc = s.lx, s.ly
                
            gtype = "G00" if s.ozc > 0 else "G01"
            s.gText.insert(END, gtype + " X"+str(round((float(s.newx)/xgs),4)) +
                    " Y" + str(round((float(s.newy)/xgs),4)) + " Z"+str(round((float(s.newz)/xgs),4))+"\n")
            s.sendgcode.config(text='Save/Update',bg='red') 
            s.tanyagcode.config(state='disabled', text='Save/Update\nTo Send Live', bg='grey')
            s.saveUpdate()
        else:
            s.notes = Label(s.notefound, bg='tomato', text="!!!<PLOT> disabled when placeing new starting location! Click to change location" ,anchor=W)
            s.notes.grid(row=0, column=0,sticky=W+E)
                
        
    def xabeamStarboard(s):
        s.motor, s.Xd,s.Yd = 'X', 0,-1
        s.orderSend()
    def xabeamPort(s):
        s.motor, s.Xd,s.Yd = 'A', 0,1
        s.orderSend()
    def yforwardBow(s):
        s.motor, s.Xd,s.Yd = 'Y',-1,0
        s.orderSend()
    def yaftStern(s):
        s.motor, s.Xd,s.Yd = 'B', 1,0
        s.orderSend()
    def zup(s):
        s.motor, s.Zd = 'Z', 1
        s.orderSend()
    def zdown(s):
        s.motor, s.Zd = 'C', -1
        s.orderSend()
    def xybs(s):
        s.motor, s.Xd,s.Yd = 'D', -1,-1
        s.orderSend()
    def xybp(s):
        s.motor, s.Xd,s.Yd = 'E', -1,1
        s.orderSend()
    def xysp(s):
        s.motor, s.Xd,s.Yd = 'F', 1,1
        s.orderSend()
    def xyss(s):
        s.motor, s.Xd,s.Yd = 'G', 1,-1
        s.orderSend()
        
    def tanyaBuild(s):
        s.notes = Label(s.notefound, bg='tomato', text="WARNING!!! All Buttons send LIVE moves to Tanya")
        s.notes.grid(row=0, column=0,sticky=W+E)
        
    def textMouseDown(s, event):
        s.sendgcode.config(text='Save/Update',bg='red')
        s.tanyagcode.config(state='disabled', text='Save/Update\nTo Send Live', bg='grey')

    def orderSend(s): #compile with sendToArd  
        if s.TBvar.get() == 1:
            if s.motor == 'Z' or s.motor == 'C':
                rpms = float(s.zrpmEntry.get())
                msteps = float(s.zEntry.get())
                order = 'Qm'+str((rpms))+'d'+ str((msteps)) + s.motor + 'e'
            else:
                rpms = float(s.rpmEntry.get())
                msteps = float(s.xyEntry.get())
                order = 'Qr'+str((rpms))+'d'+ str((msteps)) + s.motor + 'e'
            import send_path
            dataBack = send_path.main(order)#don't know: but python won't send data without geting somethin back
            
        if s.TBvar.get() == 2:
            s.stp = float(s.zEntry.get())*xgs if s.motor == 'Z' or s.motor == 'C' else float(s.xyEntry.get())*xgs
            if s.motor == 'C':
                s.surf.create_oval(s.oxc-2,s.oyc-2,s.oxc+2,s.oyc+2, outline="red", fill="black", width=1)
                s.ozc, s.newz = s.ozc+(s.Zd*s.stp), s.newz+(s.Zd*s.stp)
            if s.motor == 'Z':
                s.surf.create_oval(s.oxc-2,s.oyc-2,s.oxc+2,s.oyc+2, outline="red", fill="yellow", width=1)
                s.ozc, s.newz = s.ozc+(s.Zd*s.stp), s.newz+(s.Zd*s.stp)
            if s.motor != 'C' and s.motor != 'Z':
                s.surf.create_line(s.oxc, s.oyc, s.oxc+(s.Xd*s.stp), s.oyc+(s.Yd*s.stp),fill="black")
                s.oxc, s.oyc = s.oxc+(s.Xd*s.stp), s.oyc+(s.Yd*s.stp)
                s.newx,s.newy =  s.newx-(s.Yd*s.stp),s.newy-(s.Xd*s.stp)
            gtype = "G00" if s.ozc > 0 else "G01"
            s.gText.insert(END, gtype + " X"+str(round((float(s.newx)/xgs),4)) +
                " Y" + str(round((float(s.newy)/xgs),4)) + " Z"+str(round((float(s.newz)/xgs),4))+"\n")
            s.sendgcode.config(text='Save/Update',bg='red') 
            s.tanyagcode.config(state='disabled', text='Save/Update\nTo Send Live', bg='grey')
                    
    def gcodeCall(s):
            where,skip,ox,oy,oz = ("toArd","no",0,0,0)
            import gcode_to_bcode
            rpms = 'r'+str(s.grpmEntry.get())+'\n'+'m'+str(s.gzrpmEntry.get())+'\n'
            dataBack = gcode_to_bcode.main(s.fileName,comp,scl,ox,oy,oz,skip,passMessage,where,rpms)
            print dataBack
            order = 'path'
            import send_path
            dataBack = send_path.main(order)#don't know: but python won't send data without geting somethin back
            s.saveGo = "nogo"
#need to update s.newx/y to ... last x y z...            
    def saveUpdate(s):
            data=s.gText.get(1.0,END)[:-1] 
            fn = s.gFileName.get()
            f = ('/Users/bobmain/Desktop/Google Drive/Cthulhu/'+str(fn)+'.cnc' if comp == 'm' else
                   'C:/Users/Robert/Google Drive/Cthulhu/'+str(fn)+'.cnc')
            s.buildFile = open(f,'w')
            s.buildFile.write(data)
            s.buildFile.close()
            s.fileName = f
            s.gGrid(xgs,"intoGrid")
            s.sendgcode.config(text='Saved as is >',bg='orange')
            s.tanyagcode.config(state='normal', text='Tanya GO!!!\n{Send LIVE path}',bg='limegreen')
                 
    def drawGrid(s):
        s.surf = Canvas(s.foundation, width=sW, height=sH)
        s.surf.grid(row=2,column=0,columnspan=2)
        if comp == 'w':
            pilImage = Image.open("C:/Users/Robert/Google Drive/Cthulhu/Clogo.jpg")
            s.logo = ImageTk.PhotoImage(pilImage)
            waterMark = s.surf.create_image(0,0,image=s.logo, anchor=NW)
        for i in range(int(xg)):
            s.surf.create_line((xgs*(i)),0,(xgs*(i)),sH,fill="goldenrod")
        for i in range(int(yg)):
            s.surf.create_line(0,(ygs*(i)),sW,(ygs*(i)),fill="goldenrod")
        s.surf.bind("<Motion>", s.OnMouseMotion)
        s.surf.bind("<1>", s.OnMouseDown) 
        s.surf.create_oval(s.xC-6,s.yC-6,s.xC+6,s.yC+6, outline="sea green", fill="green", width=2)
        #s.gText.delete(1.0,2.0) #s.gText.delete(4.0,5.0) will delete the fourth line
        #s.gText.insert(1.0,"G00 X0.0 Y0.0 Z0.0\n")
                              
    def buildGUI(s):
    ### bannerControls
        s.bannerControls = Frame(s.foundation,bg='tomato')
        s.bannerControls.grid(row=0, column=0, columnspan=2,sticky=W+E)
        Grid.columnconfigure(s.bannerControls, 10, weight=1)
    ## Notes Control
        s.notefound = Canvas(s.foundation, width=150, height=400, bg='green')
        s.notefound.grid(row=1,column=0,sticky=W)
        s.notes = Label(s.notefound, bg='tomato', anchor=SW, 
            text="*Welcome to Cthuhlu Control! Tell Tanya What to do... Note: Z=0 is viewed as the top of the material to be cut +up -down")
        s.notes.grid(row=0, column=0,sticky=W+E)
    ## Send/build Paths
        s.sendBuildPaths = Frame(s.bannerControls,bg='tomato',padx=2,pady=2)
        s.sendBuildPaths.grid(row=0,column=0,columnspan=3,sticky=W+E)
        Grid.columnconfigure(s.sendBuildPaths, 0, weight=1)
        Grid.columnconfigure(s.sendBuildPaths, 1, weight=1)
        s.TBvar = IntVar()
        s.TBvar.set(2)
        s.tanyaDirect = Radiobutton(s.sendBuildPaths, text='TANYA DIRECT', bg='limegreen', selectcolor='limegreen',
                value=1,variable=s.TBvar, indicatoron=0, command=s.tanyaBuild)
        s.tanyaDirect.grid(row=0,column=0,sticky=W+E)
        s.buildPath = Radiobutton(s.sendBuildPaths, text='Build Path', bg='goldenrod', selectcolor='goldenrod',
                value=2,variable=s.TBvar, indicatoron=0)
        s.buildPath.grid(row=0,column=1,sticky=W+E)
        s.bk1 = Frame(s.bannerControls, width=5, bg='tomato')
        s.bk1.grid(row=1, column=3)
        s.setLocb = Frame(s.bannerControls,bg='tomato',padx=2,pady=2)
        s.setLocb.grid(row=0,column=4,sticky=W+E)
        Grid.columnconfigure(s.setLocb, 0, weight=1)
        s.setLocbutt = Radiobutton(s.setLocb, text='Set Start Loc.', bg='skyblue', selectcolor='sky blue',
                value=3,variable=s.TBvar, indicatoron=0)
        s.setLocbutt.grid(row=0,column=0,sticky=W+E)
    ## XYZ/Plot Labels&Entry
        s.setLoc = Frame(s.bannerControls,bg='light grey',padx=2,pady=2)
        s.setLoc.grid(row=1,column=4,rowspan=2, sticky=N+S)
        s.loctext = Label(s.setLoc,text="Coordinate Entry",bg='grey')
        s.loctext.grid(row=1,column=0,columnspan=5,sticky=W+E)
    # XY butts     
        s.locx = Label(s.setLoc, text="X:", bg='light grey')
        s.locx.grid(column=0, row=2)
        s.locEntryx = Entry(s.setLoc, width=10)
        s.locEntryx.grid(column=1, row=2)
        s.locy = Label(s.setLoc, text="Y:", bg='light grey',height=2)
        s.locy.grid(column=0, row=3)
        s.locEntryy = Entry(s.setLoc, width=10)
        s.locEntryy.grid(column=1, row=3)
    # XYTRacking
        s.cordx,s.cordy = StringVar(),StringVar()
        s.cordx.set("0")
        s.cordy.set("0")
        s.xcordinate = Label(s.setLoc, bg='light grey',textvariable=s.cordx, width=5)
        s.xcordinate.grid(row=2, column=2, sticky=W)
        s.ycordinate = Label(s.setLoc, bg='light grey',textvariable=s.cordy, width=5)
        s.ycordinate.grid(row=3, column=2, sticky=W)
    # plot    
        s.fLast = IntVar()
        s.fromLast = Checkbutton(s.setLoc, bg='light grey', text="From Last",variable=s.fLast)
        s.fromLast.grid(column=0,row=4,columnspan=2)
        s.plotbutt = Button(s.setLoc, text="Plot", bg='red',command=s.plotloc)
        s.plotbutt.grid(column=2,row=4,sticky=E+W)

    ##XYdirectionpad   
        s.directionpad = Frame(s.bannerControls, padx=2, pady=2, bg='light grey',)
        s.directionpad.grid(row=1, column=0)
    #y butts/labels
        s.xleft = Button(s.directionpad,text='<',width=3, height=1, fg='white', bg='red',command=s.yforwardBow)
        s.xleft.grid(row=2, column=1)
        s.xright = Button(s.directionpad,text='>',width=3, height=1, fg='white', bg='red',command=s.yaftStern)
        s.xright.grid(row=2, column=3)
        s.xlabel = Label(s.directionpad,text='X',width=3, height=1, fg='black', bg='light grey')
        s.xlabel.grid(row=0, column=2)
    #xy butts/labels
        s.xybs = Button(s.directionpad,text='\\',width=3, height=1, fg='white', bg='chocolate',command=s.xybs)
        s.xybs.grid(row=1 , column=1)
        s.xybp = Button(s.directionpad,text='/',width=3, height=1, fg='white', bg='chocolate',command=s.xybp)
        s.xybp.grid(row=3 , column=1)
        s.xysp = Button(s.directionpad,text='\\',width=3, height=1, fg='white', bg='chocolate',command=s.xysp)
        s.xysp.grid(row=3 , column=3)
        s.xyss = Button(s.directionpad,text='/',width=3, height=1, fg='white', bg='chocolate',command=s.xyss)
        s.xyss.grid(row=1 , column=3)
    #y butts/labels
        s.yup = Button(s.directionpad,text='^',width=3, height=1, fg='white', bg='sea green',command=s.xabeamStarboard)
        s.yup.grid(row=1, column=2)
        s.ydown = Button(s.directionpad,text='v',width=3, height=1,fg='white', bg='sea green',command=s.xabeamPort)
        s.ydown.grid(row=3, column=2)
        s.ylabel = Label(s.directionpad,text='Y',width=1, height=1,padx=6,fg='black', bg='light grey')
        s.ylabel.grid(row=2, column=0)
    #XYinchesEntry/labels
        s.xyInches = Label(s.directionpad,text='X,Y Move:',width=8, height=1, fg='black', bg='grey', anchor=SE)
        s.xyInches.grid(row=0, column=4)
        s.xyEntry = Entry(s.directionpad,width=7, fg='black', bg='white')
        s.xyEntry.grid(row=1, column=4)
        s.xyEntry.insert(0, "1")
    #XYrpmEntry/labels
        s.enterrpm = Label(s.directionpad,text='  sec/in',width=8,height=1, fg='black', bg='light grey', anchor=SW)
        s.enterrpm.grid(row=2, column=4)
        s.rpmEntry = Entry(s.directionpad, width=7, fg='black', bg='white')
        s.rpmEntry.grid(row=3, column=4)
        s.rpmEntry.insert(0, "1.1")
    ##Zpad                
        s.bk1 = Frame(s.bannerControls, width=5, bg='tomato')
        s.bk1.grid(row=1, column=1)
        s.zpad = Frame(s.bannerControls, padx=2,pady=2,bg='light grey')
        s.zpad.grid(row=1, column=2, sticky="nwse")
        s.enterDistance = Label(s.zpad,text='Z Move',width=12, height=1, fg='black', bg='grey')
        s.enterDistance.grid(row=0, column=0, columnspan=2)    
    #z butts/labels
        s.zup = Button(s.zpad,text='^',width=3, height=1, fg='white', bg='goldenrod',command=s.zup)
        s.zup.grid(row=1, column=0)
        s.zdown = Button(s.zpad,text='v',width=3, height=1, fg='white', bg='goldenrod',command=s.zdown)
        s.zdown.grid(row=3, column=0)
        s.zdown = Label(s.zpad,text='-',width=3, height=1, fg='black', bg='light grey',pady=4)
        s.zdown.grid(row=2, column=0)
    #zMove    
        s.zEntry = Entry(s.zpad,width=7, fg='black', bg='white')
        s.zEntry.grid(row=1, column=1)
        s.zEntry.insert(0, ".125")
    #Zrpm
        s.zenterrpm = Label(s.zpad,text='  sec/in',width=7,height=1, fg='black', bg='light grey', anchor=SW)
        s.zenterrpm.grid(row=2, column=1)
        s.zrpmEntry = Entry(s.zpad, width=7, fg='black', bg='white')
        s.zrpmEntry.grid(row=3, column=1)
        s.zrpmEntry.insert(0, "2.0")

    ##Gcode Pad
        
        s.gcodePad = Frame(s.bannerControls, padx=5,pady=5,bg='light grey')
        s.gcodePad.grid(row=0, column=10,rowspan=2,sticky=NE,padx=2,pady=2)
        s.tanyagcode = Button(s.gcodePad, state='disabled', text='Save/Update\nTo Send Live', bg='grey', command=s.gcodeCall, width=16)
        s.tanyagcode.grid(row=0, column=0, columnspan=2)
        s.bk1 = Frame(s.gcodePad, height=10, bg='light grey')
        s.bk1.grid(row=1, column=0)
        s.sendgcode = Button(s.foundation, text='Save/Update',bg='orange', command=s.saveUpdate, width=16)
        s.sendgcode.grid(row=1, column=1,sticky=NE,padx=2,pady=2)
        
    #gcode rpm   
        s.genterrpm = Label(s.gcodePad,text='X/Y sec/in', fg='black', bg='light grey', anchor=SE)
        s.genterrpm.grid(row=2, column=0)
        s.grpmEntry = Entry(s.gcodePad, width=7, fg='black', bg='white')
        s.grpmEntry.grid(row=2, column=1)
        s.grpmEntry.insert(0, "1.3")
        s.genterZrpm = Label(s.gcodePad,text='Z sec/in', fg='black', bg='light grey', anchor=SE)
        s.genterZrpm.grid(row=3, column=0)
        s.gzrpmEntry = Entry(s.gcodePad, width=7, fg='black', bg='white')
        s.gzrpmEntry.grid(row=3, column=1)
        s.gzrpmEntry.insert(0, "2.5")
        
    ###Gcode Column
        s.bk1 = Frame(s.foundation, width=5, bg='tomato')
        s.bk1.grid(row=0, column=2)
        s.cfound = Canvas(s.foundation, width=250, bg='sky blue')
        s.cfound.grid(row=0,column=3,rowspan=3,sticky=NSEW)
        Grid.columnconfigure(s.cfound, 1, weight=1)

        s.fileLab = Label(s.cfound, text="filename:", bg="sky blue")
        s.fileLab.grid(column=0,row=0,sticky=W,pady=2,padx=2)
        s.gFileName = Entry(s.cfound)
        s.gFileName.grid(column=1, row=0,sticky=EW, pady=5,padx=5)
        s.buildFileName = "untitled"
        s.gFileName.insert(0,s.buildFileName)

        s.scrollb = Scrollbar(s.cfound)
        s.scrollb.grid(column=2,row=1,sticky=NS)
        s.scrollbx = Scrollbar(s.cfound, orient=HORIZONTAL)
        s.scrollbx.grid(column=0,row=2, columnspan=2,sticky=NSEW)
        s.gText = Text(s.cfound, wrap=NONE, bg="wheat1",width=38,height=41,yscrollcommand=s.scrollb.set,xscrollcommand=s.scrollbx.set)
        s.scrollb.config(command=s.gText.yview)
        s.scrollbx.config(command=s.gText.xview)
        s.gText.grid(column=0,row=1,columnspan=2)
        s.gText.bind("<1>", s.textMouseDown)
        s.gText.bind("<Any Key>", s.textMouseDown)
        s.gText.insert(1.0,"G00 X0.0 Y0.0 Z0.0\n")
        

def main():
    root = Tk()
    myapp = Cthuhlu(root)
    root.mainloop()

if __name__ == '__main__':
    main()
