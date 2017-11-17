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



import FreeCAD, FreeCADGui, Part
from pivy.coin import *
from PySide import QtGui
import numpy as np
import homeDir

class makeWire:

  def __init__(self):
    self.view = FreeCADGui.ActiveDocument.ActiveView
    self.shellComplete = []
    self.nodesM = []
    self.nodesN = []
    #self.thickness = 0.3		# line thickness in mm
    self.extrude = 2
    self.callback = self.view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.addSeg) 


  def GetResources(self):
     return {'Pixmap': homeDir.__dir__ + './FreeCAD/Mod/MID/icons/addSegment.svg',
             'MenuText': 'Append Segment',
             'ToolTip': 'Appends a segment to the Line'}

  def crossproduct(self, first, other):
     return FreeCAD.Vector(first.y*other.z - first.z*other.y, first.z*other.x - first.x*other.z, first.x*other.y - first.y*other.x)

  def reverse(self, first):
     return FreeCAD.Vector(-first.x, -first.y, -first.z)


  def addSeg(self, event_cb):
    event = event_cb.getEvent()
    if (type(event) == SoMouseButtonEvent and event.getState() == SoMouseButtonEvent.DOWN and event.getButton() == SoMouseButtonEvent.BUTTON1):
      pos = event.getPosition()
      pnt = self.view.getPoint(pos[0],pos[1])
      info = self.view.getObjectInfo((pos[0], pos[1]))
      if info != None:
        obj = FreeCAD.ActiveDocument.getObject(info["Object"])
        comp = getattr(obj.Shape, info["Component"])
        print(comp)
        uv = comp.Surface.parameter(FreeCAD.Vector(info["x"],info["y"],info["z"]))
        m = comp.valueAt(uv[0],uv[1])		# vector pointing on surface
        n = comp.normalAt(uv[0],uv[1])		# normal vector
        self.nodesM.append(m)
        self.nodesN.append(n)
        print(self.nodesM)

        if len(self.nodesM) ==1:
          return

        if len(self.nodesM) == 2:
          o = self.nodesM[-1] - self.nodesM[-2]
          pOffset = self.crossproduct(o,n).normalize()*0.5*SetParameterTaskPanel._thickness
          self.nodesN[-1] -= pOffset
          self.nodesN[-2] -= pOffset
          sphere1 = Part.makeSphere(self.thickness*0.5, self.nodesM[-2])

        elif len(self.nodesM) > 2:
          o = self.nodesM[-1] - self.nodesM[-2]
          ptmp = self.crossproduct(o,n)
          pOffset = ptmp.normalize()*0.5*SetParameterTaskPanel._thickness
          self.nodesN[-1] -= pOffset


        # note: use Part.LineSegment from 0.17 on
        segmentM = Part.Line(self.nodesM[-2], self.nodesM[-1])
        faceNleft = segmentM.toShape().extrude(pOffset.normalize()*0.5*SetParameterTaskPanel._thickness)
        faceNright = segmentM.toShape().extrude(pOffset.normalize()*(-0.5)*SetParameterTaskPanel._thickness)

        # create 4 volume shells around segmentM and fuse them
        shellleftUp = faceNleft.extrude(n.normalize()*self.extrude)
        shellleftDown = faceNleft.extrude(self.reverse(n).normalize()*self.extrude)
        shellrightDown = faceNright.extrude(self.reverse(n).normalize()*self.extrude)
        shellrightUp = faceNright.extrude(n.normalize()*self.extrude)
        shell = shellleftUp.fuse(shellleftDown.fuse(shellrightDown.fuse(shellrightUp)))

        # create sphere at the node
        sphere = Part.makeSphere(self.thickness*0.5, self.nodesM[-2])
        if len(self.nodesM) == 2:
          self.shellComplete = shell.fuse(sphere.fuse(sphere1))
        elif len(self.nodesM) > 2:
          #self.Shape.FreeCAD.ActiveDocument.removeObject(self.Shape.Name)
          self.shellComplete = self.shellComplete.fuse(shell.fuse(sphere))

        vol = Part.makeSolid(self.shellComplete)
        wire = vol.section(comp)

        Shape = Part.show(wire)
        
class deleteLine:
  def GetResources(self):
    return {'Pixmap': __dir__ + '/icons/deleteSegment.svg',
            'MenuText': 'Delete Segment',
            'ToolTip': 'Deletes a segment from the Line'}

  def Activated(self):
    self.view = FreeCADGui.ActiveDocument.ActiveView
    self.callback = self.view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.delSeg) 

  def delSeg( self, event_cb):
     fp = FreeCAD.ActiveDocument.Shape
     event = event_cb.getEvent()
     pos = event.getPosition()

     i = 0
     for geom in fp.GeometryDescriptor:
       v = FreeCAD.Vector( geom[1], geom[2], geom[3])
       if ( v - pos ).Length < 0.01:
         del fp.GeometryDescriptor[i]
         i -= 1
         break
       i += 1




