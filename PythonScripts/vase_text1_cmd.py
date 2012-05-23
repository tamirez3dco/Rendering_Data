#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino
import itertools

__commandname__ = "vase_text1"

def Denary2Binary(n):
    '''convert denary integer n to binary string bStr'''
    bStr = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr

def int2bin(n, count=24):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

def int2bool(n, count):
    binary = int2bin(n,count)
    return map(lambda x: int(x)==1, list(binary))
    
def create_patterns(surface, circle1, circle2, pattern1, pattern2, n_divisions):
    points = []
    for circle in [circle1, circle2]:
        divs = rs.DivideCurve(circle, n_divisions)
        points.append(divs)
    
    final_points = []
    for i in range(n_divisions):   
        if pattern1[i % len(pattern1)]:
            final_points.append(points[0][i]) 
        if pattern2[i % len(pattern2)]:
            final_points.append(points[1][i])         
    
    p = rs.AddInterpCrvOnSrf(surface, final_points)
    return p
                               
    

def create_vase(rad, heights):
    p1=[]
    p2=[] 
    #p1.append((0,0,0))
    for r,h in zip(rad, heights):
        p1.append((r,0,h))
        p2.append((r-0.2,0,h))
    
    p2[0] = (p2[0][0], 0, p2[0][2]+0.2)
    #p1.append((0,0,0))
    
    crv1 = rs.AddInterpCurve(p1)
    crv2 = rs.AddInterpCurve(p2)
    mp = (p1[3][0]-0.1, 0, p1[3][2]+0.05)
    #rs.AddPoint((p1[3][0]-0.1, 0, p1[3][2]+0.05))
    #return x
    p2.reverse()
    #comb_p = list(itertools.chain(*[p1,[mp],p2]))
    #comb_crv = rs.AddInterpCurve(comb_p)
    #return x
    axis = rs.AddLine((0,0,0),(0,0,10))
    
    v1 = rs.AddRevSrf(crv1, axis)
    #v2 = rs.AddRevSrf(crv2, axis)
    
    rs.FlipSurface(v1, flip=True)
    rs.DeleteObject(axis)
    return (v1, crv1)

def project_text0(vase):
    size = Rhino.Geometry.Surface.GetSurfaceSize(rs.coercesurface(vase))
    boundary = rs.AddRectangle(rs.WorldXYPlane(), size[1], size[2])
   
    curves = create_text_curves("naama")
    new_curves = apply_crv(vase, boundary, curves)
    
    #rs.DeleteObjects(text_obj)
    #rs.DeleteObjects(boundary)
    
    id = rs.coerceguid(new_curves[2], True)
    new_srf = split_srf(vase, [id])
    
    strid = new_srf[1].Id.ToString()
    rs.FlipSurface(new_srf[1].Id, flip=True)
    bb = rs.coerceboundingbox(rs.BoundingBox(strid))
    normal = rs.SurfaceNormal(strid, rs.SurfaceClosestPoint(strid, bb.Center))
    cmd = "_ExtrudeSrf _SelID %s _Enter Direction %s %s 0.1 _Enter" % (strid,  point2str(normal), point2str(bb.Center))
    
    print cmd
    rs.Command(cmd)
    
    return True
    

def project_text(vase, text, ndivs, div_y, x):
    size = Rhino.Geometry.Surface.GetSurfaceSize(rs.coercesurface(vase))
    boundary = rs.AddRectangle(rs.WorldXYPlane(), size[1], size[2])
    
    letters = list(text)
    letter_ncurves = []
    height = size[2]/ndivs
    for letter in letters:
        curves = create_text_curves("m" + letter, height, x, height*div_y)
        letter_ncurves.append(len(curves)-1)
        rs.DeleteObjects(curves)
        
    curves = create_text_curves(text, height, x, height*div_y)
    start=0
    splitted_vase = vase
    all_extruded = []
    for i in range(len(letters)):
        letter_curves = curves[start:start+letter_ncurves[i]]
        start = start+letter_ncurves[i]
        proj_curves = apply_crv(splitted_vase, boundary, letter_curves)
        ids = proj_curves[:letter_ncurves[i]]
        #rs.AddPipe(ids[0],[0],[0.1])
        print ids
        new_srf = split_srf(splitted_vase, ids)
        splitted_vase = new_srf[0]
        rs.FlipSurface(new_srf[1], flip=True)
        extruded = extrude_srf(new_srf[1])
        all_extruded.append(extruded[0])
    
    all_extruded.append(splitted_vase)
    rs.DeleteObjects(curves)
    rs.DeleteObjects(boundary)
    return all_extruded
    

def point2str(p):
    return "%s,%s,%s" % (p[0],p[1],p[2])

def extrude_srf(srf):
    bb = rs.coerceboundingbox(rs.BoundingBox(srf))
    normal = rs.SurfaceNormal(srf, rs.SurfaceClosestPoint(srf, bb.Center))
    cmd = "_ExtrudeSrf _SelID %s _Enter Direction %s %s 0.1 _Enter" % (srf,  point2str(normal), point2str(bb.Center))
    serial = get_serial()
    rs.Command(cmd)
    return get_command_objects(serial)
    
def split_srf(srf, curves):
    cmd = "_Split _SelID %s _Enter " % srf.ToString()
    for c in curves: 
        cmd = cmd + ("_SelID %s " % c.ToString())
    cmd = cmd + "_Enter"
    print cmd
    serial = get_serial()
    rs.Command(cmd)
    return get_command_objects(serial)
    
def create_text_curves(text, height, x, y):
    point = (x,y,0)
    cmd = "-_TextObject Height=%s Output=Curves FontName=Comic_Sans_MS %s %s Enter" % (height, text, point2str(point))
    serial = get_serial()
    print cmd
    rs.Command(cmd)
    curves = get_command_objects(serial)
    #v = rs.CloseCurve(curves[0],30)
    #map(lambda x: rs.CloseCurve(x, 10), curves)
    return curves
    
