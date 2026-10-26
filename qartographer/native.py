#!/usr/bin/env python3
"""Fresh matched RollerSpline native movement in a private game directory."""
import argparse,hashlib,json,os,re,signal,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
DEFAULT_ENGINE=Path.home()/'.steam/steam/steamapps/common/Quake/qrustyquake'
DEFAULT_ID1=Path.home()/'.local/share/Steam/steamapps/common/Quake/id1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def kv(s):return dict(re.findall(r'"([^"\n]+)" "([^"\n]*)"',s))
def player(s):return next(b for b in re.findall(r'\{[^{}]*\}',s) if kv(b).get('classname')=='player')
def run_native(stock,fixed,engine,id1,out,ordinary):
    assert not out.exists(),'Use a new native output directory'
    game=out/'id1';maps=game/'maps';maps.mkdir(parents=True)
    for name in ['pak0.pak','pak1.pak']:
        source=(id1/name).resolve();assert source.is_file(),source
        (game/name).symlink_to(source)
    seed=(HERE/'fixtures/roller-seed.sav').read_text();body=player(seed)
    v=kv(body);v.update(origin='-1400 -1664 180',oldorigin='-1400 -1664 180',velocity='0 0 0',angles='0 90 0',v_angle='0 90 0',fixangle='1',health='10000',movetype='3',groundentity='0',flags='4104')
    replacement='{\n'+''.join(f'"{k}" "{val}"\n' for k,val in v.items())+'}'
    # QrustyQuake: skip both quit confirmation and the interactive VGA exit screen.
    lines=['exitstyle 2','version','volume 0','bgmvolume 0','joystick 0','host_framerate 0.013888889','host_maxfps 72','cl_forwardspeed 100','sv_maxspeed 100']
    for label,binary in [('stock',stock),('fixed',fixed)]:
        p=maps/(label+'.map')
        p.write_text((HERE/'fixtures/roller-direct.map').read_text()+'\n{\n"classname" "info_player_start"\n"origin" "-1400 -1664 180"\n"angle" "90"\n}\n')
        r=subprocess.run([str(binary),'-bsp2','-notex','-nopercent',str(p)],capture_output=True,text=True)
        (out/(label+'-compile.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
        (game/(label+'_seed.sav')).write_text(seed.replace(body,replacement).replace('\nrouted\n','\n'+label+'\n',1))
        lines+=['-forward','load '+label+'_seed','wait','save '+label+'_start','+forward']+['wait']*144+['-forward','save '+label+'_end']
    import shutil
    shutil.copyfile(ordinary,maps/'ordinary.bsp')
    lines+=['map ordinary']+['wait']*72+['save ordinary_start','echo QQBSP_NATIVE_DONE','quit']
    (game/'acceptance.cfg').write_text('\n'.join(lines)+'\n')
    cmd=[str(engine),'-basedir',str(out),'-window','-width','960','-height','640','-nosound','+exec','acceptance.cfg']
    started=time.monotonic()
    process={'command':cmd,'timeout_seconds':55,'environment':{k:os.environ.get(k) for k in ['SDL_VIDEODRIVER','DISPLAY','WAYLAND_DISPLAY']},'acceptance':'INCOMPLETE'}
    with (out/'engine.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            code=proc.wait(timeout=55)
        except subprocess.TimeoutExpired:
            # A completed save does not make a stuck process an unattended PASS.
            os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
            process.update(exit=proc.returncode,elapsed_seconds=time.monotonic()-started,timeout=True)
            (out/'process.json').write_text(json.dumps(process,indent=2)+'\n')
            raise RuntimeError('Native engine timeout (infrastructure failure); process group killed; saves/logs retained')
    process.update(exit=code,elapsed_seconds=time.monotonic()-started,timeout=False)
    (out/'process.json').write_text(json.dumps(process,indent=2)+'\n')
    assert code==0,('Native engine failed',code,'see '+str(out/'engine.log'))
    assert 'QQBSP_NATIVE_DONE' in (out/'engine.log').read_text(),'Native command script did not finish'
    result=validate_saved(stock,fixed,engine,id1,out,cmd,'normal')
    process['acceptance']='PASS'
    (out/'process.json').write_text(json.dumps(process,indent=2)+'\n')
    return result

def validate_saved(stock,fixed,engine,id1,out,cmd=None,shutdown=None,write_result=True):
    game=out/'id1'
    result={'compiler_sha256':{'pristine':sha(stock),'qqbsp':sha(fixed)},'shutdown':shutdown,'engine':str(engine),'engine_sha256':sha(engine),'command':cmd,'pak_sha256':{n:sha(id1/n) for n in ['pak0.pak','pak1.pak']}}
    for label in ['stock','fixed']:
        states={}
        for stage in ['start','end']:
            data=kv(player((game/(label+'_'+stage+'.sav')).read_text()))
            states[stage]={k:data.get(k,'0') for k in ['origin','velocity','movetype','flags']}
            states[stage]['server_time']=float((game/(label+'_'+stage+'.sav')).read_text().splitlines()[20])
        result[label]=states
    start=result['fixed']['start'];end=result['fixed']['end']
    assert start['origin']==result['stock']['start']['origin'],'Unmatched native start'
    a,b=[list(map(float,s['origin'].split())) for s in [start,end]]
    for label in ['stock','fixed']:
        assert result[label]['end']['server_time']>result[label]['start']['server_time'],'Native server simulation did not advance; investigate engine/harness readiness'
    assert b[1]-a[1]>100 and b[2]>130,(a,b)
    assert int(float(end['flags']))&512,'Missing grounded flag'
    assert float(end['movetype'])==3,'Not ordinary WALK movement'
    assert result['stock']['end']['origin']==result['stock']['start']['origin'],'Stock negative control changed; review'
    ordinary_state=kv(player((game/'ordinary_start.sav').read_text()))
    assert ordinary_state.get('movetype')=='3.000000'
    assert int(float(ordinary_state.get('flags','0')))&512,'Ordinary BSP29 player is not grounded'
    assert float(ordinary_state.get('health','0'))>0,'Ordinary BSP29 player is dead'
    result['ordinary']={k:ordinary_state.get(k) for k in ['origin','movetype','flags']}
    result['acceptance']='PASS'
    if write_result:(out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--artifact',choices=['development','deployment'],default='development')
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--ordinary',type=Path,required=True,help='Existing stock-VIS/LIGHT-consumed ordinary BSP29 fixture')
    ap.add_argument('--engine',type=Path,default=DEFAULT_ENGINE,help='QrustyQuake executable or extracted AppRun')
    ap.add_argument('--id1',type=Path,default=DEFAULT_ID1)
    a=ap.parse_args();work=a.work.resolve()
    from artifacts import load_artifact
    fixed=Path(load_artifact(work,a.artifact)['binary'])
    print(json.dumps(run_native(work/'pristine-build/qbsp/qbsp',fixed,a.engine.resolve(),a.id1.resolve(),a.output.resolve(),a.ordinary.resolve()),indent=2))
if __name__=='__main__':main()
