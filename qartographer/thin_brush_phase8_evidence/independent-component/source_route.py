#!/usr/bin/env python3
"""Exact segment/support checks; binary source-reader planes, not compiler BSPs."""
from pathlib import Path
from fractions import Fraction as F
import json,re,math,time,hashlib,sys
R=Path('/home/warrenmarshall/dev/ericw-tools');E=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/qqbsp-phase6/evidence')
load=lambda p:json.loads(p.read_text())
def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
rows={}
for mode,route in load(R/'qartographer/thin_brush_phase3_evidence/leak-detour.json').items():
    start=time.perf_counter();p=R/'qartographer/fixtures'/f'{mode}.map';text=p.read_text();depth=0;cells=[]
    for m in re.finditer(r'^\s*[{}]\s*$',text,re.M):
        if m[0].strip()=='{':
            depth+=1
            if depth==2:begin=m.end()
        else:
            if depth==2:
                ps=[];excluded=False
                for line in text[begin:m.start()].splitlines():
                    vs=[list(map(float,v.split())) for v in re.findall(r'\(([^()]*)\)',line)]
                    if len(vs)!=3:continue
                    excluded |= bool(re.search(r'\) (CLIP|HINT|HINTSKIP) ',line))
                    n=cross(sub(vs[0],vs[1]),sub(vs[2],vs[1]));length=math.sqrt(dot(n,n));n=[v/length for v in n];d=dot(n,vs[0]);ps.append(([F(v) for v in n],F(d)))
                if len(ps)>=4 and not excluded:cells.append((text.count('\n',0,begin)+1,ps))
            depth-=1
    points=[[F(float(v)) for v in p] for p in route['points']];hits=[]
    for index,(a,b) in enumerate(zip(points,points[1:])):
        delta=sub(b,a)
        for line,ps in cells:
            lo=F(0);hi=F(1)
            for n,d in ps:
                value=dot(n,a)-d;slope=dot(n,delta)
                if not slope:
                    if value>0:hi=F(-1);break
                elif slope>0:hi=min(hi,-value/slope)
                else:lo=max(lo,-value/slope)
                if hi<lo:break
            if hi>=lo:hits.append(dict(segment=index,source_line=line,lo=str(lo),hi=str(hi)))
    rows[mode]=dict(map_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_cells=len(cells),segments=len(points)-1,closed_solid_intersections=hits,seconds=time.perf_counter()-start)
    (E/'source-route-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(mode,rows[mode],flush=True)
assert all(not r['closed_solid_intersections'] for r in rows.values())
