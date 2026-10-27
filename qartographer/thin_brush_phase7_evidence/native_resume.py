from pathlib import Path
import os,subprocess,shutil,json,hashlib,re,time,signal,sys
sys.dont_write_bytecode=True
base=Path('/tmp/qqbsp-phase7');e=base/'evidence/native-ordinary-final'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=base/'evidence/campaign/ordinary-L-room/input.bsp';bsp=e/'ordinary.bsp'
consumers=json.loads((e/'appimage-results.json').read_text())['consumers']
game=e/'game/id1';maps=game/'maps';maps.mkdir(parents=True,exist_ok=True)
shutil.copyfile(bsp,maps/'ordinary.bsp')
id1=Path('/home/warrenmarshall/.local/share/Steam/steamapps/common/Quake/id1')
for n in ['pak0.pak','pak1.pak']:
 if not (game/n).exists():(game/n).symlink_to(id1/n)
lines=['exitstyle 2','volume 0','bgmvolume 0','joystick 0','host_framerate 0.013888889','host_maxfps 72','cl_forwardspeed 100','sv_maxspeed 100','map ordinary']+['wait']*72+['save start','+forward']+['wait']*144+['-forward','save end','echo QQBSP_PHASE7_NATIVE_DONE','quit']
(game/'acceptance.cfg').write_text('\n'.join(lines)+'\n')
engine=Path('/tmp/appimage_extracted_740db85dc4875cfdb26a910527520a99/usr/bin/qrustyquake')
cmd=[str(engine),'-basedir',str(e/'game'),'-window','-width','960','-height','640','-nosound','+exec','acceptance.cfg']
env=os.environ.copy();env['SDL_VIDEODRIVER']='dummy';start=time.monotonic()
with (e/'engine.log').open('w') as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
 try:rc=p.wait(timeout=55)
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5);raise
result=dict(engine_sha256=sha(engine),command=cmd,exit=rc,seconds=time.monotonic()-start,consumers=consumers,compiled_bsp_sha256=sha(source),consumed_bsp_sha256=sha(bsp),states={},acceptance='INCOMPLETE')
(e/'results.json').write_text(json.dumps(result,indent=2)+'\n')
assert rc==0
assert 'QQBSP_PHASE7_NATIVE_DONE' in (e/'engine.log').read_text()
for name in ['start','end']:
 text=(game/(name+'.sav')).read_text();player=next(b for b in re.findall(r'\{[^{}]*\}',text) if '"classname" "player"' in b)
 kv=dict(re.findall(r'"([^"\n]+)" "([^"\n]*)"',player))
 result['states'][name]={k:kv.get(k,'0') for k in ['origin','velocity','movetype','flags','health']}
 result['states'][name]['server_time']=float(text.splitlines()[20])
a,b=[list(map(float,result['states'][n]['origin'].split())) for n in ['start','end']]
assert b[0]-a[0]>15 and -33<b[0]<-31,(a,b)
assert abs(b[1]+96)<.1
for state in result['states'].values():
 assert int(float(state['flags']))&512 and float(state['health'])>0 and float(state['movetype'])==3
assert result['states']['end']['server_time']>result['states']['start']['server_time']
sys.path.insert(0,str(base/'source/qartographer'))
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
geometry=brushes((base/'source/testmaps/qbsp_simple_sealed2.map').read_text())
cells=[expanded(g,(16,16,28)) for g in geometry]
result['source_checks']=[]
for label,point,want in [('start',a,False),('end',b,False),('past_wall',[-31,b[1],b[2]],True)]:
 point=(point[0],point[1],point[2]+4)
 margin=c.margin(point,cells);assert (margin<0)==want,(label,margin)
 result['source_checks'].append(dict(name=label,oracle_point=point,source_margin=margin,solid=want))
result['acceptance']='PASS';(e/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
