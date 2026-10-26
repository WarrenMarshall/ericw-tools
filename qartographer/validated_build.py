#!/usr/bin/env python3
"""Normal local workflow: build -> validate -> deploy -> verify."""
import argparse,subprocess,sys
from pathlib import Path
from deploy import DEFAULT
HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--results',type=Path,required=True)
    p.add_argument('--destination',type=Path)
    a=p.parse_args();work=a.work.resolve()
    def run(*args):subprocess.run([sys.executable,*map(str,args)],check=True)
    # The pristine snapshot is immutable; reuse only if its manifest and binary
    # still match the lock. build.py rejects overwriting an existing snapshot.
    import hashlib,json
    manifest=work/'pristine-manifest.json'
    if manifest.exists():
        m=json.loads(manifest.read_text())
        assert m['lock']==json.loads((HERE/'baseline.json').read_text()),'Pristine lock changed; use a new work directory'
        assert hashlib.sha256(Path(m['binary']).read_bytes()).hexdigest()==m['binary_sha256']
    else:run(HERE/'build.py','--work',work,'--pristine')
    run(HERE/'build.py','--work',work)
    run(HERE/'regress.py',work/'pristine-build/qbsp/qbsp',work/'patched-build/qbsp/qqbsp',a.results,'--full')
    args=[HERE/'deploy.py','--work',work,'--results',a.results]
    if a.destination:args+=['--destination',a.destination]
    run(*args)
if __name__=='__main__':main()
