
import math
import rhinoscriptsyntax as rs
import Rhino
import itertools
__commandname__ = "textnew1"

def num_letter_curves(text):
    t = list(text)
    res = []
    for l in t:
        g = Rhino.Geometry.TextEntity()
        g.Text = l
        c = g.Explode()
        res.append(len(c))
        
    return res

def create_text_curves(text):
    text_entity = Rhino.Geometry.TextEntity()
    text_entity.Text = text
    curves = text_entity.Explode()
    return curves

def create_text_surfaces(curves, letters):
    path = rs.AddLine((0,0,0),(0,0,0.1))
    
    c_index = 0
    for letter in letters:
        letter_curves = curves[c_index:c_index+letter]
        letter_surfaces = []
        for crv in letter_curves:
            #c1 = rs.coercecurve(crv)
            #rs.ScaleObject(c1,(0,0,0), (10,10,10))
            s = rs.ExtrudeCurve(crv, path)
            rs.ScaleObject(s,(0,0,0), (10,10,10))
            rs.MoveObject(s, (-27,20,0))
            rs.CapPlanarHoles(s)
            letter_surfaces.append(s)
        c_index += letter
        
        if(len(letter_surfaces)==2):
            rs.BooleanDifference([letter_surfaces[0]],[letter_surfaces[1]])
            
        
def run():
    #text = "abcdefghijklmnopqrstuvwxyz"
    #text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text = "naama"
    curve_nums = num_letter_curves(text)
    curves = create_text_curves(text)
    surfaces = create_text_surfaces(curves, curve_nums)
 
    return True
    
def RunCommand( is_interactive ):
    rs.EnableRedraw(False)
    run()
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
