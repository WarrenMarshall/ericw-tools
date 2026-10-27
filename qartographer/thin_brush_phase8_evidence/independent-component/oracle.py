#!/usr/bin/env python3
"""Independent exact oracle: strict Fourier-Motzkin projection, no vertex solves."""
from fractions import Fraction as F
from itertools import combinations

def rows(planes):
    return [(tuple(F(float(v)) for v in p[:3]),F(float(p[3])),False) for p in planes]

def reduce_rows(rs):
    out={}
    for a,b,strict in rs:
        scale=next((abs(v) for v in a if v),None)
        if scale is None:
            if b<0 or (b==0 and strict):return None
            continue
        a=tuple(v/scale for v in a);b/=scale
        if a not in out or b<out[a][0]:out[a]=(b,strict)
        elif b==out[a][0]:out[a]=(b,strict or out[a][1])
    return [(a,b,s) for a,(b,s) in out.items()]

def feasible(rs):
    rs=reduce_rows(rs)
    if rs is None:return False
    while rs and rs[0][0]:
        n=len(rs[0][0]);k=min(range(n),key=lambda k:sum(a[k]>0 for a,_,_ in rs)*sum(a[k]<0 for a,_,_ in rs))
        pos=[r for r in rs if r[0][k]>0];neg=[r for r in rs if r[0][k]<0]
        new=[(a[:k]+a[k+1:],b,s) for a,b,s in rs if not a[k]]
        for a,b,s in pos:
            for c,d,t in neg:
                aa=a[k];cc=-c[k]
                new.append((tuple(a[i]/aa+c[i]/cc for i in range(n) if i!=k),b/aa+d/cc,s or t))
        rs=reduce_rows(new)
        if rs is None:return False
        if len(rs)>200000:raise RuntimeError('oracle projection resource limit')
    return True

def rank(vectors):
    basis={}
    for row in vectors:
        v=list(row)
        for k in range(3):
            if not v[k]:continue
            if k in basis:
                t=v[k];v=[x-t*y for x,y in zip(v,basis[k])]
            else:
                t=v[k];basis[k]=[x/t for x in v];break
    return len(basis)

def dimension(rs):
    if not feasible(rs):return -1
    strict=[(a,b,any(a)) for a,b,s in rs]
    if feasible(strict):return 3
    fixed=[]
    for a,b,_ in rs:
        if any(a) and not feasible(rs+[(a,b,True)]):fixed.append(a)
    return 3-rank(fixed)

def analyze(case):
    rs=rows(case['planes']);out={'dimension':dimension(rs)}
    if 'query' in case:
        q=rows([case['query']])[0];a,b,_=q;op=(tuple(-v for v in a),-b,False)
        out.update(front_dimension=dimension(rs+[op]),back_dimension=dimension(rs+[q]),section_dimension=dimension(rs+[q,op]),strict_front=int(feasible(rs+[(op[0],op[1],True)])),strict_back=int(feasible(rs+[(a,b,True)])))
    if 'point' in case:
        point=[F(float(v)) for v in case['point']]
        out['point_consistent']=all(sum(x*y for x,y in zip(a,point))<=b for a,b,_ in rs)
        if 'query' in case:
            a,b,_=rows([case['query']])[0];v=sum(x*y for x,y in zip(a,point))-b
            out['point_query_sign']=int(v>0)-int(v<0)
    if 'relation' in case:
        a,b=([F(float(v)) for v in p] for p in case['relation']);k=next((i for i in range(3) if a[i]),None)
        if k is None:relation='Degenerate'
        elif not b[k]:relation='Distinct'
        else:
            scale=b[k]/a[k];relation=('Equivalent' if scale>0 else 'Opposing') if all(y==scale*x for x,y in zip(a,b)) else 'Distinct'
        out['relation']=relation
    return out

def range_on_plane(planes,query):
    """Project onto t=n.x-d using exact FME, independently of vertex enumeration."""
    rs=[(a+(F(0),),b,s) for a,b,s in rows(planes)]
    q=rows([query])[0];a,b,_=q
    rs += [(a+(F(-1),),b,False),(tuple(-v for v in a)+(F(1),),-b,False)]
    rs=reduce_rows(rs)
    for remaining in [3,2,1]:
        if rs is None:return None
        k=min(range(remaining),key=lambda k:sum(a[k]>0 for a,_,_ in rs)*sum(a[k]<0 for a,_,_ in rs))
        pos=[r for r in rs if r[0][k]>0];neg=[r for r in rs if r[0][k]<0]
        out=[(a[:k]+a[k+1:],b,s) for a,b,s in rs if not a[k]]
        for a,b,s in pos:
            for c,d,t in neg:
                aa=a[k];cc=-c[k];out.append((tuple(a[i]/aa+c[i]/cc for i in range(len(a)) if i!=k),b/aa+d/cc,s or t))
        rs=reduce_rows(out)
    lo=hi=None
    for a,b,_ in rs:
        if a[0]>0:hi=b/a[0] if hi is None else min(hi,b/a[0])
        elif a[0]<0:lo=b/a[0] if lo is None else max(lo,b/a[0])
    return dict(minimum=str(lo),maximum=str(hi),minimum_float=float(lo) if lo is not None else None,maximum_float=float(hi) if hi is not None else None)
