#!/usr/bin/env python3
"""Deploy only a hash-matched compiler with complete passing regression evidence."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
DEFAULT=Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(p):
    env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
    r=subprocess.run([str(p),'-help'],cwd=p.parent,env=env,capture_output=True,text=True)
    assert r.returncode==0,(r.returncode,r.stderr)
    return next(line for line in r.stdout.splitlines() if line.startswith('Qartographer qqbsp;'))
def deploy(work,results,destination):
    manifest=json.loads((work/'patched-manifest.json').read_text())
    tier=json.loads((results/'tier-results.json').read_text())
    assert tier['tier']==3 and tier['acceptance']=='PASS','Tier 3 validation required'
    evidence=json.loads((results/'collision/results.json').read_text())
    assert evidence['acceptance']=='PASS' and evidence['full'] is True,'Full validation required for deployment'
    binary=Path(manifest['binary'])
    expected=manifest['binary_sha256']
    assert sha(binary)==expected==evidence['patched']['sha256']==tier['binary_sha256'],'Binary changed since build/validation'
    assert not manifest['tracked_changes'],'Only clean committed builds may be deployed'
    want=next(line for line in manifest['identity'].splitlines() if line.startswith('Qartographer qqbsp;'))
    assert identity(binary)==want,'Build identity changed'
    assert destination.name=='qqbsp','Destination must be named qqbsp; stock tools are protected'
    assert destination.parent.is_dir(),'Destination directory unavailable'
    assert not destination.is_symlink(),'Refusing to replace a symlink'
    # No runtime libraries are overwritten. Stage and execute beside the existing
    # libraries; a loader/ABI failure leaves the previous qqbsp untouched.
    temp=None;backup=None;replaced=False
    try:
        fd,name=tempfile.mkstemp(prefix='.qqbsp-',dir=destination.parent)
        temp=Path(name)
        with os.fdopen(fd,'wb') as f:
            with binary.open('rb') as source:shutil.copyfileobj(source,f)
            f.flush();os.fsync(f.fileno())
        shutil.copymode(binary,temp)
        assert sha(temp)==expected,'Staged copy hash mismatch'
        assert identity(temp)==want,'Staged executable identity mismatch'
        if destination.exists():
            backup=temp.with_name(temp.name+'-previous')
            os.link(destination,backup)
        os.replace(temp,destination);temp=None;replaced=True
        assert sha(destination)==expected,'Deployed hash mismatch'
        assert identity(destination)==want,'Deployed identity mismatch'
    except Exception:
        if replaced:
            if backup is not None:
                os.replace(backup,destination);backup=None
            else:destination.unlink(missing_ok=True)
        raise
    finally:
        if backup is not None:backup.unlink(missing_ok=True)
        if temp is not None:temp.unlink(missing_ok=True)
    receipt={'destination':str(destination),'sha256':expected,'identity':want,'results':str(results)}
    (work/'deployment.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--results',type=Path,required=True)
    p.add_argument('--destination',type=Path,default=Path(os.environ.get('QQBSP_DEPLOY_PATH',DEFAULT)))
    a=p.parse_args()
    try:deploy(a.work.resolve(),a.results.resolve(),a.destination.absolute())
    except Exception as e:p.exit(1,f'QQBSP deployment FAILED: {e}\n')
if __name__=='__main__':main()
