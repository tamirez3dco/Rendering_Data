#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino
import itertools

__commandname__ = "text1"
def create_vase(rad, heights):
    p1=[]
    p2=[] 
    
    for r,h in zip(rad, heights):
        p1.append((r,0,h))
        p2.append((r-0.2,0,h))
    
    p2[0] = (p2[0][0], 0, p2[0][2]+0.2)
   
    crv1 = rs.AddInterpCurve(p1)
    crv2 = rs.AddInterpCurve(p2)
    mp = (p1[3][0]-0.1, 0, p1[3][2]+0.05)
    p2.reverse()
    axis = rs.AddLine((0,0,0),(0,0,10))
    
    v1 = rs.AddRevSrf(crv1, axis)
   
    rs.FlipSurface(v1, flip=True)
    rs.DeleteObject(axis)
    return (v1, crv1)
    
def apply_crv(srf, boundary, curves):
    curves.append(boundary)
    curves.append(srf)
    rs.UnselectAllObjects()
    rs.SelectObjects(curves)
    cmd = "-_ApplyCrv"
    rs.Command(cmd)
    new_curves = rs.LastCreatedObjects()
    rs.UnselectAllObjects()
    rs.DeleteObject(new_curves[len(new_curves)-1])
    return new_curves
    
def create_text_curves(text):
    cmd = "-TextObject \"%s\" 0" % (text)
    rs.Command(cmd)
    return rs.LastCreatedObjects()

def RunCommand( is_interactive ):
    rs.UnselectAllObjects()
    (vase, crv) = create_vase([3,4,3,5],[0, 3, 6, 10])
    rs.UnselectAllObjects()
    c = create_text_curves("na")
    #rs.DeleteObjects(c)
    #c = create_text_curves("gy")
    #rs.DeleteObjects(c)
    #c = create_text_curves("nmn")
    
    size = Rhino.Geometry.Surface.GetSurfaceSize(rs.coercesurface(vase))
    boundary = rs.AddRectangle(rs.WorldXYPlane(), size[1], size[2])
    apply_crv(vase, boundary, c)
    #rs.DeleteObjects(c)
    
if( __name__=="__main__" ):
    RunCommand(True)