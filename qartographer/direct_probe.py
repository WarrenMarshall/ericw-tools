#!/usr/bin/env python3
"""Exact MAP halfspace oracle for the frozen unregularized RollerSpline.
Usage: direct_probe.py QBSP OUTPUT. Reports finite failures without hiding them.
"""
import sys,json,subprocess,shutil
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests/helpers'))
from wildspline_bsp_collision_compile import brushes,expanded
from spline_smooth_collision_compile import BSP,margin,halton

def height(x,y,cells):
    heights=[]
    for planes in cells:
        low, high=-float('inf'),float('inf')
        for n,d in planes:
            v=d-n[0]*x-n[1]*y
            if abs(n[2])<1e-8:
                if v < -1e-5:break
            elif n[2]>0:high=min(high,v/n[2])
            else:low=max(low,v/n[2])
        else:
            if high>low+.001:heights.append(high)
    return max(heights) if heights else None

def main():
    qbsp,out=sys.argv[1],Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    fixture=Path(__file__).resolve().parent/'fixtures/roller-direct.map'
    geometry=brushes(fixture.read_text());results={}
    for chop in [False,True]:
        label='chopfragment' if chop else 'default';p=out/(label+'.map');shutil.copyfile(fixture,p)
        timing=out/(label+'.time')
        cmd=[qbsp,*(['-chopfragment'] if chop else []),'-bsp2','-notex','-nopercent',str(p)]
        run=subprocess.run(['/usr/bin/time','-f','%e %M','-o',str(timing),*cmd],capture_output=True,text=True)
        (out/(label+'.log')).write_text(run.stdout+run.stderr);assert run.returncode==0
        b=BSP(p.with_suffix('.bsp'));report={}
        for hull,radius,offset in [(0,(0,0,0),0),(1,(16,16,28),4),(2,(32,32,44),20)]:
            cells=[expanded(cell,radius) for cell in geometry];failures=[];checked=0
            if hull:
                for x in [-1480,-1460,-1452,-1448,-1400,-1368,-1340,-1336]:
                    for y in range(-2064,-1487,8):
                        top=height(x,y,cells)
                        if top is None:continue
                        checked+=1
                        for dz,want in [(-.5,-2),(1,-1)]:
                            point=(x,y,top-offset+dz)
                            if b.contents(point,hull=hull)!=want:failures.append([point,want,b.contents(point,hull=hull)])
            else:
                vertices=[v for _,vs,_ in geometry for v in vs]
                lo=[min(v[i] for v in vertices)-4 for i in range(3)];hi=[max(v[i] for v in vertices)+4 for i in range(3)]
                for k in range(1,1025):
                    point=tuple(lo[i]+halton(k,[2,3,5][i])*(hi[i]-lo[i]) for i in range(3));distance=margin(point,cells)
                    if abs(distance)<.2:continue
                    checked+=1;want=-2 if distance<0 else -1
                    if b.contents(point,hull=hull)!=want:failures.append([point,want,b.contents(point,hull=hull)])
            report[str(hull)]={'samples':checked,'failures':failures}
        seconds,rss=timing.read_text().split()
        results[label]={'hulls':report,'seconds':float(seconds),'peak_rss_kib':int(rss),'map_bytes':p.stat().st_size,'bsp_bytes':len(b.b),'clipnodes':b.l[9][1]//12}
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print({k:{h:len(v['failures']) for h,v in r['hulls'].items()} for k,r in results.items()})
if __name__=='__main__':main()
