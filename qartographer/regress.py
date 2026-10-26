#!/usr/bin/env python3
"""Assert failing-before/passing-after P1 evidence, using disposable MAP copies.
Usage: regress.py PRISTINE_QBSP QQBSP OUTPUT [--full]
"""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
LOCK=json.loads((HERE/'baseline.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def invoke(cmd,log):
    r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
    log.write_text(r.stdout+r.stderr)
    return r.returncode

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pristine',type=Path);p.add_argument('qqbsp',type=Path);p.add_argument('output',type=Path);p.add_argument('--full',action='store_true')
    a=p.parse_args();a.output=a.output.resolve()
    assert not a.output.exists(),'Choose a new output directory; never overwrite evidence'
    a.output.mkdir(parents=True)
    for name,want in LOCK['fixtures'].items():assert sha(HERE/'fixtures'/name)==want,name
    summary={}
    for label,binary in [('pristine',a.pristine.resolve()),('patched',a.qqbsp.resolve())]:
        d=a.output/label;d.mkdir()
        identity=subprocess.run([str(binary),'-help'],capture_output=True,text=True)
        (d/'identity.txt').write_text(identity.stdout+identity.stderr)
        if label=='patched':assert 'Qartographer qqbsp,' in identity.stdout and 'patches=P1' in identity.stdout
        reduced=d/'reduced'
        rc=invoke([sys.executable,HERE/'wildspline_bsp_collision_compile.py',binary,reduced],d/'reduced.log')
        data=json.loads((reduced/'results.json').read_text())
        count=len(data['failures'])
        assert (rc!=0 and count>0) if label=='pristine' else (rc==0 and count==0),(label,'reduced',rc,count)
        roller=d/'roller'
        assert invoke([sys.executable,HERE/'direct_probe.py',binary,roller],d/'roller.log')==0
        roll=json.loads((roller/'results.json').read_text())
        counts={k:{h:len(v['failures']) for h,v in r['hulls'].items()} for k,r in roll.items()}
        for mode,hulls in counts.items():
            assert hulls['0']==0,(label,mode,hulls)
            assert all(hulls[h]>0 if label=='pristine' else hulls[h]==0 for h in ['1','2']),(label,mode,hulls)
        summary[label]={'binary':str(binary),'sha256':sha(binary),'reduced_failures':count,'reduced_hulls':data['hulls'],'roller_failures':counts}
        if a.full:
            full=d/'full';full.mkdir()
            for name in ['full-on.map','full-off.map','full-geometry.json']:shutil.copyfile(HERE/'fixtures'/name,full/name)
            for stem in ['full-on','full-off']:
                assert invoke([binary,'-chopfragment','-bsp2','-notex','-nopercent',full/(stem+'.map')],full/(stem+'-compile.log'))==0
            rc=invoke([sys.executable,HERE/'full_oracle.py',binary,full],d/'full-oracle.log')
            failures=json.loads((full/'oracle-failures.json').read_text())
            assert (rc!=0 and len(failures)>0) if label=='pristine' else (rc==0 and not failures),(label,rc,failures[:10])
            summary[label]['full_failures']=len(failures)
            summary[label]['full_counts']=json.loads((full/'full-counts.json').read_text())
        summary[label]['artifacts']={str(f.relative_to(d)):sha(f) for f in sorted(d.rglob('*')) if f.is_file() and f.suffix in ['.map','.bsp']}
        (a.output/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    summary['acceptance']='PASS'
    summary['full']=a.full
    (a.output/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    print('P1 failing-before/passing-after regression PASS')
if __name__=='__main__':main()
