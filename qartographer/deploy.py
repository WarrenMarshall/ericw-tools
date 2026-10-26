#!/usr/bin/env python3
"""Deploy only a hash-matched compiler with complete passing regression evidence."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
from artifacts import load_artifact
DEFAULT=Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(p):
    env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
    r=subprocess.run([str(p),'-help'],cwd=p.parent,env=env,capture_output=True,text=True)
    assert r.returncode==0,(r.returncode,r.stderr)
    return next(line for line in r.stdout.splitlines() if line.startswith('Qartographer qqbsp,'))
def archive_debug(work,manifest):
    # Keep matching symbols across later rebuilds and disposable workdir cleanup.
    dev=load_artifact(work)
    assert dev['binary_sha256']==manifest['development_sha256']
    folder=Path(__file__).resolve().parents[1]/'build-symbols'/dev['binary_sha256']
    folder.mkdir(parents=True,exist_ok=True);saved=folder/'qqbsp'
    if not saved.exists():
        fd,name=tempfile.mkstemp(prefix='.qqbsp-',dir=folder)
        os.close(fd);temp=Path(name)
        try:
            shutil.copy2(dev['binary'],temp)
            assert sha(temp)==dev['binary_sha256'],'Debug archive copy mismatch'
            os.replace(temp,saved)
        finally:temp.unlink(missing_ok=True)
    assert sha(saved)==dev['binary_sha256'],'Existing debug archive mismatch'
    (folder/'development-build.json').write_text(json.dumps(dev,indent=2)+'\n')
    return saved

def deploy(work,results,destination):
    manifest=load_artifact(work,'deployment')
    tier=json.loads((results/'deployment/tier-results.json').read_text())
    assert tier['artifact_kind']=='deployment','Deployment-artifact validation required'
    assert tier['tier']==3 and tier['acceptance']=='PASS','Tier 3 validation required'
    evidence=json.loads((results/'deployment/collision/results.json').read_text())
    assert evidence['acceptance']=='PASS' and evidence['full'] is True,'Full validation required for deployment'
    development=json.loads((results/'development/tier-results.json').read_text())
    comparison=json.loads((results/'artifact-comparison.json').read_text())
    assert development['tier']==3 and development['acceptance']=='PASS' and development['artifact_kind']=='development'
    assert development['binary_sha256']==manifest['development_sha256']
    assert comparison['acceptance']=='PASS' and comparison['development_sha256']==manifest['development_sha256']
    assert comparison['deployment_sha256']==manifest['binary_sha256'],'Artifact equivalence validation required'
    binary=Path(manifest['binary'])
    expected=manifest['binary_sha256']
    assert sha(binary)==expected==evidence['patched']['sha256']==tier['binary_sha256'],'Binary changed since build/validation'
    assert not manifest['tracked_changes'],'Only clean committed builds may be deployed'
    want=next(line for line in manifest['identity'].splitlines() if line.startswith('Qartographer qqbsp,'))
    assert identity(binary)==want,'Build identity changed'
    assert destination.name=='qqbsp','Destination must be named qqbsp; stock tools are protected'
    assert destination.parent.is_dir(),'Destination directory unavailable'
    assert not destination.is_symlink(),'Refusing to replace a symlink'
    # No runtime libraries are overwritten. Stage and execute beside the existing
    # libraries; a loader/ABI failure leaves the previous qqbsp untouched.
    debug_archive=archive_debug(work,manifest)
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
        receipt={'destination':str(destination),'artifact_kind':'deployment','source_artifact':str(binary),'sha256':expected,'development_sha256':manifest['development_sha256'],'debug_archive':str(debug_archive),'deployment_artifact_manifest_sha256':sha(work/'deployment-artifact.json'),'identity':want,'results':str(results)}
        (work/'deployment.json').write_text(json.dumps(receipt,indent=2)+'\n')
    except Exception:
        if replaced:
            if backup is not None:
                os.replace(backup,destination);backup=None
            else:destination.unlink(missing_ok=True)
        raise
    finally:
        if backup is not None:backup.unlink(missing_ok=True)
        if temp is not None:temp.unlink(missing_ok=True)
    print(json.dumps(receipt,indent=2))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--results',type=Path,required=True)
    p.add_argument('--destination',type=Path,default=Path(os.environ.get('QQBSP_DEPLOY_PATH',DEFAULT)))
    a=p.parse_args()
    try:deploy(a.work.resolve(),a.results.resolve(),a.destination.absolute())
    except Exception as e:p.exit(1,f'QQBSP deployment FAILED: {e}\n')
if __name__=='__main__':main()
