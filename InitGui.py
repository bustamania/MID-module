# -*- coding: utf-8 -*-
# MID Workbench For FreeCAD
# (c) 2017 Hendrik Mohrmann
#***************************************************************************
#*   (c) Hendrik Mohrmann 2017                                             *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License (GPL)            *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/

__title__="MID Workbench For FreeCAD"
__author__ = "Hendrik Mohrmann"




class MIDWorkbench(Workbench):

    import homeDir
    Icon = homeDir.__dir__ + '/icons/WorkbenchIcon.svg'
    MenuText = 'MID Workbench'
    ToolTip = 'Create electric circuits on a 3D object'



    def Initialize(self):
	import Commands
	list = ["LineSettings", "makeWire"]
	self.appendToolbar("MID Tools", list)
	self.appendMenu("MID Workbench", list)
	self.appendCommandbar("PyModuleCommands",list)
	Log ("Loading MyModule... done\n")

    def Activated(self):
        # do something here if needed...
	Msg ("MIDWorkbench.Activated()\n")

    def Deactivated(self):
        # do something here if needed...
        Msg ("MIDWorkbench.Deactivated()\n")


Gui.addWorkbench(MIDWorkbench())
