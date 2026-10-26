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

def canonical_bsp(path):
    """Only normalize observed nonsemantic ordering; preserve every other byte.

    QBSP's pointer-sorted leaf face lists and stock LIGHT's atomic allocation
    can differ between identical compiler runs. Keep membership multiplicity and
    every per-face lightmap byte, including allocation padding, when reordering.
    """
    b=bytearray(path.read_bytes());version=bytes(b[:4])
    assert version in [b'BSP2',struct.pack('<i',29)],'Unsupported comparison BSP format'
    bsp2=version==b'BSP2'
    lumps=[struct.unpack_from('<ii',b,4+i*8) for i in range(15)]
    leaf_size,mark_size,face_size=(44,4,28) if bsp2 else (28,2,20)
    changes=[]
    lo,ln=lumps[10];mo,mn=lumps[11];fo,fn=lumps[7]
    assert ln%leaf_size==mn%mark_size==fn%face_size==0
    mark_fmt='I' if bsp2 else 'H';cursor=0
    for at in range(lo,lo+ln,leaf_size):
        start,count=struct.unpack_from('<II' if bsp2 else '<HH',b,at+(32 if bsp2 else 20))
        assert start==cursor and start+count<=mn//mark_size,'Noncontiguous leaf face ranges'
        values=list(struct.unpack_from('<'+mark_fmt*count,b,mo+start*mark_size))
        assert all(v<fn//face_size for v in values),'Invalid leaf face index'
        ordered=sorted(values)
        if ordered!=values and 'leaf_face_order' not in changes:changes.append('leaf_face_order')
        struct.pack_into('<'+mark_fmt*count,b,mo+start*mark_size,*ordered)
        cursor+=count
    assert cursor==mn//mark_size,'Unreferenced leaf face records'
    lighto,lightn=lumps[8]
    if lightn:
        fields=[at+face_size-4 for at in range(fo,fo+fn,face_size)]
        offsets=[struct.unpack_from('<i',b,at)[0] for at in fields]
        starts=sorted(o for o in offsets if o>=0)
        assert starts and starts[0]==0 and starts[-1]<lightn and len(starts)==len(set(starts)), 'Unsupported shared/noncontiguous lightmap allocation'
        lights=bytes(b[lighto:lighto+lightn])
        chunks={start:lights[start:(starts[i+1] if i+1<len(starts) else lightn)] for i,start in enumerate(starts)}
        reordered=bytearray()
        for field,offset in zip(fields,offsets):
            if offset<0:continue
            struct.pack_into('<i',b,field,len(reordered));reordered.extend(chunks[offset])
        assert len(reordered)==lightn
        if bytes(reordered)!=lights or [struct.unpack_from('<i',b,f)[0] for f in fields]!=offsets:
            changes.append('lightmap_allocation_order')
        b[lighto:lighto+lightn]=reordered
    return bytes(b),changes

def compare_bsp(a,b):
    left,right=sha(a),sha(b)
    if left==right:return {'byte_identical':True,'development_sha256':left,'deployment_sha256':right}
    ca,na=canonical_bsp(a);cb,nb=canonical_bsp(b)
    assert ca==cb,('BSP semantic/output difference',str(a),str(b))
    return {'byte_identical':False,'development_sha256':left,'deployment_sha256':right,
        'canonical_sha256':hashlib.sha256(ca).hexdigest(),'normalizations':sorted(set(na+nb))}

def compare(work,results):
    dev=load_artifact(work);packed=load_artifact(work,'deployment')
    reports={k:json.loads((results/k/'tier-results.json').read_text()) for k in ['development','deployment']}
    for k,m in [('development',dev),('deployment',packed)]:
        r=reports[k]
        assert r['tier']==3 and r['acceptance']=='PASS' and r['artifact_kind']==k
        assert r['binary_sha256']==m['binary_sha256']
        assert r['native']['compiler_sha256']['qqbsp']==m['binary_sha256'] and r['native']['shutdown']=='normal'
    left=results/'development';right=results/'deployment';maps={};bsps={}
    for suffix in ['.map','.bsp']:
        paths={str(p.relative_to(left)) for p in left.rglob('*'+suffix)}
        assert paths=={str(p.relative_to(right)) for p in right.rglob('*'+suffix)},'Artifact fixture sets differ'
        assert paths,'Missing fixture outputs'
        for name in sorted(paths):
            a,b=left/name,right/name
            if suffix=='.map':
                assert sha(a)==sha(b),('Development/deployment MAP differs',name)
                maps[name]=sha(a)
            else:bsps[name]=compare_bsp(a,b)
    assert (left/'identity.txt').read_text()==(right/'identity.txt').read_text(),'Build identity differs'
    for name in ['stock','fixed','ordinary','engine_sha256','pak_sha256']:
        assert reports['development']['native'][name]==reports['deployment']['native'][name],('Native state differs',name)
    result={'acceptance':'PASS','development_sha256':dev['binary_sha256'],'deployment_sha256':packed['binary_sha256'],
        'development_results':str(left),'deployment_results':str(right),'identical_map_sha256':maps,'bsp_comparison':bsps,
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
