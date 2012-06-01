import math
import random
import collections
import rhinoscriptsyntax as rs
import Rhino
import itertools

__commandname__ = "ahilim"
def create_vase(rad, heights):
    p1=[]
    for r,h in zip(rad, heights):
        p1.append((r,0,h))
    
    crv1 = rs.AddInterpCurve(p1)
    axis = rs.AddLine((0,0,0),(0,0,10))
    
    v1 = rs.AddRevSrf(crv1, axis)
    #rs.FlipSurface(v1, flip=True)
    rs.DeleteObjects([crv1,axis])
    return (v1, crv1)

def make_hole(srf, uv, radius):
    fr = rs.SurfaceFrame(srf, uv)
    c1 = rs.AddCircle(fr, radius)
    n = rs.SurfaceNormal(srf,uv)
    n = (-n[0],-n[1],-n[2])
    s = rs.ExtrudeCurveStraight(c1, rs.CircleCenterPoint(c1), n)
    ss = rs.SplitBrep(srf, s, True)
    rs.DeleteObjects([c1, s, ss[1]])
    return ss[0]
    
def RandomPointsOnSurface(srf, n):
    u = rs.SurfaceDomain(srf,0)
    v = rs.SurfaceDomain(srf,1)
    points = [(random.uniform(u[0],u[1]), random.uniform(v[0],v[1]))for i in range(n)]
    return points
    
def RunCommand( is_interactive ):
    rs.EnableRedraw(False)
    n_holes = 30
    hole_radius = 5
    (vase, crv) = create_vase([20,30,30,20],[0,20,40,60])
    uv = RandomPointsOnSurface(vase, n_holes)
    for p in uv:
        vase = make_hole(vase, p, hole_radius)
    
    #rs.EnableRedraw(True)
    rs.Command("OffsetSrf SelID %s Enter Enter" % vase.ToString())
    vase = rs.LastCreatedObjects()
    rs.MoveObject(vase, (0,0,27))
    #ars.DeleteObject(vase)
    rs.EnableRedraw(True)
    #vv = rs.OffsetSurface(v, 0.1, 0.0)
    #print vv
    
if( __name__=="__main__" ):
    RunCommand(True)