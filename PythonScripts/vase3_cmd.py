#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import rhinoscriptsyntax as rs
import Rhino
import itertools

__commandname__ = "vase3"

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
                               
    
def project_spheres(curves, r, distance):
    spheres = []
    l = r * distance
    for crv in curves:
        points = rs.DivideCurveLength(crv, l)
        for point in points:
            b = rs.AddBox([(-r,-r,-r),(r,-r,-r),(r,r,-r),(-r,r,-r),(-r,-r,r),(r,-r,r),(r,r,r),(-r,r,r)])
            #rs.AddBox(
            rs.MoveObject(b, point)
            spheres.append(b)
    return spheres
    

def create_pipes(curves, r):
    pipes = []
    for crv in curves:
        print r
        p = rs.AddPipe(crv, 0, r)
        #rs.AddPipe(
        pipes.append(p)
    return pipes

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
    v2 = rs.AddRevSrf(crv2, axis)
    
    rs.FlipSurface(v1, flip=True)
    return (v1,v2, crv1)

def get_vase_circles(curve, n_circles):
    points = rs.DivideCurve(curve, n_circles)
    circles = []
    for p in points:
        c = rs.AddCircle(rs.MovePlane(rs.WorldXYPlane(), (0,0,p[2])), p[0])
        circles.append(c)
    return circles
    
def run(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad):
    
    
    rad = [rad1, rad2, rad3, rad4]
    heights = [0, 3, 6, 10]
    
    (vase1, vase2, curve) = create_vase(rad, heights)
    circles = get_vase_circles(curve, n_vertical_divs)
    p1 = int2bool(2,2)
    p2 = int2bool(1,2)
    
    conn_pattern = int2bool(pattern_value, pattern_length*pattern_length)
    end = n_vertical_divs-1
    start = 1
    spheres = []
    #return (vase, spheres)
    while(start <= end):
        for i in range(pattern_length):
            for j in range(pattern_length):
                if(i+start > end or j+start > end): 
                    continue
                if conn_pattern[i*pattern_length + j]:
                    curve = create_patterns(vase1, circles[i+start], circles[j+start], p1, p2, n_horizontal_divs)
                    #spheres.append(project_spheres([curve], sphere_rad, sphere_distance_ratio))
                    spheres.append(create_pipes([curve], sphere_rad))
                    
        start=start+pattern_length
    all_spheres = list(itertools.chain(*spheres))
    return (vase1, vase2, all_spheres)

def normalize_inputs(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad):
    rad1 = rad1*4.5 + 1
    rad2 = rad2*4.5 + 1
    rad3 = rad3*4.5 + 1
    rad4 = rad4*4.5 + 1
    print n_vertical_divs
    n_vertical_divs = int(math.ceil(n_vertical_divs*12+3))
    print n_vertical_divs
    n_horizontal_divs = int(math.ceil(n_horizontal_divs*12+3)) * 2
    pattern_length = int(math.floor((n_vertical_divs-2)*pattern_length+1))
    print pattern_length
    pattern_value = int((math.pow(2,pattern_length*pattern_length)-1) * pattern_value) + 1
    sphere_rad = (float(sphere_rad)/5.0) + 0.04
    
    return (rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad)

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
    
    rs.EnableRedraw(False)
    (rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad) = normalize_inputs(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad)
    (vase1, vase2, spheres) = run(rad1, rad2, rad3, rad4, n_vertical_divs, n_horizontal_divs, pattern_length, pattern_value, sphere_rad)
    
    spheres.append(vase1)
    spheres.append(vase2)
    rs.ScaleObjects(spheres, (0,0,0), (3,3,3), copy=False)
    rs.RotateObjects(spheres, (0,0,0), -90, copy=False)
    
    print "n_sphers = %s" % len(spheres)
    rs.EnableRedraw(True)

if( __name__=="__main__" ):
    RunCommand(True)