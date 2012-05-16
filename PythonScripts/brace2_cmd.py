#import rhinoscript.userinterface
#import rhinoscript.geometry
import math
import collections
import rhinoscriptsyntax as rs
import Rhino
import itertools

__commandname__ = "brace2"

def run(ring_rad_diff, n_ring_divisions, n_circle_divisions, in_circle_rad, out_circle_rad, div_pipe_rad, in_pipe_rad, out_pipe_rad, division_shift):
    ring_rad_diff = ring_rad_diff*3
    #n_ring_divisions = int(math.floor((14 * n_ring_divisions) + 10))
    n_circle_divisions = int(math.floor((17 * n_circle_divisions) + 3))
    in_circle_rad = (9*in_circle_rad)+1
    out_circle_rad = (9*out_circle_rad)+1
    div_pipe_rad = (1.1 * div_pipe_rad) + 0.2
    in_pipe_rad = (1.1 * in_pipe_rad) + 0.2
    out_pipe_rad = (1.1 * out_pipe_rad) + 0.2
    division_shift = math.floor(float(n_circle_divisions/2.0) * division_shift) 
    
    ring_in_rad = 15
    ring_out_rad = ring_in_rad + ring_rad_diff
    
    p1 = (0, 0, ring_in_rad)
    p2 = (0, 0, ring_out_rad)
    
    c1 = rs.AddCircle(p1, in_circle_rad)
    c2 = rs.AddCircle(p2, out_circle_rad)
    
    in_pipe = rs.AddPipe(c1, 0, in_pipe_rad, cap=0)
    out_pipe = rs.AddPipe(c2, 0, out_pipe_rad, cap=0)
    pipes = [in_pipe, out_pipe]
   
    divs1 = rs.DivideCurve(c1, n_circle_divisions, create_points=False)
    divs2 = rs.DivideCurve(c2, n_circle_divisions, create_points=False)
    
    rs.DeleteObjects([c1,c2])
    q = collections.deque(divs2)
    q.rotate(division_shift)
    divs2 = list(q)
    
    for p1,p2 in zip(divs1, divs2):
        l = rs.AddLine(p1,p2)
        pipe = rs.AddPipe(l, 0, div_pipe_rad, cap=2)
        rs.DeleteObject(l)
        pipes.append(pipe)
        
    axis = rs.VectorCreate((0,0,0),(0,10,0))
    all_pipes = [pipes]
    
    #a = rs.BooleanUnion(pipes)
    
    #print a
    #return
    bb = rs.BoundingBox(pipes)
    circum = math.pi * 2 * ( ring_in_rad + (ring_rad_diff/2))
    #print circum
    width = (bb[1][0] - bb[0][0])-0.2
    #print width
    min_ring_divisions = max(10,math.ceil(circum/width)+1)
    max_ring_divisions = min((min_ring_divisions-1)*3,30)
    n_ring_divisions = int(min_ring_divisions + (n_ring_divisions * (max_ring_divisions - min_ring_divisions)))
    
    for i in range(1,n_ring_divisions):
        new_pipes = rs.RotateObjects(pipes, (0,0,0), i*(360.0/float(n_ring_divisions)), axis=axis, copy=True)
        all_pipes.append(new_pipes)
        
    all_pipes = list(itertools.chain(*all_pipes))
    bb = rs.BoundingBox(all_pipes)
    rs.MoveObjects(all_pipes, (0,0,-bb[0][2]))
    #print bb[0][2]
    
def RunCommand( is_interactive ):
    go = Rhino.Input.Custom.GetOption()
    
    a1_o = Rhino.Input.Custom.OptionDouble(0.3)
    a2_o = Rhino.Input.Custom.OptionDouble(0.01)
    a3_o = Rhino.Input.Custom.OptionDouble(0.3)
    a4_o = Rhino.Input.Custom.OptionDouble(0.1)
    a5_o = Rhino.Input.Custom.OptionDouble(0.4)
    a6_o = Rhino.Input.Custom.OptionDouble(0.01)
    a7_o = Rhino.Input.Custom.OptionDouble(0.01)
    a8_o = Rhino.Input.Custom.OptionDouble(0.3)
    a9_o = Rhino.Input.Custom.OptionDouble(0.5)
     
    go.AddOptionDouble("a1", a1_o)
    go.AddOptionDouble("a2", a2_o)
    go.AddOptionDouble("a3", a3_o)
    go.AddOptionDouble("a4", a4_o)
    go.AddOptionDouble("a5", a5_o)
    go.AddOptionDouble("a6", a6_o)
    go.AddOptionDouble("a7", a7_o)
    go.AddOptionDouble("a8", a8_o)
    go.AddOptionDouble("a9", a9_o)
    
    go.AcceptNothing(True)
    while True:
        if go.Get()!=Rhino.Input.GetResult.Option:
            break
            
    a1 = a1_o.CurrentValue
    a2 = a2_o.CurrentValue
    a3 = a3_o.CurrentValue
    a4 = a4_o.CurrentValue
    a5 = a5_o.CurrentValue
    a6 = a6_o.CurrentValue
    a7 = a7_o.CurrentValue
    a8 = a8_o.CurrentValue
    a9 = a9_o.CurrentValue
    
    rs.EnableRedraw(False)
    run(a1,a2,a3,a4,a5,a6,a7,a8,a9)
    rs.EnableRedraw(True)
    return 0
  
if( __name__=="__main__" ):
    RunCommand(True)
