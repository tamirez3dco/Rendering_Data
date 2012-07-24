#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import rhinoscriptsyntax as rs
import Rhino
import itertools

__commandname__ = "vase1"

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
    
def create_patterns(surface, segment, circle1, circle2, pattern1, pattern2, n_divisions):
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
    
    crv = rs.AddInterpCrvOnSrf(surface, final_points)
    ins = rs.CurveSurfaceIntersection(crv, segment)
    #rs.CurveSurfaceIntersection(
    start_p = rs.CurveClosestPoint(crv, ins[0][1])
    end_p = rs.CurveClosestPoint(crv, ins[0][2])
    
    np = rs.SplitCurve(crv, [start_p, end_p])
  
    #rs.DivideCurve(crv,3)
    #d = rs.CurveDomain(crv)
    #print d
    #np = rs.SplitCurve(crv,[d[1]/3,2*(d[1]/3)])
    rs.DeleteObjects([np[0],np[2]])
    return np[1]
                               
    
def project_shape(shape, point, surface):
    #new_shape = rs.CopyObject(shape)
    
    uv = rs.SurfaceClosestPoint(surface, point)
    frame = rs.SurfaceFrame(surface, uv)
    
    xform = rs.XformRotation1(rs.WorldXYPlane(),frame)
    new_shape = rs.TransformObject(shape, xform, True)
    
    return new_shape
    
def create_pattern_base_shape(r):
    #shape = rs.AddSphere((0,0,0), r)
    shape = rs.AddBox([(-r,-r,-r),(r,-r,-r),(r,r,-r),(-r,r,-r),(-r,-r,r),(r,-r,r),(r,r,r),(-r,r,r)])
    #shape = rs.AddCylinder(rs.WorldXYPlane(), r, r)
    #shape = rs.AddTorus(rs.WorldXYPlane(), r, r*0.3)
    
    return shape
    
def project_spheres(curves, r, distance, vase_surface):
    shape = create_pattern_base_shape(r)
    spheres = []
    l = r * distance
    for crv in curves:
        n = int(math.ceil(rs.CurveLength(crv) / l))
        points = rs.DivideCurve(crv, n)
        for j in range(n):
        #for point in points:
            b = project_shape(shape, points[j], vase_surface)
            #b = rs.AddSphere(points[j], r)
            spheres.append(b)
            
    return spheres
    
def create_vase_surfaces(vase_crv, out_crv, n_divs):
    axis = rs.AddLine((0,0,0),(0,0,10))
    angle1 = (360/n_divs)*2
    angle2 = angle1*5
    out_srf = rs.AddRevSrf(out_crv, axis, 0, angle2)
    vase_srf = rs.AddRevSrf(vase_crv, axis, angle1*2, angle1*3)
    out_surf_seg = rs.AddRevSrf(out_crv, axis, angle1*2, angle1*3)
    rs.DeleteObject(axis)
    return (vase_srf, out_srf, out_surf_seg)
    
def create_vase_curves(rad, heights):
    width = 0.2
    axis = rs.AddLine((0,0,0),(0,0,10))
    p_out=[]
    p_in=[]
    for r,h in zip(rad, heights):
        p_out.append((r,0,h))
        p_in.append((r-width,0,h))
    
    crv_out = rs.AddInterpCurve(p_out)
    crv_in = rs.AddInterpCurve(p_in)
    
    p = rs.CurveClosestPoint(crv_out,rs.CurveEndPoint(crv_in))
    crv_out_sp = rs.SplitCurve(crv_out, p)
    if crv_out_sp != None:
        crv_out = crv_out_sp[0]
    
    ins = rs.CurveCurveIntersection(crv_in, rs.AddLine((0,0,width+0.1), (rad[0]+1,0,width+0.1)))
    p = rs.CurveClosestPoint(crv_in, ins[0][1])
    #rs.AddPoint(ins[0][1])
    crv_in_sp = rs.SplitCurve(crv_in, p)
    crv_in = crv_in_sp[1]
    #rs.AddPoint(p)
    #rs.AddPoint(rs.CurveEndPoint(crv_out))
    #rs.AddPoint(rs.CurveEndPoint(crv_in))
    connect_line = rs.AddLine(rs.CurveEndPoint(crv_out), rs.CurveEndPoint(crv_in))
   
    frame = rs.CurveFrame(connect_line, rs.CurveParameter(connect_line,0.5))
    arc = rs.AddArc(frame,rs.CurveLength(connect_line)/2,-180)
    
    sp_in = rs.EvaluateCurve(crv_in,rs.CurveParameter(crv_in,0))
    print sp_in
    base_out = rs.AddLine((rad[0],0,0), (0,0,0))
    base_in = rs.AddLine(sp_in, (0,0,sp_in[2]))
    
    crv_vase = rs.JoinCurves([base_out, crv_out, arc, crv_in, base_in])
    
    rs.DeleteObjects([connect_line, axis, crv_in, arc])
    
    return (crv_vase, crv_out)
    
