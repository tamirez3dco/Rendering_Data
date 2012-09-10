
import math
import rhinoscriptsyntax as rs
import Rhino
import itertools
__commandname__ = "textnew1"


def Sweep1(rail, cross_sections):
    #rail = rs.GetObject("Select rail curve", rs.filter.curve)
    rail_crv = rs.coercecurve(rail)
    if not rail_crv: return
 
    #cross_sections = rs.GetObjects("Select cross section curves", rs.filter.curve)
    if not cross_sections: return
    cross_sections = [rs.coercecurve(crv) for crv in cross_sections]
 
    sweep = Rhino.Geometry.SweepOneRail()
    sweep.AngleToleranceRadians = scriptcontext.doc.ModelAngleToleranceRadians
    sweep.ClosedSweep = False
    sweep.SweepTolerance = scriptcontext.doc.ModelAbsoluteTolerance
    sweep.SetToRoadlikeTop()
    breps = sweep.PerformSweep(rail_crv, cross_sections)
    for brep in breps: scriptcontext.doc.Objects.AddBrep(brep)
    scriptcontext.doc.Views.Redraw()
    
def num_letter_curves(text):
    t = list(text)
    res = []
    for l in t:
        if l == " ": 
            res.append(0)
            continue
            
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
     
def base_bounds(box, n , center):
     c = rs.AddCircle(center, 0.1)
     rs.RotateObject(c, center, 90)
     d = rs.DivideCurve(c,n)
     d.append(d[0])
     bound = rs.AddPolyline(d)
     return bound

def create_text_surfaces(curves, letters):
    path = rs.AddLine((0,0,0),(0,0,0.1))
    c_index = 0
    res = []
    
    for letter in letters:
        if letter==0:
            continue
        letter_curves = curves[c_index:c_index+letter]
        letter_surfaces = []
        for crv in letter_curves:
            s = rs.ExtrudeCurve(crv, path)
            #rs.ScaleObject(s,(0,0,0), (10,10,10))
            #rs.MoveObject(s, (-27,20,0))
            rs.CapPlanarHoles(s)
            letter_surfaces.append(s)
        c_index += letter
        
        #s = letter_surfaces[0]
        if(len(letter_surfaces)>1):
            srf = rs.AddPlanarSrf([letter_curves[0]])
            ins = rs.CurveSurfaceIntersection(letter_curves[1], srf)
            rs.DeleteObject(srf)
            if len(ins) == 0:
                res.append(letter_surfaces[0])
                res.append(letter_surfaces[1])
            else:
                s = rs.BooleanDifference([letter_surfaces[0]],letter_surfaces[1:len(letter_surfaces)])
                res.append(s)
        else:
            res.append(letter_surfaces[0])
            
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

def extrude_bound2(inner_poly, outer_poly, path):
    bb = rs.BoundingBox(outer_poly)
    bbrect = rs.AddPolyline([bb[0],bb[1],bb[2],bb[3],bb[0]])
    
    center = rs.CurveAreaCentroid(bbrect)[0]
    diff_rect_bottm = rs.AddPolyline([bb[0], bb[1], (bb[1].X, center[1], bb[1].Z), (bb[3].X, center[1] ,bb[3].Z), bb[0]])
    diff_rect_top = rs.AddPolyline([bb[3], bb[2], (bb[2].X, center[1], bb[2].Z), (bb[3].X, center[1] ,bb[3].Z), bb[3]])
    rs.ScaleObjects([diff_rect_bottm,diff_rect_top] , center, (1.1,1.1,1.1))
    #diff_rect_top = diff_rect_bottm
    
    outer_top = rs.CurveBooleanDifference(outer_poly, diff_rect_bottm)
    inner_top = rs.CurveBooleanDifference(inner_poly, diff_rect_bottm)
    final_top = rs.CurveBooleanDifference(outer_top, inner_top)
    outer_bottom = rs.CurveBooleanDifference(outer_poly, diff_rect_top)
    inner_bottom = rs.CurveBooleanDifference(inner_poly, diff_rect_top)
    final_bottom = rs.CurveBooleanDifference(outer_bottom, inner_bottom)
    #rs.MoveObjects([final_top, final_bottom], (0,10,0))
    bound_top = rs.ExtrudeCurve(final_top, path)
    bound_bottom = rs.ExtrudeCurve(final_bottom, path)
    rs.CapPlanarHoles(bound_top)
    rs.CapPlanarHoles(bound_bottom)
    return [bound_top, bound_bottom]
    
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

