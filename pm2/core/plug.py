# coding: utf-8
import maya.OpenMaya as om
import maya.cmds as mc

from nodetypes import DependNode

class Plug:

    @property
    def name(self): return self.mplug.name()

    @property
    def isArray(self): return self.mplug.isArray()

    def __init__(self, mplug, node):
        self.mplug = mplug
        self.node = node

    @staticmethod
    def fromName(plugName):
        names = plugName.split(".")
        nodeName = ".".join(names[:-1])
        name = names[-1]
        node = DependNode.find(om.MFn.kNamedObject, lambda _, fn: fn.name() == nodeName)[0]
        return node.getPlug(name)

    ## value ##

    def getValue(self):
        return mc.getAttr(self.name)

    def findValue(self):
        if mc.hasAttr(self.name):
            return self.getValue()
        return None

    def setValue(self, value):
        mc.setAttr(self.name, value)

    ## connections ##
    def connect(self, plug):
        if plug is str:
            plug = Plug.fromName(plug)
        if plug.isArray:
            mc.connectAttr(self.name, plug.name, nextAvailable = True)
        else:
            mc.connectAttr(self.name, plug.name)

    def disconnect(self, plug):
        if plug is str:
            plug = Plug.fromName(plug)
        if plug.isArray:
            mc.disconnectAttr(self.name, plug.name, nextAvailable = True)
        else:
            mc.disconnectAttr(self.name, plug.name)
