#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino
import itertools

__commandname__ = "text1"

def point2str(p):
    return "%s,%s,%s" % (p[0],p[1],p[2])

def create_text_curves(text, height, x, y):
    point = (x,y,0)
    cmd = "-_TextObject _Height=%s _Output=_Curves _FontName=Corbel \"%s\" %s" % (height, text, point2str(point))
    curves = rs.Command(cmd)
    return curves

def RunCommand( is_interactive ):
    create_text_curves("na",2,3,3)
    
if( __name__=="__main__" ):
    RunCommand(True)