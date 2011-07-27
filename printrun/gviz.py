import wx,time

class window(wx.Frame):
    def __init__(self,f,size=(600,600),bedsize=(200,200)):
        wx.Frame.__init__(self,None,title="Layer view (Use arrow keys to switch layers)",size=(size[0],size[1]))
        self.p=gviz(self,size=size,bedsize=bedsize)
        s=time.time()
        for i in f:
            self.p.addgcode(i)
        #print time.time()-s
        self.initpos=[0,0]
        self.p.Bind(wx.EVT_KEY_DOWN,self.key)
        self.Bind(wx.EVT_KEY_DOWN,self.key)
        self.p.Bind(wx.EVT_MOUSEWHEEL,self.zoom)
        self.Bind(wx.EVT_MOUSEWHEEL,self.zoom)
        self.p.Bind(wx.EVT_MOUSE_EVENTS,self.mouse)
        self.Bind(wx.EVT_MOUSE_EVENTS,self.mouse)
        
    def mouse(self,event):
        if event.ButtonUp(wx.MOUSE_BTN_LEFT):
            if(self.initpos is not None):
                self.initpos=None
        elif event.Dragging():
            e=event.GetPositionTuple()
            if(self.initpos is None):
                self.initpos=e
                self.basetrans=self.p.translate
            #print self.p.translate,e,self.initpos
            self.p.translate = [ self.basetrans[0]+(e[0]-self.initpos[0]),
                            self.basetrans[1]+(e[1]-self.initpos[1]) ]
            self.p.repaint()
            self.p.Refresh()
        
        else:
            event.Skip()
    
    def key(self, event):
        x=event.GetKeyCode()
        #print x
        if x==wx.WXK_UP:
            self.p.layerup()
        if x==wx.WXK_DOWN:
            self.p.layerdown()
    
        #print p.lines.keys()
    def zoom(self, event):
        z=event.GetWheelRotation()
        if event.ShiftDown():
            if z > 0:   self.p.layerdown()
            elif z < 0: self.p.layerup()
        else:
            if z > 0:   self.p.zoom(event.GetX(),event.GetY(),1.2)
            elif z < 0: self.p.zoom(event.GetX(),event.GetY(),1/1.2)
        
