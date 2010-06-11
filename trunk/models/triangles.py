# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
import random
_r = random.randint

class Model(object):
    """A scene class that uses a list of mutating translucid triangles
    to approach a target picture"""
    def __init__(self, target):
        """Init stuff, target is the target image"""
        self.NUM_T=1000
        self.NUM_M=100
        self.T_W=100
        self.w=target.width()
        self.h=target.height()
        self.polys = [Triangle(self.T_W,self.w,self.h) for t in range(self.NUM_T)]
        self.curdiff=1000000000000
    def step(self):
        """Make a step"""
        self.mutated = [p.copy() for p in self.polys]
        for x in range(self.NUM_M):
            i=_r(0,len(self.mutated)-1)
            self.mutated[i]=self.mutated[i].mutate()
        return self.mutated

    def decide(self, diff):
        """Called after step(), diff is what the metric says
        about the current mutated state"""
        if diff <= self.curdiff: # better
            print "** Better: %s - %s"%(diff, self.curdiff-diff)
            self.polys = self.mutated
            self.curdiff=diff
        else: # worse
            print "Worse: %s - %s"%(diff, self.curdiff-diff),
        


class Point(object):
    """A point"""
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y

class Triangle(object):
    """A translucid triangle"""
    def __init__(self, T_W=100, w=100, h=100):
        self.T_w=T_W
        self.w=w
        self.h=h
        x1 = _r(-T_W/2,w+T_W/2)
        y1 = _r(-T_W/2,h+T_W/2)
        self.points=[Point(x1,y1),
            Point(x1+_r(0,T_W),y1+_r(0,T_W)),
            Point(x1+_r(0,T_W),y1+_r(0,T_W)),
        ]
        self.color=[127,127]
        #self.color=[0,0]
        self.rotation=0
        self.scale=1.0

    def copy(self):
        c=Triangle()
        c.scale=self.scale
        c.color=self.color[:]
        c.rotation=self.rotation
        c.points=[Point(p.x,p.y) for p in self.points]
        return c

    def mutate(self):
        # Choose what way to mutate
        mutated=self.copy()
        mutation = _r(1,50)
        if  mutation<10:
            # Change size
            mutated.scale +=_r(-3,3)/100.
        elif 20 > mutation:
            # rotate a bit
            mutated.rotation+=_r(-5,5)
        elif 30 > mutation:
            # lighter/darker
            mutated.color[0] = min(255,max(0, self.color[0] + _r(-10,10)))
        elif 40 > mutation:
            # more transparent
            mutated.color[1] = min(255,max(0, self.color[1] + _r(-10,10)))
        else:
            # move a bit
            for i,p in enumerate(self.points):
                mutated.points[i]=Point(p.x+_r(-10,10),
                    p.y+_r(-10,10))
        return mutated

    def shape(self):
        poly = QtGui.QPolygonF(0)
        for p in self.points:
            poly.insert(0,QtCore.QPointF(p.x,p.y))
        shape = QtGui.QGraphicsPolygonItem(poly)
        shape.setBrush(QtGui.QColor(self.color[0],self.color[0],self.color[0],self.color[1]))
        shape.setPen(QtGui.QColor(self.color[0],self.color[0],self.color[0],self.color[1]))
        shape.setScale(self.scale)
        shape.setTransformOriginPoint(QtCore.QPointF(
            sum([po.x for po in self.points])/3.,
            sum([po.y for po in self.points])/3.,
        ))
        shape.setRotation(self.rotation)
        return shape
