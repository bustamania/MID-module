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

import FreeCAD
import os,sys,string
from SliceVars import *
from pivy import coin
import homeDir

if FreeCAD.GuiUp:
	import FreeCADGui
	from FreeCADGui import PySideUic as uic
	from PySide import QtCore, QtGui

# Default Values
defaultVals = {"thickness":0.1, "distance":0.3, "depth":2.0 }


class SetParameterTaskPanel:
	def __init__(self):
		self.form = uic.loadUi(homeDir.__dir__ + "/UI/SetParameter.ui")

		self.form.doubleSpinBox_1.setValue(readSetting("thickness"))
		self.form.doubleSpinBox_2.setValue(readSetting("distance"))
		self.form.doubleSpinBox_3.setValue(readSetting("depth"))

		self.form.doubleSpinBox_1.valueChanged.connect(self._thickness)
		self.form.doubleSpinBox_2.valueChanged.connect(self._distance)
		self.form.doubleSpinBox_3.valueChanged.connect(self._depth)

	def accept(self):
		#makePrintBedGrp()
		FreeCADGui.Control.closeDialog()

	def reject(self):
		FreeCADGui.Control.closeDialog()

	def getStandardButtons(self):
		return int(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

	def _thickness(self, val):
		writeSetting("thickness", val)

	def _distance(self, val):
		writeSetting("distance", val)

	def _depth(self, val):
		writeSetting("depth", val)

def readSetting(key):
    global defaultVals
    grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/MID/SetParameter")
    val = grp.GetFloat(key, defaultVals[key])
    FreeCAD.Console.PrintMessage("Reading Key: " + key + " Value: " + str(val) + "\n")
    return val

def writeSetting(key, val):
    grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/MID/SetParameter")
    FreeCAD.Console.PrintMessage("Setting " + key + " to " + str(val) + '\n')
    grp.SetFloat(key, val)

