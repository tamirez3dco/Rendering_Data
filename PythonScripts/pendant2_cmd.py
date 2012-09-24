import math
import rhinoscriptsyntax as rs
import scriptcontext
import Rhino
import itertools
import random

__commandname__ = "pendant2"

ORIGIN = (0,0,0)
X0 = (1,0,0)
Y0 = (0,1,0)
Z0 = (0,0,1)

def create_border():
    border = rs.AddCircle(rs.WorldXYPlane(), 10)
    return border

def create_base_pattern_curves(border, num_curves, rotations):
    domain = rs.CurveDomain(border)
    curves=[]
    for i in range(num_curves):
        p1 = random.uniform(domain[0],domain[1])
        fr1 = rs.CurveFrame(border, p1)
        
        d = random.uniform(10, domain[1]-10)
        p2 = p1+d 
        if p2>domain[1]:
            p2 = p2-domain[1]
            
        fr2 = rs.CurveFrame(border, p2)
        p3 = (random.uniform(-8,8), random.uniform(-8,8), 0)
        c = rs.AddLine(fr1.Origin, fr2.Origin)
        #c = rs.AddInterpCurve([fr1.Origin, p3, fr2.Origin])
        curves.append(c)
        
    all_curves = curves
    deg = 360.0 / float(rotations)
    for j in range(rotations):
        new_curves = rs.RotateObjects(curves, ORIGIN, deg*j, None, True)
        all_curves = all_curves+new_curves
        
    return all_curves
    
#def create_base_pattern_curves(border, num_curves, rotations):
    #c = rs.AddLine(fr1.Origin, fr2.Origin)
    #mid_point = rs.CurveMidPoint(c)
    

def project_shape(frame, radius, wave):
    distance = rs.Distance(frame.Origin, ORIGIN)
    height = 0.1 + ((1 + math.sin(distance*wave)) / 2)
    #print height
    #height = random.uniform(0.1,0.5)
    pipe_path = rs.AddLine(frame.Origin, (frame.Origin[0], frame.Origin[1], height))
    #rs.AddPipe(
    return rs.AddPipe(pipe_path, rs.CurveDomain(pipe_path),  [radius,radius], cap=2)
    return rs.AddCylinder(frame.Origin, height, radius) 
    return rs.AddSphere(frame,radius)
    #rs.AddLoftSrf(
    
def project_shapes(curves, radius, wave):
    all_shapes = []
    for curve in curves:
        points = rs.DivideCurveLength(curve, (radius*2)-0.03)
        shapes = map(lambda x: project_shape(rs.CurveFrame(curve,rs.CurveClosestPoint(curve,x)),radius, wave), points)
        all_shapes = all_shapes + shapes
    return all_shapes
    
def copy_shapes(shapes):
    new_shapes = rs.CopyObjects(shapes)
    rs.ScaleObjects(new_shapes, ORIGIN, (0.7,0.7,1))
    rs.MoveObjects(new_shapes,(0,-16,0))
    return new_shapes

def run(radius, n_curves, rotations, wave):
    random.seed(3)
    border = create_border()
    curves1 = create_base_pattern_curves(border, n_curves, rotations)
    #curves2 = copy_shapes(curves1)
    shapes1 = project_shapes(curves1, radius, wave)
    #shapes2 = project_shapes(curves2, radius, wave)
    #copy_shapes(shapes)
    rs.DeleteObjects(curves1)
    fit_scene(shapes1)
    #fit_scene(shapes2)
    
def fit_scene(polygons):
    b = rs.BoundingBox(polygons)
    trs = (0, -b[0][1], 0)
    rs.MoveObjects(polygons, trs)
    rs.RotateObjects(polygons, (0,0,0), -100, rs.VectorCreate((0,0,0),(10,0,0)))
    rs.RotateObjects(polygons, (0,0,0), 200.4)
    
def normalize_inputs(radius, n_curves, rotations, wave):
    #0.2 - 4.0
    radius = radius * 3.8 + 0.2
    n_curves = int(math.floor(n_curves * 20)) + 3
    rotations = int(math.floor(rotations * 12)) + 1
    wave = wave * 6 + 0.5
    return (radius, n_curves, rotations, wave)

def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetOption()
    a1_o = Rhino.Input.Custom.OptionDouble(0.2)
    a2_o = Rhino.Input.Custom.OptionDouble(0.21)
    a3_o = Rhino.Input.Custom.OptionDouble(0.2)
    a4_o = Rhino.Input.Custom.OptionDouble(0.2)
    
    go.AddOptionDouble("a1", a1_o)
    go.AddOptionDouble("a2", a2_o)
    go.AddOptionDouble("a3", a3_o)
    go.AddOptionDouble("a4", a4_o)
    go.AcceptNothing(True)
    while True:
        if go.Get()!=Rhino.Input.GetResult.Option:
            break
            
    a1 = a1_o.CurrentValue
    a2 = a2_o.CurrentValue
    a3 = a3_o.CurrentValue
    a4 = a4_o.CurrentValue
    #text = rs.GetString()
    text = 'aa'
    
    (radius, n_curves, rotations, wave) = normalize_inputs(a1,a2, a3, a4)
   
    rs.EnableRedraw(False)
    run(radius, n_curves, rotations, wave)
    rs.EnableRedraw(True)
    
if( __name__=="__main__" ):
    RunCommand(True)
