
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
    
def base_bounds2(box, n):
     c1 = rs.AddCircle3Pt(box[0],box[1],box[2])
     return c1
     
def base_bounds(box, n):
     center = rs.CurveAreaCentroid(box)
     #rs.AddCircle(
     c = rs.AddCircle(center[0], 0.1)
     rs.RotateObject(c, center[0], 90)
     d = rs.DivideCurve(c,n)
     d.append(d[0])
     bound = rs.AddPolyline(d)
     return bound

def create_text_surfaces(curves, letters):
    path = rs.AddLine((0,0,0),(0,0,0.1))
    c_index = 0
    res = []
    
    for letter in letters:
        letter_curves = curves[c_index:c_index+letter]
        letter_surfaces = []
        for crv in letter_curves:
            s = rs.ExtrudeCurve(crv, path)
            #rs.ScaleObject(s,(0,0,0), (10,10,10))
            #rs.MoveObject(s, (-27,20,0))
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
            
    return res

def extrude_bound(b_in, b_out, path, diff):
    s1 = rs.ExtrudeCurve(b_out, path)
    rs.CapPlanarHoles(s1)
    if diff == False:
        return s1
    s0 = rs.ExtrudeCurve(b_in, path)
    rs.CapPlanarHoles(s0)
    bound = rs.BooleanDifference([s1],[s0])
    return bound
    
def create_rect_bound(box, path):
    points = box[0:4]
    points.append(box[0])
    
    margin = 0.1
    c0 = rs.AddPolyline(points)
    cc0 = rs.OffsetCurve(c0, (10,10,10), margin)
    cc1 = rs.OffsetCurve(cc0, (10,10,10), 0.1)
    bound = extrude_bound(cc0, cc1, path, True)
    diff_box =  extrude_bound(cc0, cc1, path, False)
    return (cc0, cc1, bound, diff_box)
    
def create_bounds(surfaces, width, distance, n_rects, n_corners):
    box = rs.BoundingBox(surfaces)
    box_width = box[1][0]-box[0][0]
    shape_size=box_width*0.85
    
    n_rects = int(math.ceil((shape_size-0.1)/float((width+distance))))
    path = rs.AddLine(box[0],box[4])
    margin = 0.1
    distance = width + distance
    res=[]
    
    (cc0, cc1, bound,diff_box) = create_rect_bound(box, path)
    res.append(bound)
    base_bounds2(box,n_corners)
    
    c0 = base_bounds(cc0,n_corners)
    c1 = rs.OffsetCurve(c0, (10,10,10), width)
    bound = extrude_bound(c0, c1, path, True)
    bound_diff = rs.BooleanDifference(bound, diff_box)
    if (bound_diff):
        res.append(bound_diff[0])
    else:
        rs.DeleteObject(bound)
        
    cc=[c0]
    for j in range(1,n_rects):
        diff_box =  extrude_bound(cc0, cc1, path, False)
        c0 = rs.OffsetCurve(cc[j-1], (10,10,10), distance)
        c1 = rs.OffsetCurve(c0, (10,10,10), width)
        cc.append(c0)
        bound = extrude_bound(c0, c1, path, True)
        #bound = rs.BooleanDifference(bound, diff_box)
        bound_diff = rs.BooleanDifference(bound, diff_box)
        if (bound_diff):
            for k in bound_diff:
                res.append(k)
        else:
            rs.DeleteObject(bound)
        
    rs.DeleteObject(diff_box)
    return res

def fit_scene(surfaces, scale, trs):
    rs.MoveObjects(surfaces, trs)
    rs.ScaleObjects(surfaces,(0,0,0), (scale,scale,scale))
    #rs.VectorCreate(
    rs.RotateObjects(surfaces, (0,0,0), -80, rs.VectorCreate((0,0,0),(10,0,0)))
    rs.RotateObjects(surfaces, (0,0,0), 20.4)
    
    rs.MoveObjects(surfaces, (-18.5,-8,0))

def find_scale(bounds):
    max_width = 36.0
    b = rs.BoundingBox(bounds)
    bb_width = b[1][0] - b[0][0]
    scale = max_width / bb_width
    trs = (-b[0][0], -b[0][1], 0)
    return (scale, trs)
    
def run(text, width, distance, n_rects, n_corners):
    curve_nums = num_letter_curves(text)
    curves = create_text_curves(text)
    surfaces = create_text_surfaces(curves, curve_nums)
    bounds = create_bounds(surfaces, width, distance, n_rects, n_corners)
    (scale, trs) = find_scale(bounds)
    fit_scene(surfaces, scale, trs)
    fit_scene(bounds, scale, trs)
    #find_scale(bounds)
    return True

def normalize_inputs(width, distance, n_rects, n_corners):
    width = width*0.3 + 0.1
    distance = distance*0.3 + 0.07
    n_rects = int(math.floor((12 * n_rects) + 1))
    n_corners = int(math.floor((6 * n_corners) + 3))  
    return (width, distance, n_rects, n_corners)

def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetOption()
    a1_o = Rhino.Input.Custom.OptionDouble(0.5)
    a2_o = Rhino.Input.Custom.OptionDouble(0.5)
    a3_o = Rhino.Input.Custom.OptionDouble(0.5)
    #a4_o = Rhino.Input.Custom.OptionDouble(0.5)
    
    go.AddOptionDouble("a1", a1_o)
    go.AddOptionDouble("a2", a2_o)
    go.AddOptionDouble("a3", a3_o)
    #go.AddOptionDouble("a4", a4_o)
    go.AcceptNothing(True)
    while True:
        if go.Get()!=Rhino.Input.GetResult.Option:
            break
            
    a1 = a1_o.CurrentValue
    a2 = a2_o.CurrentValue
    a3 = a3_o.CurrentValue
    #a4 = a4_o.CurrentValue
    a4 = 0.5
    text = rs.GetString()

    (width, distance, n_rects, n_corners) = normalize_inputs(a1,a2, a4, a3)
   
    #rs.EnableRedraw(False)
    run(text, width, distance, n_rects, n_corners)
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