def create_text_connectors(box, offset_rect, margin):
    offset_box = rs.BoundingBox(offset_rect)
    connector_rect = rs.AddRectangle(rs.WorldXYPlane(), (box[1][0]-box[0][0])+(2*margin), margin)
    rs.MoveObject(connector_rect, (offset_box[0][0],offset_box[0][1],0))
    path = rs.AddLine(box[0],(box[4][0],box[4][1],box[4][2]/2))
    bottom_connector = rs.ExtrudeCurve(connector_rect, path)
    rs.CapPlanarHoles(bottom_connector)
    rs.MoveObject(bottom_connector, (0,0,box[4][2]/4))
    top_connector = rs.CopyObject(bottom_connector)
    rs.MoveObject(top_connector, (0, (margin+ (box[3][1]-box[0][1])), 0))
    return (bottom_connector, top_connector)
    
def create_line_connectors(outer_curve, center, diff_box, width, extrude_path, center_outer_rect):
    v = rs.PolylineVertices(outer_curve)
    maxd = 0
    for p in v:
        d = rs.Distance(p,center)
        if d > maxd: 
            maxd = d
    eps = 0.001
    vertex = []
    for p in v:
        d = rs.Distance(p,center)
        if d+eps > maxd: 
            vertex.append(p)
            #rs.AddPoint(p)
    
    connectors = []
    for v in vertex:
        l1 = rs.AddLine(v, center)
        l2 = rs.CopyObject(l1)
        
        frame = rs.CurveFrame(l1, 0)
        n = rs.CurveNormal(l1)
        axis = frame.YAxis
        vec = rs.VectorScale(rs.VectorUnitize(rs.VectorCreate(center, v)), width/2)
        vec1 = rs.VectorRotate(vec,90,rs.VectorCreate(center,rs.PointAdd(center,(0,0,1))))
        vec2 = rs.VectorRotate(vec,-90,rs.VectorCreate(center,rs.PointAdd(center,(0,0,1))))
        rs.MoveObject(l1, vec1)
        rs.MoveObject(l2, vec2)
        
        #if axis[2] != 0:
        #    axis=(1,0,0)
            
        #rs.CurveFrame(
        #rs.MoveObject(l1, axis*(width/2))
        #rs.MoveObject(l2, -axis*(width/2))
        
        ins1  = rs.CurveCurveIntersection(l1, center_outer_rect)
        ins2  = rs.CurveCurveIntersection(l2, center_outer_rect)
        if ((ins1 == None) or (ins2 == None) or (len(ins1) == 0) or (len(ins2) == 0)):
            continue
        connector_rect = rs.AddPolyline([rs.CurveStartPoint(l1), ins1[0][1], ins2[0][1], rs.CurveStartPoint(l2), rs.CurveStartPoint(l1)])
        connector = rs.ExtrudeCurve(connector_rect, extrude_path)
        rs.CapPlanarHoles(connector)
        connectors.append(connector)
        
    return connectors

def union_poly_rect(rect, inner_poly, outer_poly, path):
    copies = rs.CopyObjects([rect, inner_poly, outer_poly])
    #rs.MoveObjects(copies, (15,0,-1))
    
    ins = rs.CurveCurveIntersection(rect, inner_poly)
    area_diff = rs.CurveArea(inner_poly)[0] - rs.CurveArea(rect)[0]
    
    inner_diff = rs.CurveBooleanDifference(inner_poly, rect)
    #rs.MoveObjects(inner_diff, (15,0,0))
    outer_diff = rs.CurveBooleanDifference(outer_poly, rect)
    #rs.MoveObjects(outer_diff, (15,0,0))
    
    u1 = rs.CurveBooleanUnion([inner_poly, rect])
    uu = rs.CopyObjects(u1, (15,0,0))
    if len(u1)==0:
        return []
    if len(u1)>1:
        u1 = [u1[0]]
        
    #rs.MoveObjects(u1, (15,0,0))
    u2 = rs.CurveBooleanDifference(outer_poly, u1)
    #rs.MoveObjects(u2, (15,0,2))
    
    res=[]
    if len(u2) == 1:
        bound = rs.ExtrudeCurve(u2[0], path)
        rs.CapPlanarHoles(bound)
        return [bound]
        
    if len(u2) > 1:
        if rs.PointInPlanarClosedCurve(rs.CurveAreaCentroid(u2[1])[0], u2[0]):
            return extrude_bound2(u2[1], u2[0], path)
        else:
            for curve in u2:
                bound = rs.ExtrudeCurve(curve, path)
                rs.CapPlanarHoles(bound)
                res.append(bound)
    
    return res
    
    if (area_diff>0) and (len(ins)==0):
        return extrude_bound2(inner_poly, outer_poly, path)
        
    res=[]
    for outer_curve in outer_diff:
        for inner_curve in inner_diff:
            ins = rs.CurveCurveIntersection(outer_curve, inner_curve)
            if len(ins)>0:
                final = rs.CurveBooleanDifference(outer_curve, inner_curve)
                #rs.MoveObject(final,(0,0,1))
                bound = rs.ExtrudeCurve(final, path)
                rs.CapPlanarHoles(bound)
                res.append(bound)
                
    #outer_inner_diff = rs.CurveBooleanDifference(outer_diff, inner_diff)
    #rs.MoveObjects(outer_inner_diff, (10,0,-0.5))
    rs.DeleteObjects(inner_diff)
    rs.DeleteObjects(outer_diff)
    rs.DeleteObjects(copies)
    return res
    

