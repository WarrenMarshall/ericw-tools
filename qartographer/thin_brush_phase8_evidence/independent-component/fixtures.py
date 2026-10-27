#!/usr/bin/env python3
import json,re,math,random,hashlib
from pathlib import Path
R=Path('/home/warrenmarshall/dev/ericw-tools');B=Path('/tmp/qqbsp-phase6');E=B/'evidence'

def box(lo,hi):
    ps=[]
    for i in range(3):
        for s,v in [(-1,-lo[i]),(1,hi[i])]:
            p=[0.,0.,0.,float(v)];p[i]=s;ps.append(p)
    return ps

def preserved(name):
    p=R/'qartographer/thin_brush_phase5_evidence'/name/'stdout.log';text=p.read_text()
    def plane(m):return list(map(float,m[1].split()))+[float(m[2])]
    query=plane(re.search(r'PHASE5_REJECT partition=\d+ plane=\{normal: ([^,]+), dist: ([^}]+)',text))
    ps=[plane(m) for m in re.finditer(r'PHASE5_SUPPORT id=\d+ plane=\{normal: ([^,]+), dist: ([^}]+)',text)]
    vs=[list(map(float,m.split())) for m in re.findall(r'\(([-+\d.eE ]+)\)',text[text.index('PHASE5_REJECT'):])]
    point=max(vs,key=lambda v:sum(a*b for a,b in zip(query,v))-query[3])
    return ps,query,point,dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

cases=[]
def add(name,planes,query=None,point=None,expected=None,**extra):
    c=dict(name=name,planes=planes,**extra)
    if query is not None:c['query']=query
    if point is not None:c['point']=point
    if expected is not None:c['established']=expected
    cases.append(c)

add('A-hull2-front',box([-1360.000488281,-1488,172.03125],[-1280,-1392,322.5093526806837]),[1.,0.,0.,-1280.000244141],[-1280.0001220705,-1440,236.73692674130805],{'dimension':3,'front_dimension':3,'section_dimension':2,'point_consistent':True})
cases.append(json.loads((E/'actor-actual-region.json').read_text()))
f=json.loads((R/'qartographer/thin_brush_phase5_evidence/phase5-witness.json').read_text());ps=[p['p'] for p in f['region']]+[p['p'] for p in f['cap']['ancestor_constraints']]
add('B-narrow-quadrilateral',ps,f['partition'],expected={'dimension':3,'section_dimension':2})
add('C-sky-roof-gap',box([-1728,-1583,509],[-1727.99987793,-1581,511]),[1.,0.,0.,-1727.999938965],[-1727.999938965,-1582,510],{'dimension':3,'front_dimension':3,'back_dimension':3,'section_dimension':2},source_boundaries=[-1728,-1727.99987793])
for name,folder in [('D-halloween-rounded-extent','candidate-halloween-off'),('E-p1-rounded-extent','candidate-p1-reduced')]:
    ps,q,p,identity=preserved(folder);add(name,ps,q,p,identity=identity)
portal=json.loads((E/'portal-site.json').read_text());add('F-rotated-portal',portal['planes'],portal['query'],winding=portal['winding'])
for filename,name in [('base-winding-site.json','F-base-winding'),('make-portal-site.json','F-make-portal')]:
    site=json.loads((E/filename).read_text());add(name,site['planes'],site['query'])
base=box([-1,-1,-1],[1,1,1]);q=[1.,0.,0.,0.]
add('ordinary-box',base,q,[0,0,0],{'dimension':3,'front_dimension':3,'back_dimension':3,'section_dimension':2})
for name,extra,dim in [('face',[[1.,0.,0.,-1.]],2),('edge',[[1.,0.,0.,-1.],[0.,1.,0.,-1.]],1),('point',[[1.,0.,0.,-1.],[0.,1.,0.,-1.],[0.,0.,1.,-1.]],0),('empty',[[1.,0.,0.,-2.]],-1)]:
    add(name+'-contact' if name!='empty' else name,base+extra,q,expected={'dimension':dim})
for label,delta in [('binary-2^-45',2.**-45),('binary-2^-500',2.**-500),('min-subnormal',2.**-1074)]:
    add(label,box([0,0,0],[delta,1,1]),[1.,0.,0.,0.],expected={'dimension':3,'front_dimension':3,'back_dimension':2,'section_dimension':2})
add('large-coordinate-ulp',box([2.**40,0,0],[math.nextafter(2.**40,math.inf),1,1]),[1.,0.,0.,2.**40],expected={'dimension':3,'front_dimension':3})
add('nearly-parallel',base+[[1.,2.**-50,0.,.5],[-1.,-2.**-50,0.,-.5+2.**-48]],[1.,2.**-50,0.,.5-2.**-49],expected={'dimension':3,'section_dimension':2})
# Invertible rational-coordinate change: u=x+y, v=y+z, w=x+z; integer coefficients remain exact.
rot=[[1.,1.,0.,1.],[-1.,-1.,0.,1.],[0.,1.,1.,1.],[0.,-1.,-1.,1.],[1.,0.,1.,1.],[-1.,0.,-1.,1.]]
add('transformed-box',rot,[1.,1.,0.,0.],expected={'dimension':3,'section_dimension':2})
add('rotated-translated',[[*p[:3],p[3]+p[0]*1024+p[1]*(-2048)+p[2]*512] for p in rot],[1.,1.,0.,-1024],expected={'dimension':3,'section_dimension':2})
add('coincident',base+[[2.,0.,0.,2.]],q,relation=[[1.,0.,0.,1.],[2.,0.,0.,2.]],expected={'dimension':3,'relation':'Equivalent'})
add('opposing',base+[[1.,0.,0.,0.],[-2.,0.,0.,0.]],q,relation=[[1.,0.,0.,0.],[-2.,0.,0.,0.]],expected={'dimension':2,'relation':'Opposing'})
add('not-approximately-equivalent',base,q,relation=[[1.,0.,0.,1.],[1.,0.,0.,math.nextafter(1.,math.inf)]],expected={'dimension':3,'relation':'Distinct'})
add('zero-redundant',base+[[0.,0.,0.,0.],[0.,0.,0.,1.]],q,expected={'dimension':3})
add('zero-inconsistent',base+[[0.,0.,0.,-1.]],q,expected={'dimension':-1})
add('unbounded-explicit-limit',[[1.,0.,0.,1.]],expected={'dimension':3},component_expected={'dimension':-2})
add('overflow-filter',box([0.,0.,0.],[1e200,1e200,1e200]),[1e200,0.,0.,1e200],expected={'dimension':3,'section_dimension':2})
# Reordering and redundant identities must preserve the authoritative model.
original=list(cases)
rng=random.Random(6006)
for c in original:
    if c['name']=='unbounded-explicit-limit':continue
    for variant in ['reverse','shuffle-duplicates']:
        cc=json.loads(json.dumps(c));cc['name']=c['name']+'-'+variant;cc['parent']=c['name'];cc.pop('established',None)
        if variant=='reverse':cc['planes'].reverse()
        else:rng.shuffle(cc['planes']);cc['planes']+=cc['planes'][:min(3,len(cc['planes']))]
        cases.append(cc)
# Depth scaling has known redundant supports enclosing the ordinary unit box.
for depth in [0,8,16,32,64]:
    ps=base+[[1.,float(i+1),1.,float(10*(i+2))] for i in range(depth)]
    add('depth-'+str(depth),ps,q,expected={'dimension':3,'section_dimension':2})
(E/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
print(len(cases),'cases')
