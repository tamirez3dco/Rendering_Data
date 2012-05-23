#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino
import itertools

__commandname__ = "text1"

def create_text_curves(text):
    cmd = "Enter -TextObject \"%s\" 0" % (text)
    curves = rs.Command(cmd)
    return curves

def RunCommand( is_interactive ):
    create_text_curves("na")
    
if( __name__=="__main__" ):
    RunCommand(True)