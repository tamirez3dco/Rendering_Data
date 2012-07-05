
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
    res = []
    
    for letter in letters:
        letter_curves = curves[c_index:c_index+letter]
        letter_surfaces = []
        for crv in letter_curves:
            s = rs.ExtrudeCurve(crv, path)
            rs.ScaleObject(s,(0,0,0), (10,10,10))
            rs.MoveObject(s, (-27,20,0))
            rs.CapPlanarHoles(s)
            letter_surfaces.append(s)
        c_index += letter
        
        s = letter_surfaces[0]
        if(len(letter_surfaces)>1):
            srf = rs.AddPlanarSrf([letter_curves[0]])
            ins = rs.CurveSurfaceIntersection(letter_curves[1], srf)
            rs.DeleteObject(srf)
            if len(ins) != 0:
                s = rs.BooleanDifference([letter_surfaces[0]],letter_surfaces[1:len(letter_surfaces)])
                res.append(s)
                
        res.append(s)
            
    return res

def create_bounds(surfaces, width, distance, n_rects):
    box = rs.BoundingBox(surfaces)
    
    path = rs.AddLine(box[0],box[4])
    points = box[0:4]
    points.append(box[0])
    #curves = []
    margin_left = 1
    margin_top = 0.2
    #distance = 1
    distance = width + distance
    #n_rects=2
    for j in range(n_rects):
        curves = []
        for k in range(2):
            p1 = rs.PointAdd(points[0], ((-distance*j)+(-width*k)-margin_left,(-distance*j)+(-width*k)+margin_top,0))
            p2 = rs.PointAdd(points[1], ((distance*j)+(width*k)+margin_left,(-distance*j)+(-width*k)+margin_top,0))
            p3 = rs.PointAdd(points[2], ((distance*j)+(width*k)+margin_left,(distance*j)+(width*k)-margin_top,0))
            p4 = rs.PointAdd(points[3], ((-distance*j)+(-width*k)-margin_left,(distance*j)+(width*k)-margin_top,0))
            np = [p1,p2,p3,p4,p1]
            curves.append(rs.AddPolyline(np))
            #rs.ExtrudeCurve(c0, path)
            #rs.ExtrudeCurve(c1, path)
        s0 = rs.ExtrudeCurve(curves[0], path)
        s1 = rs.ExtrudeCurve(curves[1], path)
        rs.CapPlanarHoles(s0)
        rs.CapPlanarHoles(s1)
        rs.BooleanDifference([s1],[s0])
    
def run(text, width, distance, n_rects):
    path = rs.AddLine((0,0,0),(0,0,0.1))
    curve_nums = num_letter_curves(text)
    curves = create_text_curves(text)
    surfaces = create_text_surfaces(curves, curve_nums)
    create_bounds(surfaces, width, distance, n_rects)
    
    return True

def normalize_inputs(width, distance, n_rects):
    width = width*4.5 + 0.2
    distance = distance*4.5 + 0.2
    n_rects = int(math.floor((12 * n_rects) + 1))
    return (width, distance, n_rects)

def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetOption()
    a1_o = Rhino.Input.Custom.OptionDouble(0.5)
    a2_o = Rhino.Input.Custom.OptionDouble(0.5)
    a3_o = Rhino.Input.Custom.OptionDouble(0.5)
    
    go.AddOptionDouble("a1", a1_o)
    go.AddOptionDouble("a2", a2_o)
    go.AddOptionDouble("a3", a3_o)
    
    go.AcceptNothing(True)
    while True:
        if go.Get()!=Rhino.Input.GetResult.Option:
            break
            
    a1 = a1_o.CurrentValue
    a2 = a2_o.CurrentValue
    a3 = a3_o.CurrentValue
    
    text = rs.GetString()

    (width, distance, n_rects) = normalize_inputs(a1,a2,a3)
    
    rs.EnableRedraw(False)
    run(text, width, distance, n_rects)
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
