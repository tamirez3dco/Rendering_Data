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
    go = Rhino.Input.Custom.GetOption()
    a1_o = Rhino.Input.Custom.OptionDouble(0.3)
    go.AddOptionDouble("a1", a1_o)
    go.AcceptNothing(True)
    while True:
        if go.Get()!=Rhino.Input.GetResult.Option:
            break
            
    a1 = a1_o.CurrentValue
    create_text_curves("na",2,3,3)
    
if( __name__=="__main__" ):
    RunCommand(True)