class gviz(wx.Panel):
    def __init__(self,parent,size=(200,200),bedsize=(200,200)):
        wx.Panel.__init__(self,parent,-1,size=(size[0],size[1]))
        self.size=size
        self.bedsize=bedsize
        self.lastpos=[0,0,0,0,0]
        self.hilightpos=self.lastpos[:]
        self.Bind(wx.EVT_PAINT,self.paint)
        self.lines={}
        self.pens={}
        self.layers=[]
        self.layerindex=0
        self.scale=[min(float(size[0])/bedsize[0],float(size[1])/bedsize[1])]*2
        self.translate=[0.0, 0.0]
        self.mainpen=wx.Pen(wx.Colour(0,0,0))
        self.hlpen=wx.Pen(wx.Colour(200,50,50))
        self.fades=[wx.Pen(wx.Colour(150+20*i,150+20*i,150+20*i)) for i in xrange(6)]
        self.showall=0
        self.hilight=[]
        self.dirty=1
        self.blitmap=wx.EmptyBitmap(self.GetClientSize()[0],self.GetClientSize()[1],-1)
        
    def clear(self):
        self.lastpos=[0,0,0,0,0]
        self.lines={}
        self.pens={}
        self.layers=[]
        self.layerindex=0
        self.showall=0
        self.dirty=1
        #self.repaint()        
    def layerup(self):
        if(self.layerindex+1<len(self.layers)):
            self.layerindex+=1
            self.repaint()
            self.Refresh()
    
    def layerdown(self):
        if(self.layerindex>0):
            self.layerindex-=1
            self.repaint()
            self.Refresh()
    
    def setlayer(self,layer):
        try:
            self.layerindex=self.layers.index(layer)
            self.repaint()
            wx.CallAfter(self.Refresh)
            self.showall=0
        except:
            pass
    

    def zoom(self,x,y,factor):
        self.scale = [s * factor for s in self.scale]
        self.translate = [ x - (x-self.translate[0]) * factor,
                            y - (y-self.translate[1]) * factor]
        #self.dirty=1
        self.repaint()
        self.Refresh()
        
    def repaint(self):
        self.blitmap=wx.EmptyBitmap(self.GetClientSize()[0],self.GetClientSize()[1],-1)
        dc=wx.MemoryDC()
        dc.SelectObject(self.blitmap)
        dc.SetBackground(wx.Brush((250,250,200)))
        dc.Clear()
        if not self.showall:
            dc.SetBrush(wx.Brush((43,144,255)))
            dc.DrawRectangle(self.size[0]-15,0,15,self.size[1])
            dc.SetBrush(wx.Brush((0,255,0)))
            if len(self.layers):
                dc.DrawRectangle(self.size[0]-14,(1.0-(1.0*(self.layerindex+1))/len(self.layers))*self.size[1],13,self.size[1]-1)
        def scaler(x):
            return (self.scale[0]*x[0]+self.translate[0],
                    self.scale[1]*x[1]+self.translate[1],
                    self.scale[0]*x[2]+self.translate[0],
                    self.scale[1]*x[3]+self.translate[1],)
        if self.showall:
            l=[]
            for i in self.layers:
                dc.DrawLineList(l,self.fades[0])
                l=map(scaler,self.lines[i])
                dc.DrawLineList(l,self.pens[i])
            return
        if self.layerindex<len(self.layers) and self.layers[self.layerindex] in self.lines.keys():
            for i in range(min(self.layerindex,6))[-6:]:
                #print i, self.layerindex, self.layerindex-i
                l=map(scaler,self.lines[self.layers[self.layerindex-i-1]])
                dc.DrawLineList(l,self.fades[i])
            l=map(scaler,self.lines[self.layers[self.layerindex]])
            dc.DrawLineList(l,self.pens[self.layers[self.layerindex]])
        l=map(scaler,self.hilight)
        dc.DrawLineList(l,self.hlpen)
        dc.SelectObject(wx.NullBitmap)
    
    def paint(self,event):
        dc=wx.PaintDC(self)
        if(self.dirty):
            self.repaint()
        self.dirty=0
        sz=self.GetClientSize()
        dc.DrawBitmap(self.blitmap,0,0)
        del dc
        
    def addgcode(self,gcode="M105",hilight=0):
        gcode=gcode.split("*")[0]
        gcode=gcode.split(";")[0]
        if "g1" in gcode.lower():
            gcode=gcode.lower().split()
            target=self.lastpos[:]
            if hilight:
                target=self.hilightpos[:]
            for i in gcode:
                if i[0]=="x":
                    target[0]=float(i[1:])
                elif i[0]=="y":
                    target[1]=float(i[1:])
                elif i[0]=="z":
                    target[2]=float(i[1:])
                elif i[0]=="e":
                    target[3]=float(i[1:])
                elif i[0]=="f":
                    target[4]=float(i[1:])
            #draw line
            if not hilight:
                if not target[2] in self.lines.keys():
                    self.lines[target[2]]=[]
                    self.pens[target[2]]=[]
                    self.layers+=[target[2]]
                self.lines[target[2]]+=[(self.lastpos[0],self.bedsize[1]-self.lastpos[1],target[0],self.bedsize[1]-target[1])]
                self.pens[target[2]]+=[self.mainpen]
                self.lastpos=target
            else:
                self.hilight+=[(self.hilightpos[0],self.bedsize[1]-self.hilightpos[1],target[0],self.bedsize[1]-target[1])]
                self.hilightpos=target
            self.dirty=1
            
            
if __name__ == '__main__':
    app = wx.App(False)
    #main = window(open("/home/kliment/designs/spinner/gearend_export.gcode"))
    main = window(open("jam.gcode"))
    main.Show()
    app.MainLoop()