def create_bounds(surfaces, width, distance, n_rects, n_corners):
    box = rs.BoundingBox(surfaces)
    box_width = box[1][0]-box[0][0]
    shape_size=box_width*0.85
    
    n_rects = int(math.ceil((shape_size-0.1)/float((width+distance))))
    path = rs.AddLine(box[0],box[4])
    margin = 0.1
    distance = width + distance
    res=[]
    
    (cc0, center_outer_rect, bound, diff_box) = create_rect_bound(box, path)
    res.append(bound)
    
    center = rs.CurveAreaCentroid(cc0)[0]
    
    text_connectors = create_text_connectors(box, cc0, margin)
    #base_bounds2(box,n_corners)
    
    c0 = base_bounds(cc0, n_corners, center)
    c1 = rs.OffsetCurve(c0, (10,10,10), width)
    bound = extrude_bound(c0, c1, path, True)
    bound_diff = rs.BooleanDifference(bound, diff_box)
    if (bound_diff):
        res.append(bound_diff[0])
    else:
        rs.DeleteObject(bound)
    
    rs.DeleteObject(diff_box)
    inner_curves=[c0]
    for j in range(1,n_rects):
        diff_box =  extrude_bound(cc0, center_outer_rect, path, False)
        c0 = rs.OffsetCurve(inner_curves[j-1], (10,10,10), distance)
        c1 = rs.OffsetCurve(c0, (10,10,10), width)
        inner_curves.append(c0)
        #bound = extrude_bound(c0, c1, path, True)
        newbounds = union_poly_rect(center_outer_rect, c0, c1, path)
        
        #bound = rs.BooleanDifference(bound, diff_box)
        #bound_diff = rs.BooleanDifference(bound, diff_box)
        if (newbounds):
            for k in newbounds:
                res.append(k)
        else:
            pass
            #rs.DeleteObject(bound)
        rs.DeleteObject(diff_box)
        
    connectors = create_line_connectors(inner_curves[n_rects-1], center, diff_box, margin, path, center_outer_rect)
    for c in connectors:
        res.append(c)
    res.append(text_connectors[0])
    res.append(text_connectors[1])
    rs.DeleteObject(diff_box)
    return res

def fit_scene(surfaces, scale, trs):
    rs.MoveObjects(surfaces, trs)
    rs.ScaleObjects(surfaces,(0,0,0), (scale,scale,scale))
    #rs.VectorCreate(
    rs.RotateObjects(surfaces, (0,0,0), -100, rs.VectorCreate((0,0,0),(10,0,0)))
    rs.RotateObjects(surfaces, (0,0,0), 200.4)
    
    rs.MoveObjects(surfaces, (12,0,0))

def find_scale(bounds):
    max_width = 30.0
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
    a1_o = Rhino.Input.Custom.OptionDouble(0.6)
    a2_o = Rhino.Input.Custom.OptionDouble(0.6)
    a3_o = Rhino.Input.Custom.OptionDouble(0.6)
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
    text = text.upper()
    (width, distance, n_rects, n_corners) = normalize_inputs(a1,a2, a4, a3)
   
    #rs.EnableRedraw(False)
    run(text, width, distance, n_rects, n_corners)
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
