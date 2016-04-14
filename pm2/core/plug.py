# coding: utf-8
import maya.OpenMaya as om
import maya.cmds as mc

class Plug:

    @property
    def name(self): return self.mplug.name()

    def __init__(self, mplug, node):
        self.mplug = mplug
        self.node = node

    ## value ##

    def getValue(self):
        return mc.getAttr(self.name)

    def findValue(self):
        if mc.hasAttr(self.name):
            return self.getValue()
        return None

    def setValue(self, value):
        mc.setAttr(self.name, value)
