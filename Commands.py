#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2017                                                    *
#*   Hendrik Mohrmann <hendrik.mohrmann@posteo.net>                        *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *	
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************


import FreeCAD, FreeCADGui, inspect, Part
from FreeCAD import Console
from command.PCBmoveParts import moveParts
#from FreeCAD import DraftVecUtils
from pivy.coin import *
from PySide import QtGui
#import numpy as np
import homeDir
from SetParameter import readSetting
import math
import newWire


# helper -------------------------------------------------------------------

def addCommand(name,cmdObject):
	(list,num) = inspect.getsourcelines(cmdObject.Activated)
	pos = 0
	# check for indentation
	while(list[1][pos] == ' ' or list[1][pos] == '\t'):
		pos += 1
	source = ""
	for i in range(len(list)-1):
		source += list[i+1][pos:]
	FreeCADGui.addCommand(name,cmdObject,source)
	

#---------------------------------------------------------------------------
# The command classes
#---------------------------------------------------------------------------




class LineSettings:
	"Parameter Settings"
	def Activated(self):
		import SetParameter
		reload(SetParameter)
		panel = SetParameter.SetParameterTaskPanel()
		FreeCADGui.Control.showDialog(panel)

	def GetResources(self):
		return {'Pixmap': homeDir.__dir__ + '/icons/Settings.svg', 'MenuText': 'Parameter Settings', 'ToolTip': 'Set the parameter for surface circuits'}
	      
FreeCADGui.addCommand('LineSettings',LineSettings())

#----------------------------------------------------------------------------------------

class cmdPartMoveModel:
    def Activated(self):
        panel = moveParts(FreeCADGui.Selection.getSelection()[0].Package)
        FreeCADGui.Control.showDialog(panel)
        
    def GetResources(self):
        return {'MenuText': 'Placement model', 'ToolTip': 'Placement model'}

FreeCADGui.addCommand('cmdPartMoveModel', cmdPartMoveModel())


#----------------------------------------------------------------------------------------


