#!/usr/bin/env python3
"""Fresh matched RollerSpline native movement in a private game directory."""
import hashlib,json,os,re,signal,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def kv(s):return dict(re.findall(r'"([^"\n]+)" "([^"\n]*)"',s))
def player(s):return next(b for b in re.findall(r'\{[^{}]*\}',s) if kv(b).get('classname')=='player')
def run_native(stock,fixed,engine,id1,out,ordinary):
    game=out/'id1';maps=game/'maps';maps.mkdir(parents=True)
    for name in ['pak0.pak','pak1.pak']:
        source=(id1/name).resolve();assert source.is_file(),source
        (game/name).symlink_to(source)
    seed=(HERE/'fixtures/roller-seed.sav').read_text();body=player(seed)
    v=kv(body);v.update(origin='-1400 -1664 180',oldorigin='-1400 -1664 180',velocity='0 0 0',angles='0 90 0',v_angle='0 90 0',fixangle='1',health='10000',movetype='3',groundentity='0',flags='4104')
    replacement='{\n'+''.join(f'"{k}" "{val}"\n' for k,val in v.items())+'}'
    lines=['volume 0','bgmvolume 0','joystick 0','host_framerate 0.013888889','host_maxfps 72','cl_forwardspeed 100','sv_maxspeed 100']
    for label,binary in [('stock',stock),('fixed',fixed)]:
        p=maps/(label+'.map')
        p.write_text((HERE/'fixtures/roller-direct.map').read_text()+'\n{\n"classname" "info_player_start"\n"origin" "-1400 -1664 180"\n"angle" "90"\n}\n')
        r=subprocess.run([str(binary),'-bsp2','-notex','-nopercent',str(p)],capture_output=True,text=True)
        (out/(label+'-compile.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
        (game/(label+'_seed.sav')).write_text(seed.replace(body,replacement).replace('\nrouted\n','\n'+label+'\n',1))
        lines+=['-forward','load '+label+'_seed','wait','save '+label+'_start','+forward']+['wait']*144+['-forward','save '+label+'_end']
    import shutil
    shutil.copyfile(ordinary,maps/'ordinary.bsp')
    lines+=['map ordinary']+['wait']*72+['save ordinary_start','quit']
    (game/'acceptance.cfg').write_text('\n'.join(lines)+'\n')
    cmd=[str(engine),'-basedir',str(out),'-window','-width','960','-height','640','-nosound','+exec','acceptance.cfg']
    shutdown='normal'
    with (out/'engine.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:assert proc.wait(timeout=55)==0,'Engine failed'
        except subprocess.TimeoutExpired:
            # Some local engine builds hang in shutdown after saving all states.
            # Missing/incomplete states still fail below; completed movement does
            # not become a collision failure because teardown stalls.
            os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
            shutdown='forced cleanup after timeout; all state assertions still required'
    return validate_saved(stock,fixed,engine,id1,out,cmd,shutdown)

def validate_saved(stock,fixed,engine,id1,out,cmd=None,shutdown=None):
    game=out/'id1'
    result={'compiler_sha256':{'pristine':sha(stock),'qqbsp':sha(fixed)},'shutdown':shutdown,'engine':str(engine),'engine_sha256':sha(engine),'command':cmd,'pak_sha256':{n:sha(id1/n) for n in ['pak0.pak','pak1.pak']}}
    for label in ['stock','fixed']:
        states={}
        for stage in ['start','end']:
            data=kv(player((game/(label+'_'+stage+'.sav')).read_text()))
            states[stage]={k:data.get(k,'0') for k in ['origin','velocity','movetype','flags']}
        result[label]=states
    start=result['fixed']['start'];end=result['fixed']['end']
    assert start['origin']==result['stock']['start']['origin'],'Unmatched native start'
    a,b=[list(map(float,s['origin'].split())) for s in [start,end]]
    assert b[1]-a[1]>100 and b[2]>130,(a,b)
    assert int(float(end['flags']))&512,'Missing grounded flag'
    assert float(end['movetype'])==3,'Not ordinary WALK movement'
    assert result['stock']['end']['origin']==result['stock']['start']['origin'],'Stock negative control changed; review'
    ordinary_state=kv(player((game/'ordinary_start.sav').read_text()))
    assert ordinary_state.get('movetype')=='3.000000'
    result['ordinary']={k:ordinary_state.get(k) for k in ['origin','movetype','flags']}
    result['acceptance']='PASS'
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