def apply_crv(srf, boundary, curves):
    curves.append(boundary)
    curves.append(srf)
    rs.SelectObjects(curves)
    cmd = "-_ApplyCrv Enter"
    serial = get_serial()
    rs.Command(cmd)
    new_curves = get_command_objects(serial)
    rs.UnselectAllObjects()
    rs.DeleteObject(new_curves[len(new_curves)-1])
    return new_curves
    
def get_serial():
    ref_point = rs.AddPoint(0,0,0)
    a = scriptcontext.doc.Objects.MostRecentObject()
    s = a.RuntimeSerialNumber
    rs.DeleteObject(ref_point)
    return s

def get_command_objects(serial):
    objs = list(scriptcontext.doc.Objects.AllObjectsSince(serial))
    return map(lambda x: rs.coerceguid(x, True), objs)
    #return map(lambda x: x, objs)

def get_vase_circles(curve, n_circles):
    points = rs.DivideCurve(curve, n_circles)
    circles = []
    for p in points:
        c = rs.AddCircle(rs.MovePlane(rs.WorldXYPlane(), (0,0,p[2])), p[0])
        circles.append(c)
    return circles
    
def run(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, text):
    rs.UnselectAllObjects()
    rad = [rad1, rad2, rad3, rad4]
    heights = [0, 3, 6, 10]
    
    (vase1, curve) = create_vase(rad, heights)
    vase_model_parts = project_text(vase1, text, n_vertical_divs, 2, 7)
    #extruded_text.append(vase1)
    #circles = get_vase_circles(curve, n_vertical_divs)

    return vase_model_parts

def normalize_inputs(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad):
    rad1 = rad1*4.5 + 1
    rad2 = rad2*4.5 + 1
    rad3 = rad3*4.5 + 1
    rad4 = rad4*4.5 + 1
    n_vertical_divs = int(math.ceil(n_vertical_divs*12+3))
    print n_vertical_divs
    n_horizontal_divs = int(math.ceil(n_horizontal_divs*12+3)) * 2
    pattern_length = int(math.floor((n_vertical_divs-2)*pattern_length+1))
    print pattern_length
    pattern_value = int((math.pow(2,pattern_length*pattern_length)-1) * pattern_value) + 1
    sphere_rad = (float(sphere_rad)/5.0) + 0.04
    
    return (rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad)

def RunCommand( is_interactive ):
    rad1 = 2.5
    rad2 = 3
    rad3 = 2.8
    rad4 = 4
    n_vertical_divs = 6
    n_horizontal_divs = 16
    pattern_length = 2
    pattern_value = 3
    sphere_rad = 0.1
    
    go = Rhino.Input.Custom.GetOption()
    
    rad1_o = Rhino.Input.Custom.OptionDouble(0.3)
    rad2_o = Rhino.Input.Custom.OptionDouble(0.5)
    rad3_o = Rhino.Input.Custom.OptionDouble(0.3)
    rad4_o = Rhino.Input.Custom.OptionDouble(0.6)
    n_vertical_divs_o = Rhino.Input.Custom.OptionDouble(0.5)
    n_horizontal_divs_o = Rhino.Input.Custom.OptionDouble(0.5)
    pattern_length_o = Rhino.Input.Custom.OptionDouble(0.2)
    pattern_value_o = Rhino.Input.Custom.OptionDouble(0.3)
    sphere_rad_o = Rhino.Input.Custom.OptionDouble(0.5)
    
    
    go.AddOptionDouble("rad1", rad1_o)
    go.AddOptionDouble("rad2", rad2_o)
    go.AddOptionDouble("rad3", rad3_o)
    go.AddOptionDouble("rad4", rad4_o)
    go.AddOptionDouble("n_vertical_divs",n_vertical_divs_o )
    go.AddOptionDouble("n_horizontal_divs", n_horizontal_divs_o)
    go.AddOptionDouble("pattern_length", pattern_length_o)
    go.AddOptionDouble("pattern_value", pattern_value_o)
    go.AddOptionDouble("sphere_rad", sphere_rad_o)
    
    
    go.AcceptNothing(True)
    while True:
        if go.Get()!=Rhino.Input.GetResult.Option:
            break
            
    
    rad1 = rad1_o.CurrentValue
    rad2 = rad2_o.CurrentValue
    rad3 = rad3_o.CurrentValue
    rad4 = rad4_o.CurrentValue
    n_vertical_divs = n_vertical_divs_o.CurrentValue
    n_horizontal_divs = n_horizontal_divs_o.CurrentValue
    pattern_length = pattern_length_o.CurrentValue
    pattern_value = pattern_value_o.CurrentValue
    sphere_rad = sphere_rad_o.CurrentValue
    
    rad1 = 0.3
    rad2 = 0.5
    rad3 = 0.3
    rad4 = 0.6
    #text = rs.GetString()
    text = "naama"
    
    rs.EnableRedraw(False)
    (rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad) = normalize_inputs(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad)
    (vase1) = run(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, text)
    
    rs.ScaleObjects(vase1, (0,0,0), (3,3,3), copy=False)
    rs.RotateObjects(vase1, (0,0,0), -90, copy=False)
    
    #print "n_sphers = %s" % len(spheres)
    rs.EnableRedraw(True)

if( __name__=="__main__" ):
    RunCommand(True)
    
#vase_text rad1=0.5 rad2=0.5 rad3=0.5 rad4=0.5 n_vertical_divs=0.5 n_horizontal_divs=0.5 pattern_length=0.5 pattern_value=0.5 sphere_rad=0.5 Enter naama Enter