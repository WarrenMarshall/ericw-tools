#!/usr/bin/env python3
"""Executable policy study, not compiler code. No size-based deletion rule.
A merge means removing an internal separator of the ENTIRE convex parent,
retaining its external supports and ports. It never means dropping a fragment.
"""
from fractions import Fraction as F
from pathlib import Path
import json,struct,sys,itertools
from oracle import rows,feasible,dimension
E=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/qqbsp-phase6/evidence');R=Path('/home/warrenmarshall/dev/ericw-tools')

def box(lo,hi):
    result=[]
    for k in range(3):
        for sign,d in [(-1,-lo[k]),(1,hi[k])]:
            p=[0.,0.,0.,d];p[k]=sign;result.append(p)
    return result

def constant_contents(region,brushes,complete=True,budget=10000):
    if not complete:return 'Unresolved: incomplete source/ownership scope'
    rr=rows(region)
    if not feasible(rr):return 'EmptyRegion'
    sources=[rows(p) for p in brushes]
    if all(not feasible(rr+b) for b in sources):return 'EMPTY'
    calls=0
    def uncovered(cell,remaining):
        nonlocal calls
        calls+=1
        if calls>budget:raise RuntimeError('coverage budget')
        if not feasible(cell):return False
        if not remaining:return True
        # Outside a closed convex brush is the union of strict opposing supports.
        for a,b,_ in remaining[0]:
            if uncovered(cell+[(tuple(-v for v in a),-b,True)],remaining[1:]):return True
        return False
    try:
        return 'Mixed' if uncovered(rr,sources) else 'SOLID'
    except RuntimeError:return 'Unresolved: coverage budget'

def permit_sibling_merge(region,brushes,external_boundary_and_ports_unchanged,complete=True):
    contents=constant_contents(region,brushes,complete)
    if contents not in ['SOLID','EMPTY']:return dict(action='RetainOrUnresolved',contents=contents)
    if not external_boundary_and_ports_unchanged:return dict(action='RetainOrUnresolved',contents=contents,reason='external occupancy/connectivity transport unproved')
    return dict(action='RemoveInternalSeparator',contents=contents)

def reachability(edges,ports):
    adjacent={}
    for a,b in edges:adjacent.setdefault(a,set()).add(b);adjacent.setdefault(b,set()).add(a)
    out={}
    for p in ports:
        seen={p};todo=[p]
        while todo:
            node=todo.pop()
            for q in adjacent.get(node,()):
                if q not in seen:seen.add(q);todo.append(q)
        out[p]=sorted(seen&set(ports))
    return out

records=[]
def test(name,region,brushes,want,ports=True,complete=True):
    got=permit_sibling_merge(region,brushes,ports,complete);assert got['action']==want,(name,got,want)
    records.append(dict(name=name,result=got))

ulp=struct.unpack('d',struct.pack('d',208.00000000000003))[0]
region=box([208,-1,-1],[209,1,1]);thin=ulp-208
q=[1.,0.,0.,ulp]
assert dimension(rows(region+[q]))==3
assert dimension(rows(region+[[-v for v in q]]))==3
assert dimension(rows(region+[q,[-v for v in q]]))==2
# Both volumetric children may be merged without ever constructing a tiny cap.
test('microscopic-empty-internal-divider',region,[],'RemoveInternalSeparator')
test('microscopic-solid-internal-divider',region,[region],'RemoveInternalSeparator')
test('solid-union-redundant-divider',region,[box([208,-1,-1],[208.5,1,1]),box([208.5,-1,-1],[209,1,1])],'RemoveInternalSeparator')
test('same-contents-with-unproved-ports',region,[],'RetainOrUnresolved',ports=False)
wall=box([208,-1,-1],[ulp,1,1]);corridor=box([207,-1,-1],[209,1,1])
test('float32-collapsed-wall-still-blocks',corridor,[wall],'RetainOrUnresolved')
test('hull2-blocker',box([-1281,-1489,79],[-1279,-1391,393]),[box([-1584.000488281,-1488,80],[-1232,-1392,392])],'RetainOrUnresolved')
test('source-sky-roof-opening',box([-1729,-1,-1],[-1727,1,1]),[box([-1729,-1,-1],[-1728,1,1]),box([-1727.99987793,-1,-1],[-1727,1,1])],'RetainOrUnresolved')
# Exact geometry is known for D, but the full-node source union/port graph is not.
test('D-needs-semantic-context-not-more-digits',region,[],'RetainOrUnresolved',complete=False)

cases=json.loads((E/'cases.json').read_text());byname={c['name']:c for c in cases}
e=byname['E-p1-rounded-extent'];q=e['query'];front=e['planes']+[[ -v for v in q ]];assert dimension(rows(front))==-1
records.append(dict(name='E-empty-child-no-loss-route-back',action='CertifiedEmptyChild'))
f=byname['F-rotated-portal'];section=f['planes']+[f['query'],[-v for v in f['query']]];assert dimension(rows(section))==1
records.append(dict(name='F-omit-edge-only-area-portal',action='CertifiedNoAreaPortal'))

# A local graph quotient proof applies only to a certified constant EMPTY parent
# and unchanged external ports, not to an arbitrary narrow empty/solid strip.
ports=['north','south','east','west'];edges=[('left','right'),('north','left'),('south','left'),('east','right'),('west','right')]
merged=[('parent' if a in ['left','right'] else a,'parent' if b in ['left','right'] else b) for a,b in edges]
assert reachability(edges,ports)==reachability(merged,ports)
# A genuinely solid separating slab cannot be contracted as an empty connector.
separated=[('north','left'),('south','left'),('east','right'),('west','right')]
assert reachability(separated,ports)!=reachability(edges,ports)

float32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
quantized=[]
for name in ['A-hull2-front','A-actual-post-csg-route','B-narrow-quadrilateral','C-sky-roof-gap','D-halloween-rounded-extent','E-p1-rounded-extent','F-rotated-portal']:
    c=byname[name];qc={k:v for k,v in c.items() if k in ['name','planes','query','point']};qc['name']=name+'-binary32-planes';qc['planes']=[[float32(v) for v in p] for p in c['planes']];qc['query']=[float32(v) for v in c['query']];quantized.append(qc)
(E/'bsp-quantized-cases.json').write_text(json.dumps(quantized,indent=2)+'\n')
(E/'practical-policy-results.json').write_text(json.dumps(dict(records=records,internal_divider_width=thin,wall_boundary_float32_equal=float32(208)==float32(ulp),empty_parent_port_reachability_preserved=True,removing_wall_changes_port_reachability=True,policy='No minimum thickness. Only prove redundancy/coverage and unchanged external boundary/ports, or retain/diagnose. Unproved input is not approval to collapse.'),indent=2)+'\n')
print('PASS: safe internal merges, union coverage, withheld topology transport, meaningful thin blockers, gap, empty child and edge portal')
