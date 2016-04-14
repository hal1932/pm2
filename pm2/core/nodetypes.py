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

    @staticmethod
    def fromName(nodeName):
        return DependNode.find(om.MFn.kNamedObject, lambda _, fn: fn.name() == nodeName)[0]

    def hasFn(self, type):
        return self.mobj.hasFn(type)

    def delete(self):
        mc.delete(self)
        self.mobj = None

    ## attribute ##

    def hasAttr(self, attrName):
        return self.fn.hasAttribute(attrName)

    def getAttr(self, attrName):
        return mc.getAttr(self.name + "." + attrName)

    def findAttr(self, attrName):
        if self.hasAttr(attrName):
            return self.getAttr(attrName)
        return None

    def setAttr(self, attrName, value):
        mc.setAttr(self.name + "." + attrName, value)

    def addAttr(self, attrType, dataType, longName, shortName):
        if not attrType is None:
            mc.addAttr(self.name, attributeType = attrType, longName = longName, shortName = shortName)
        else:
            mc.addAttr(self.name, dataType = dataType, longName = longName, shortName = shortName)

    def deleteAttr(self, attrName):
        mc.deleteAttr(self.name + "." + attrName)

    ## plugs ##

    def hasPlug(self, plugName):
        return self.hasAttr(plugName)

    def getPlug(self, plugName):
        mplug = self.fn.findPlug(plugName)
        return Plug(mplug, self)

    def findPlug(self, plugName):
        if self.hasPlug(plugName):
            return self.getPlug(plugName)
        return None

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

    def getConnectedPlugs(self, predicate=None):
        mplugs = om.MPlugArray()
        self.fn.getConnections(mplugs)

        plugs = []
        for i in xrange(mplugs.length()):
            mplug = mplugs[i]
            if predicate is None:
                plugs.append(Plug(mplug, self))
            else:
                if predicate(mplug):
                    plugs.append(Plug(mplug, self))
        return plugs

    def findConnectedPlugs(self, predicate=None):
        try:
            return self.getConnectedPlugs(predicate)
        except:
            return []

    ## connected nodes ##

    def findSourceNodes(self, predicate=None):
        return self.findConnectedNodes(True, False, predicate)

    def findDestinationNodes(self, predicate=None):
        return self.findConnectedNodes(False, True, predicate)

    def findConnectedNodes(self, asDestination, asSource, predicate=None):
        plugs = om.MPlugArray()
        self.fn.getConnections(plugs)

        nodes = []
        for i in xrange(plugs.length()):
            plug = plugs[i]
            connectedPlus = om.MPlugArray()
            plug.connectedTo(connectedPlus, asDestination, asSource)

            for j in xrange(connectedPlus.length()):
                connectedPlug = connectedPlus[j]
                if predicate is None:
                    node = DependNode(connectedPlug.node())
                    nodes.append(node)
                else:
                    if predicate(connectedPlug):
                        node = DependNode(connectedPlug.node())
                        nodes.append(node)
        return nodes

    ## find from scene ##

    @staticmethod
    def find(target, predicate=None):
        return DependNode._findImpl(target, predicate, False)

    @staticmethod
    def findFirst(target, predicate=None):
        return DependNode._findImpl(target, predicate, True)
    
    @staticmethod
    def _findImpl(target, predicate, first):
        if isinstance(target, str): # target is name
            return DependNode._findImpl(om.MFn.kNamedObject, lambda _, fn: fn.name() == target, first)
        elif isinstance(target, int): # target is type
            iter = om.MItDependencyNodes(target)
            return DependNode._collect(iter, predicate, first)

    @staticmethod
    def findSelected(target = None, predicate=None):
        return DependNode._findSelectedImpl(target, predicate, False)

    @staticmethod
    def findFirstSelected(target = None, predicate=None):
        return DependNode._findSelectedImpl(target, predicate, True)

    @staticmethod
    def _findSelectedImpl(target, predicate, first):
        if target is None:
            target = om.MFn.kInvalid

        if isinstance(target, str): # target is name
            return DependNode._findSelectedImpl(om.MFn.kNamedObject, lambda _, fn: fn.name() == target, first)
        elif isinstance(target, int): # target is type
            selections = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(selections)
            iter = om.MItSelectionList(selections)

            nodes = []
            fn = om.MFnDependencyNode()
            while not iter.isDone():
                obj = om.MObject()
                iter.getDependNode(obj)
                fn.setObject(obj)
                if DependNode._gather(nodes, obj, fn, predicate) and first:
                    return nodes[0]
                iter.next()
            return nodes

    ## private ##

    @staticmethod
    def _collect(iter, predicate, first):
        nodes = []
        fn = om.MFnDependencyNode()
        while not iter.isDone():
            obj = iter.item()
            fn.setObject(obj)
            if DependNode._gather(nodes, obj, fn, predicate) and first:
                return nodes[0]
            iter.next()
        return nodes

    @staticmethod
    def _gather(nodes, obj, fn, predicate):
        if predicate is None:
            node = DependNode(obj)
            nodes.append(node)
            return True
        else:
            if predicate(obj, fn):
                node = DependNode(obj)
                nodes.append(node)
                return True
        return False

