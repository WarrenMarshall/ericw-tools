#!/usr/bin/env python3
"""Prepare a debug-stripped Linux artifact, or compare its independent release evidence."""
import argparse,hashlib,json,os,shutil,struct,subprocess,tempfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def output(args):return subprocess.check_output(list(map(str,args)),text=True).strip()
def banner(text):return next(line for line in text.splitlines() if line.startswith('Qartographer qqbsp,'))
def load_artifact(work,kind='development'):
    dev_path=work/'patched-manifest.json'
    dev=json.loads(dev_path.read_text())
    assert sha(Path(dev['binary']))==dev['binary_sha256'],'Development binary changed since build'
    if kind=='development':return dev
    assert kind=='deployment',kind
    m=json.loads((work/'deployment-artifact.json').read_text())
    assert m['artifact_kind']=='deployment' and m['development_sha256']==dev['binary_sha256']
    assert m['development_manifest_sha256']==sha(dev_path),'Deployment artifact belongs to a different build manifest'
    assert sha(Path(m['binary']))==m['binary_sha256'],'Deployment artifact changed since preparation'
    return m

def elf_profile(path):
    """The pinned Linux baseline is ELF64 little-endian x86_64."""
    b=path.read_bytes()
    assert b[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',b,18)[0]==62,'Expected Linux x86_64 ELF'
    off=struct.unpack_from('<Q',b,40)[0];size,count,names=struct.unpack_from('<HHH',b,58)
    assert size==64 and 0<count<65535 and names<count,'Unsupported ELF section table'
    headers=[struct.unpack_from('<IIQQQQIIQQ',b,off+i*size) for i in range(count)]
    strings=b[headers[names][4]:headers[names][4]+headers[names][5]]
    sections={}
    for h in headers:
        name=strings[h[0]:].split(b'\0',1)[0].decode()
        sections[name]={'type':h[1],'flags':h[2],'address':h[3],'bytes':h[5],
            'sha256':None if h[1]==8 else hashlib.sha256(b[h[4]:h[4]+h[5]]).hexdigest()}
    phoff=struct.unpack_from('<Q',b,32)[0];phsize,phcount=struct.unpack_from('<HH',b,54)
    return {'sections':sections,'entry':struct.unpack_from('<Q',b,24)[0],
        'program_headers_sha256':hashlib.sha256(b[phoff:phoff+phsize*phcount]).hexdigest(),
        'debug_bytes':sum(v['bytes'] for k,v in sections.items() if k.startswith(('.debug','.zdebug'))),
        'alloc':{k:v for k,v in sections.items() if v['flags']&2}}

def prepare(work):
    m=load_artifact(work);source=Path(m['binary']);original=m['binary_sha256']
    before=elf_profile(source);assert before['debug_bytes']>0,'Development binary has no embedded DWARF'
    dest=work/'deployment';dest.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='strip-',dir=work) as name:
        stage=Path(name);binary=stage/'qqbsp';shutil.copy2(source,binary)
        command=['strip','--strip-debug',str(binary)]
        subprocess.run(command,check=True)
        after=elf_profile(binary)
        assert after['debug_bytes']==0,'DWARF remains in deployment artifact'
        assert before['alloc']==after['alloc'],'Stripping changed an allocated ELF section'
        assert before['entry']==after['entry'] and before['program_headers_sha256']==after['program_headers_sha256']
        for section in ['.symtab','.dynsym','.eh_frame','.note.gnu.build-id']:assert section in after['sections'],section
        symbols=output(['nm','--defined-only','-P',source])
        assert symbols==output(['nm','--defined-only','-P',binary]),'Defined diagnostic symbols changed'
        for name,want in m['runtime_sha256'].items():
            lib=source.parent/name;assert sha(lib)==want,lib
            shutil.copy2(lib,stage/name)
        identity=subprocess.run([str(binary),'-help'],capture_output=True,text=True)
        assert identity.returncode==0 and banner(identity.stdout)==banner(m['identity'])
        assert sha(source)==original,'Development executable was modified'
        for name in m['runtime_sha256']:shutil.copy2(stage/name,dest/name)
        result={**m,'label':'deployment','artifact_kind':'deployment','binary':str(dest/'qqbsp'),
            'binary_sha256':sha(binary),'identity':identity.stdout,'development_binary':str(source),
            'development_sha256':original,'development_manifest_sha256':sha(work/'patched-manifest.json'),
            'development_bytes':source.stat().st_size,'deployment_bytes':binary.stat().st_size,
            'strip':{'flags':['--strip-debug'],'version':output(['strip','--version']).splitlines()[0],
                'executable_sha256':sha(Path(shutil.which('strip')))},
            'elf':{'before':before,'after':after,'defined_symbols':len(symbols.splitlines()),
                'defined_symbols_sha256':hashlib.sha256(symbols.encode()).hexdigest()}}
        os.replace(binary,dest/'qqbsp')
        result['ldd']=output(['ldd',dest/'qqbsp'])
        assert sha(dest/'qqbsp')==result['binary_sha256']
        (work/'deployment-artifact.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['binary','binary_sha256','development_sha256','development_bytes','deployment_bytes']},indent=2))
    return result

def compare(work,results):
    dev=load_artifact(work);packed=load_artifact(work,'deployment')
    reports={k:json.loads((results/k/'tier-results.json').read_text()) for k in ['development','deployment']}
    for k,m in [('development',dev),('deployment',packed)]:
        r=reports[k]
        assert r['tier']==3 and r['acceptance']=='PASS' and r['artifact_kind']==k
        assert r['binary_sha256']==m['binary_sha256']
        assert r['native']['compiler_sha256']['qqbsp']==m['binary_sha256'] and r['native']['shutdown']=='normal'
    left=results/'development';right=results/'deployment';files={}
    for suffix in ['.map','.bsp']:
        paths={str(p.relative_to(left)) for p in left.rglob('*'+suffix)}
        assert paths=={str(p.relative_to(right)) for p in right.rglob('*'+suffix)},'Artifact fixture sets differ'
        assert paths,'Missing fixture outputs'
        for name in sorted(paths):
            a,b=left/name,right/name
            assert sha(a)==sha(b),('Development/deployment output differs',name)
            files[name]=sha(a)
    assert (left/'identity.txt').read_text()==(right/'identity.txt').read_text(),'Build identity differs'
    for name in ['stock','fixed','ordinary','engine_sha256','pak_sha256']:
        assert reports['development']['native'][name]==reports['deployment']['native'][name],('Native state differs',name)
    result={'acceptance':'PASS','development_sha256':dev['binary_sha256'],'deployment_sha256':packed['binary_sha256'],
        'development_results':str(left),'deployment_results':str(right),'identical_map_and_bsp_sha256':files,
        'native_states_identical':True,'identity_identical':True}
    (results/'artifact-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('operation',choices=['prepare','compare'])
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--results',type=Path)
    a=ap.parse_args()
    if a.operation=='prepare':prepare(a.work.resolve())
    else:
        assert a.results is not None,'--results is required for comparison'
        compare(a.work.resolve(),a.results.resolve())
if __name__=='__main__':main()
