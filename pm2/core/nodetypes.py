# coding: utf-8
import maya.OpenMaya as om
import maya.cmds as mc

from plug import *

class DependNode:
    """ Dependency Node """

    @property
    def fn(self):
        if self._fn is None:
            self._fn = om.MFnDependencyNode(self.mobj)
        return self._fn

    @property
    def name(self): return self.fn.name()

    @property
    def apiType(self): return self.mobj.apiType()

    @property
    def apiTypeStr(self): return self.mobj.apiTypeStr()

    def __init__(self, obj):
        self.mobj = obj
        self._fn = None

    def hasFn(self, type):
        return self.mobj.hasFn(type)

    def hasAttr(self, attrName):
        return self.fn.hasAttribute(attrName)

    def getAttr(self, attrName):
        return mc.getAttr(self.name + "." + attrName)

    def setAttr(self, attrName, value):
        mc.setAttr(self.name + "." + attrName, value)

    def hasPlug(self, plugName):
        return self.hasAttr(plugName)

    def findPlug(self, plugName):
        mplug = self.fn.findPlug(plugName)
        return Plug(mplug, self)

    def findPlugs(self, predicate=None):
        plugs = []
        for i in xrange(self.fn.attributeCount()):
            attrObj = self.fn.attribute(i)
            mplug = om.MPlug(self.mobj, attrObj)
            if predicate is None:
                plugs.append(Plug(mplug, self))
            else:
                if predicate(mplug):
                    plugs.append(Plug(mplug, self))
        return plugs

    def findConnectedPlugs(self, predicate=None):
        mplugs = om.MPlugArray()
        a = self.fn.getConnections(mplugs)
        print a

        plugs = []
        for i in xrange(mplugs.length()):
            mplug = mplugs[i]
            if predicate is None:
                plugs.append(Plug(mplug, self))
            else:
                if predicate(mplug):
                    plugs.append(Plug(mplug, self))
        return plugs

    @staticmethod
    def find(type, predicate=None):
        iter = om.MItDependencyNodes(type)
        return DependNode._collect(iter, type, predicate)

    @staticmethod
    def findSelected(type, predicate=None):
        selections = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selections)
        iter = om.MItSelectionList(selections)

        nodes = []
        fn = om.MFnDependencyNode()
        while not iter.isDone():
            obj = om.MObject()
            iter.getDependNode(obj)
            fn.setObject(obj)
            DependNode._gather(nodes, obj, fn, predicate)
            iter.next()
        return nodes

    @staticmethod
    def _collect(iter, type, predicate):
        nodes = []
        fn = om.MFnDependencyNode()
        while not iter.isDone():
            obj = iter.item()
            fn.setObject(obj)
            DependNode._gather(nodes, obj, fn, predicate)
            iter.next()
        return nodes

    @staticmethod
    def _gather(nodes, obj, fn, predicate):
        if predicate is None:
            node = DependNode(obj)
            nodes.append(node)
        else:
            if predicate(obj, fn):
                node = DependNode(obj)
                nodes.append(node)