class makeWire:  
  
  def __init__(self ):
    self.view = FreeCADGui.ActiveDocument.ActiveView
    self.callback = self.view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.execute)

  def GetResources(self ):
     return {'Pixmap': homeDir.__dir__ + '/icons/makeWire.svg',
             'MenuText': 'Append Segment',
             'ToolTip': 'Appends a segment to the Line'}

  def Activated(self ):
    self.wire = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Wire")
    #self.wire.Proxy = self
    self.thickness = readSetting("thickness")
    self.distance = readSetting("distance")
    self.extrude = readSetting("depth")
    self.nodesM = []
    self.nodesN = []
    self.error = False
    
  def Deactivated(self ):
    self.view.removeEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.execute) 

  def execute(self, event_cb ):
    self.getPoint(event_cb )
    if len(self.nodesM) >= 2:     
      self.makeSegment()
      self.makeVolume()
      self.showWire()

  def getPoint(self, event_cb ):
    event = event_cb.getEvent()
    if (type(event) == SoMouseButtonEvent and event.getState() == SoMouseButtonEvent.DOWN and event.getButton() == SoMouseButtonEvent.BUTTON1):
      pos = event.getPosition()
      pnt = self.view.getPoint(pos[0],pos[1])
      info = self.view.getObjectInfo((pos[0], pos[1]))

      if info == None:
	return

      elif "Face" in info["Component"]:
        obj = FreeCAD.ActiveDocument.getObject(info["Object"])
        self.face = getattr(obj.Shape, info["Component"])
        uv = self.face.Surface.parameter(FreeCAD.Vector(info["x"],info["y"],info["z"]))

        self.m = self.round(self.face.valueAt(uv[0],uv[1]), 8)
        self.n = self.round(self.face.normalAt(uv[0],uv[1]), 8)
        self.nodesM.append(self.m)
        self.nodesN.append(self.n)
        
      elif "Edge" in info["Component"]:
	print("edge selected")
        obj = FreeCAD.ActiveDocument.getObject(info["Object"])
        self.edge = getattr(obj.Shape, info["Component"])
        self.m = FreeCAD.Vector(info["x"],info["y"],info["z"])
        self.n = self.getTangent(self.edge, pos)
        self.nodesM.append(self.m)
        self.nodesN.append(self.n)
        

  def makeSegment(self ):
        if len(self.nodesM) == 2:
          self.o = self.nodesM[-1] - self.nodesM[-2]
          self.pOffset = self.crossproduct(self.o,self.n).normalize()*0.5*self.thickness

        elif len(self.nodesM) > 2:
          self.o = self.nodesM[-1] - self.nodesM[-2]
          ptmp = self.crossproduct(self.o,self.n)
          self.pOffset = ptmp.normalize()*0.5*self.thickness

        # note: use Part.LineSegment from 0.17 on
        self.segmentM = Part.Line(self.nodesM[-2], self.nodesM[-1])

  def makeVolume(self ):
        faceNleft = self.segmentM.toShape().extrude(self.pOffset.normalize()*0.5*self.thickness)
        faceNright = self.segmentM.toShape().extrude(self.pOffset.normalize()*(-0.5)*self.thickness)

        # create 4 volume shells around segmentM and fuse them
        shellleftUp = faceNleft.extrude(self.n.normalize()*self.extrude)
        shellleftDown = faceNleft.extrude(self.n.normalize()*self.extrude*(-1))
        shellrightDown = faceNright.extrude(self.n.normalize()*self.extrude*(-1))
        shellrightUp = faceNright.extrude(self.n.normalize()*self.extrude)
        shell = shellleftUp.fuse(shellleftDown.fuse(shellrightDown.fuse(shellrightUp)))

        # create sphere at the node
        sphere = Part.makeSphere(self.thickness*0.5, self.nodesM[-1])
        
        try:
          if len(self.nodesM) == 2:
	    sphere1 = Part.makeSphere(self.thickness*0.5, self.nodesM[0])
	    #shell = shell.fuse(sphere1)
	    self.shellComplete = shell#.fuse(sphere)
          elif len(self.nodesM) > 2:
	    self.shellComplete = self.shellComplete.fuse(shell)
           #self.shellComplete = self.shellComplete.fuse(sphere)
            
          self.vol = Part.makeSolid(self.shellComplete)
          self.error = False
	except:
          if self.error == False:
            self.nodesM = self.nodesM[:-1]
            self.nodesN = self.nodesN[:-1]
          self.error = True
          print("Fusion error!")

  def showWire(self ):
      if self.error == False:
        shape = self.vol.section(self.face)
        self.wire.Shape = shape
        self.wire.ViewObject.Proxy = 0
        FreeCAD.ActiveDocument.recompute() 

  def deleteWire(self ):
      try:
        FreeCAD.ActiveDocument.removeObject("Shape")
      except:
        print("No Shape to be deleted!")

  def crossproduct(self, first, other ):
      return FreeCAD.Vector(first.y*other.z - first.z*other.y, first.z*other.x - first.x*other.z, first.x*other.y - first.y*other.x)
    
  def sub(self, first, other): 
      "sub(Vector,Vector) - subtracts second vector from first one"
      if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
 	return FreeCAD.Vector(first.x-other.x, first.y-other.y, first.z-other.z)

  def length(self, vector):
      return math.sqrt(vector.x*vector.x + vector.y*vector.y + vector.z*vector.z)

  def reverse(self, vector ):
      return FreeCAD.Vector(-vector.x, -vector.y, -vector.z)

  def round(self, vector, n):
      return FreeCAD.Vector(round(vector.x, n), round(vector.y, n), round(vector.z, n))

  def getTangent(self, edge, pos):
    "Returns a tangent vector from an edge in FreeCAD"
    if isinstance(edge.Curve,Part.Line):
        vec = self.sub(edge.Vertexes[-1].Point, edge.Vertexes[0].Point)
    elif isinstance(edge.Curve,Part.Circle):
        v1 = self.sub(edge.Vertexes[-1], edge.Curve.Center)
        v2 = edge.Curve.Axis
        vec = self.crossproduct(v1,v2)
    else:
        print "not supported"
        vec = None
    return vec

FreeCADGui.addCommand('makeWire',makeWire())
