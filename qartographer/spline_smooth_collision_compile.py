#!/usr/bin/env python3
"""Independent BSP2 traversal and MAP/actor support oracle.
Extracted unchanged algorithms from Qartographer's collision investigation;
source revision is pinned in baseline.json. This is a library, not a runner.
"""
import struct,math,pathlib

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):
 l=math.sqrt(dot(a,a));return tuple(x/l for x in a) if l>1e-8 else None
def quake(p):return (p[0],-p[2],p[1])
class BSP:
 def __init__(self,path):
  self.b=pathlib.Path(path).read_bytes();assert self.b[:4]==b'BSP2'
  self.l=[struct.unpack_from('<ii',self.b,4+i*8) for i in range(15)]
 def i(self,at):return struct.unpack_from('<i',self.b,at)[0]
 def head(self,model,hull):return self.i(self.l[14][0]+64*model+36+4*hull)
 def contents(self,p,model=0,hull=1):
  n=self.head(model,hull)
  while n>=0:
   at=self.l[5 if hull==0 else 9][0]+n*(44 if hull==0 else 12)
   plane=self.l[1][0]+self.i(at)*20
   a,b,c,d=struct.unpack_from('<4f',self.b,plane)
   n=self.i(at+(4 if a*p[0]+b*p[1]+c*p[2]>=d else 8))
  return self.i(self.l[10][0]+(-1-n)*44) if hull==0 else n
 def models(self):return self.l[14][1]//64

def supports(faces,extents=(0,0,0)):
 vertices=[quake(v) for f in faces for v in f['v']];center=tuple(sum(v[i] for v in vertices)/len(vertices) for i in range(3));ns=[]
 for f in faces:
  vs=[quake(v) for v in f['v']];n=norm(cross(sub(vs[1],vs[0]),sub(vs[2],vs[0])))
  if dot(n,sub(center,vs[0]))>0:n=tuple(-v for v in n)
  ns.append(n)
  for a,b in zip(vs,vs[1:]+vs[:1]):
   for axis in [(1,0,0),(0,1,0),(0,0,1)]:
    n=norm(cross(sub(b,a),axis))
    if n:
     ds=[dot(n,v) for v in vertices];d=dot(n,a)
     if max(ds)-d<.001:ns.append(n)
     if d-min(ds)<.001:ns.append(tuple(-v for v in n))
 ns.extend([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)])
 return [(n,max(dot(n,v) for v in vertices)+sum(abs(n[i])*extents[i] for i in range(3))) for n in ns]

def halton(index,base):
 value=0;fraction=1/base
 while index:
  value+=fraction*(index%base);index//=base;fraction/=base
 return value

def margin(point,cells):return min(max(dot(n,point)-d for n,d in cell) for cell in cells)