def get_vase_circles(curve, n_circles):
    points = rs.DivideCurve(curve, n_circles)
    circles = []
    for p in points:
        c = rs.AddCircle(rs.MovePlane(rs.WorldXYPlane(), (0,0,p[2])), p[0])
        circles.append(c)
    return circles
    
def rotate_all(objects, n_divs):
    angle = (360.0/float(n_divs))*2.0
    for i in range(1,int(n_divs/2)):
        rs.RotateObjects(objects, (0,0,0), angle*i, None, True)

def run(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, sphere_distance_ratio):
    rad = [rad1, rad2, rad3, rad4]
    heights = [0, 3, 6, 10]
    
    (vase_crv, out_crv) = create_vase_curves(rad, heights)
    (vase_srf, out_srf, out_surf_seg) = create_vase_surfaces(vase_crv, out_crv, n_horizontal_divs)
    
    circles = get_vase_circles(out_crv, n_vertical_divs)
    p1 = int2bool(2,2)
    p2 = int2bool(1,2)
    
    conn_pattern = int2bool(pattern_value, pattern_length*pattern_length)
    end = n_vertical_divs-1
    start = 1
    spheres = []
    while(start <= end):
        for i in range(pattern_length):
            for j in range(pattern_length):
                if(i+start > end or j+start > end): 
                    continue
                if conn_pattern[i*pattern_length + j]:
                    curve = create_patterns(out_srf, out_surf_seg, circles[i+start], circles[j+start], p1, p2, n_horizontal_divs)
                    spheres.append(project_spheres([curve], sphere_rad, sphere_distance_ratio, out_srf))
                    rs.DeleteObject(curve)
        start=start+pattern_length
    all_spheres = list(itertools.chain(*spheres))
    
    rs.DeleteObjects(circles)
    rs.DeleteObject(out_srf)
    rs.DeleteObjects([vase_crv, out_crv])
    
    all_spheres.append(vase_srf)
    rs.ScaleObjects(all_spheres, (0,0,0), (3,3,3), False)
    rotate_all(all_spheres, n_horizontal_divs)
    
    return all_spheres
    

def normalize_inputs(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, sphere_distance_ratio):
    rad1 = rad1*4.5 + 1
    rad2 = rad2*4.5 + 1
    rad3 = rad3*4.5 + 1
    rad4 = rad4*4.5 + 1
    # n_vertical_divs
    n_vertical_divs = int(math.ceil(n_vertical_divs*12+3))
    #print n_vertical_divs
    #n_horizontal_divs = int(math.ceil(n_horizontal_divs*12+3)) * 2
    n_horizontal_divs = int(math.floor(n_horizontal_divs*5+2)) * 5
    pattern_length = int(math.floor((n_vertical_divs-2)*pattern_length+1))
    #print pattern_length
    pattern_value = int((math.pow(2,pattern_length*pattern_length)-1) * pattern_value) + 1
    sphere_rad = (float(sphere_rad)/5.0) + 0.03
    sphere_distance_ratio = float(sphere_distance_ratio)*4.5 + 1.5
    
    return (rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, sphere_distance_ratio)

def RunCommand( is_interactive ):
    #Rhino.FileIO.File3dm.Read('C:\Users\aaviv\Documents\Rendering_Data\Scene\scene17.3dm')
    rad1 = 2.5
    rad2 = 3
    rad3 = 2.8
    rad4 = 4
    n_vertical_divs = 6
    n_horizontal_divs = 16
    pattern_length = 2
    pattern_value = 3
    sphere_rad = 0.1
    sphere_distance_ratio = 3
   
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
    sphere_distance_ratio_o = Rhino.Input.Custom.OptionDouble(0.5)
    
    go.AddOptionDouble("rad1", rad1_o)
    go.AddOptionDouble("rad2", rad2_o)
    go.AddOptionDouble("rad3", rad3_o)
    go.AddOptionDouble("rad4", rad4_o)
    go.AddOptionDouble("n_vertical_divs",n_vertical_divs_o )
    go.AddOptionDouble("n_horizontal_divs", n_horizontal_divs_o)
    go.AddOptionDouble("pattern_length", pattern_length_o)
    go.AddOptionDouble("pattern_value", pattern_value_o)
    go.AddOptionDouble("sphere_rad", sphere_rad_o)
    go.AddOptionDouble("sphere_distance_ratio", sphere_distance_ratio_o)
    
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
    sphere_distance_ratio = sphere_distance_ratio_o.CurrentValue
    
    #rs.EnableRedraw(False)
    (rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, sphere_distance_ratio) = normalize_inputs(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, sphere_distance_ratio)
    all = run(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad, sphere_distance_ratio)
    
    #rs.ScaleObjects(all, (0,0,0), (3,3,3), False)
    #rs.RotateObjects(spheres, (0,0,0), 90, copy=False)
    #rs.RotateObjects(spheres, (0,0,0), -30, axis=(10,4,0), copy=False)
    
    #print "n_sphers = %s" % len(spheres)
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
