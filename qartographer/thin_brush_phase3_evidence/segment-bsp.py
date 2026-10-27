import sys,json,struct,pathlib
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer');import spline_smooth_collision_compile as c
r=pathlib.Path('/tmp/qqbsp-phase3');out={}
for mode,v in json.load(open(r/'leak-detour.json')).items():
 p=r/'p1-nofill'/mode/(mode+'.bsp')
 if not p.exists():continue
 b=c.BSP(p);hits=[]
 def rec(n,a,d,lo,hi,k):
  if n<0:
   content=b.i(b.l[10][0]+(-1-n)*44)
   if content==-2 and hi-lo>1e-12:hits.append(dict(segment=k,lo=lo,hi=hi,point=[a[i]+(lo+hi)/2*d[i] for i in range(3)]))
   return
  at=b.l[5][0]+n*44;pl=b.l[1][0]+b.i(at)*20;nx,ny,nz,dist=struct.unpack_from('<4f',b.b,pl);x=c.dot((nx,ny,nz),a)-dist;y=c.dot((nx,ny,nz),d)
  if abs(y)<1e-18:rec(b.i(at+(4 if x>=0 else 8)),a,d,lo,hi,k);return
  t=-x/y
  if t<=lo or t>=hi:rec(b.i(at+(4 if x+((lo+hi)/2)*y>=0 else 8)),a,d,lo,hi,k)
  else:
   rec(b.i(at+(4 if y<0 else 8)),a,d,lo,t,k);rec(b.i(at+(4 if y>0 else 8)),a,d,t,hi,k)
 for k,(a,z) in enumerate(zip(v['points'],v['points'][1:])):rec(b.head(0,0),a,c.sub(z,a),0,1,k)
 out[mode]=hits
print(out);(r/'segment-bsp.json').write_text(json.dumps(out,indent=2))
