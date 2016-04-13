# coding: utf-8
import maya.OpenMaya as om
import maya.cmds as mc

class Plug:

    @property
    def name(self): return self.mplug.name()

    def __init__(self, mplug, node):
        self.mplug = mplug
        self.node = node

    def getValue(self):
        return mc.getAttr(self.name)

    def setValue(self, value):
        mc.setAttr(self.name, value)
