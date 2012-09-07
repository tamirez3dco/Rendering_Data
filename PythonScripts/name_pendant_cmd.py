import math
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino
import itertools

__commandname__ = "name_pendant"

ORIGIN = (0,0,0)
X0 = (1,0,0)
Y0 = (0,1,0)
Z0 = (0,0,1)


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

def add_text(text):
    curve_nums = num_letter_curves(text)
    curves = create_text_curves(text)
    surfaces = create_text_surfaces(curves, curve_nums)
    return surfaces
    
def sweep1(rail, cross_sections):
    rail_crv = rs.coercecurve(rail)
    if not rail_crv: return
    if not cross_sections: return
    cross_sections = [rs.coercecurve(crv) for crv in cross_sections]
 
    sweep = Rhino.Geometry.SweepOneRail()
    sweep.AngleToleranceRadians = scriptcontext.doc.ModelAngleToleranceRadians
    sweep.ClosedSweep = False
    sweep.MiterType = 2
    sweep.SweepTolerance = scriptcontext.doc.ModelAbsoluteTolerance
    sweep.SetToRoadlikeTop()
    breps = sweep.PerformSweep(rail_crv, cross_sections)
    guids=[]
    for brep in breps: 
        rc = scriptcontext.doc.Objects.AddBrep(brep)
        guids.append(rc)
    scriptcontext.doc.Views.Redraw()
    return guids

def PlaneRemapToPlaneSpace(plane_guid, point):
    plane_obj = rs.coerceplane(plane_guid)
    (status, point) = plane_obj.RemapToPlaneSpace(rs.coerce3dpoint(point))
    return point

def PlanePointAt(plane_guid, point):
    plane_obj = rs.coerceplane(plane_guid)
    point = plane_obj.PointAt(point[0], point[1], point[2])
    return point

def create_section_shape(plane, width, height):
    points = [ORIGIN, (-width,0,0), (-width, height, 0), (0,height,0), ORIGIN]
    mapped_points = map(lambda x: PlanePointAt(plane, x), points)
    shape = rs.AddPolyline(mapped_points)
    #shape = rs.AddRectangle(plane, width, height)
    return shape
    
def polygon_corners(center, n, radius):
    circle = rs.AddCircle(center, radius)
    rs.RotateObject(circle, center, 90)
    corners = rs.DivideCurve(circle ,n)
    rs.DeleteObject(circle)
    return corners

def polygon(center, n, radius):
    corners = polygon_corners(center, n, radius)
    corners.append(corners[0])
    polygon = rs.AddPolyline(corners)
    return polygon

def project_section(plane, section):
    rs.AddPlaneSurface(plane, 20, 20)
    #rs.ProjectCurveToSurface(

def polygon_cross_sections(poly, n, width, height):
    section_points = rs.DivideCurve(poly, 2*n, False, True)
    mid_section_points = section_points[1:2*n:2]
    corner_section_points = section_points[0:2*n:2]
    cross_sections = []
    
    for i in range(n):
        section_plane = rs.PlaneFromPoints(corner_section_points[i], ORIGIN, Z0)
        #project_section(section_plane,None)
        cross_section = create_section_shape(section_plane, width, height)
        cross_sections.append(cross_section)
        
    return {'points': section_points, 'sections': cross_sections}

def sweep_polygon(poly, n, section_width, section_height):
    section_data = polygon_cross_sections(poly, n, section_width, section_height)
    srf1 = sweep1(poly, section_data['sections'])
    help_line = rs.AddLine(section_data['points'][-1],section_data['points'][0])
    srf2 = sweep1(help_line, [section_data['sections'][-1], section_data['sections'][0]])
    polygon_brep = rs.BooleanUnion([srf1, srf2])
    rs.DeleteObject(help_line)
    rs.DeleteObjects(section_data['sections'])
    
    return polygon_brep

def create_all_polygons(polygon_sides, radius_in, radius_out, distance, section_width, section_height):
    #rad_diff = (radius_out-radius_in)/float(num_polygons)
    rad_diff = section_width+distance
    num_polygons = int(math.ceil((radius_out-radius_in)/rad_diff))
    polygons=[]
    #for i in range(num_polygons):
    rad = radius_out    
    while(True):
        if (rad-section_width)<0.1:
            break
        poly = polygon(ORIGIN, polygon_sides, rad-section_width)
        polygon_brep = sweep_polygon(poly, polygon_sides, section_width, section_height)
        polygons.append(polygon_brep)
        rs.DeleteObject(poly)
        rad = rad-(rad_diff)
    return polygons

def create_text_bounding_rect(width, height):
    rect = rs.AddRectangle(rs.WorldXYPlane(), width, height)
    rs.MoveObject(rect, (-width/2, -height/2, 0))
    

def create_trim_planes(width, height):
    planes = []
    h2 = float(height)/2.0
    w2 = float(width)/2.0
    planes.append(rs.PlaneFromPoints((0,-h2,0), (w2,-h2,0), (0, -h2, -1)))
    planes.append(rs.PlaneFromPoints((w2,0,0), (w2,h2,0), (w2, 0, -1)))
    planes.append(rs.PlaneFromPoints((-w2,0,0), (-w2,h2,0), (-w2, 0, 1)))
    planes.append(rs.PlaneFromPoints((0,h2,0), (w2,h2,0), (0, h2, 1)))
    return planes

def trim_polygon(polygon_brep, width, height):
    planes = create_trim_planes(width, height)
    res = []
    for plane in planes:
        poly_copy = rs.CopyObject(polygon_brep)
        retained = rs.TrimBrep(poly_copy, plane)
        if(len(retained)==0):
            rs.DeleteObject(poly_copy)
        else:
            res.append(retained[0])
    rs.DeleteObject(polygon_brep)
    return res
    
def trim_all_polygons(polygons, width, height):
    res = []
    for poly in polygons:
        trimed = trim_polygon(poly, width, height)  
        for t in trimed:
            res.append(t)
    return res

def create_text_surfaces():
    text_surfaces = add_text(text)
    rs.ScaleObjects(text_surfaces, ORIGIN, (2.2,2.2,15))
    rs.MoveObjects(text_surfaces, (-5,-1,0))
    
def fit_scene(polygons):
    b = rs.BoundingBox(polygons)
    trs = (0, -b[0][1], 0)
    rs.MoveObjects(polygons, trs)
    rs.RotateObjects(polygons, (0,0,0), -100, rs.VectorCreate((0,0,0),(10,0,0)))
    rs.RotateObjects(polygons, (0,0,0), 200.4)
    
def run(text, section_width, distance, polygon_sides):
    #polygon_sides = 3
    radius_in = 5
    radius_out = 16.5
    section_height = 0.5
    text_width = 16
    text_height = 3
    center_width = text_width + 1
    center_height = text_height + 1 
    text = text.upper()
    #create_text_bounding_rect(center_width, center_height)
    polygons = create_all_polygons(polygon_sides, radius_in, radius_out, distance, section_width, section_height)
    polygons = trim_all_polygons(polygons, center_width, center_height )
    fit_scene(polygons)
    
def normalize_inputs(width, distance, n_corners):
    width = width*3 + 0.5
    distance = distance*3 + 0.3
    n_corners = int(math.floor((6 * n_corners) + 3))  
    return (width, distance, n_corners)

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

    (width, distance, n_corners) = normalize_inputs(a1,a2, a3)
   
    rs.EnableRedraw(False)
    run(text, width, distance, n_corners)
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
