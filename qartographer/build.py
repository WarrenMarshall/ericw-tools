#!/usr/bin/env python3
"""Pinned Linux build. Requires GCC 13.3, CMake 3.28.3 and Ninja 1.11.1.
No installation; all downloads, outputs and pristine source stay in --work.
"""
import argparse, hashlib, json, os, shutil, subprocess, tarfile, urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
LOCK=json.loads((HERE/'baseline.json').read_text())
def run(args, **kwargs):
    subprocess.run([str(x) for x in args],check=True,**kwargs)
def output(args):
    return subprocess.check_output([str(x) for x in args],text=True).strip()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--pristine',action='store_true')
    ap.add_argument('--jobs',default='6')
    a=ap.parse_args();a.work=a.work.resolve();a.work.mkdir(parents=True,exist_ok=True)
    versions={'c++':output(['c++','-dumpfullversion']),'cmake':output(['cmake','--version']).splitlines()[0],'ninja':output(['ninja','--version']),'ld':output(['ld','--version']).splitlines()[0]}
    assert versions['c++']=='13.3.0',versions
    assert versions['cmake']=='cmake version 3.28.3',versions
    assert versions['ninja']=='1.11.1',versions
    for name,rev in LOCK['submodules'].items():
        assert output(['git','-C',ROOT/'3rdparty'/name,'rev-parse','HEAD'])==rev,name
        assert not output(['git','-C',ROOT/'3rdparty'/name,'status','--porcelain']),name
    deps=a.work/'deps';deps.mkdir(exist_ok=True)
    for name,entry in LOCK['archives'].items():
        archive=deps/(name+'.archive')
        if not archive.exists():
            urllib.request.urlretrieve(entry['url'],archive)
        assert sha(archive)==entry['sha256'],archive
        dest=deps/name
        if not dest.exists():
            dest.mkdir()
            with tarfile.open(archive) as tf: tf.extractall(dest,filter='data')
    gtest=deps/'googletest'
    if not gtest.exists(): run(['git','clone','https://github.com/google/googletest.git',gtest])
    run(['git','-C',gtest,'checkout','--detach',LOCK['googletest']])
    assert not output(['git','-C',gtest,'status','--porcelain'])
    source=ROOT;target='qqbsp';label='patched'
    if a.pristine:
        source=a.work/'pristine-source';target='qbsp';label='pristine'
        assert not source.exists(),'Use a new work directory for a new pristine source snapshot'
        source.mkdir()
        def extract(repo,revision,dest):
            data=subprocess.check_output(['git','-C',str(repo),'archive',revision])
            archive=a.work/'source.tar';archive.write_bytes(data)
            with tarfile.open(archive) as tf:tf.extractall(dest,filter='data')
            archive.unlink()
        extract(ROOT,LOCK['upstream'],source)
        for name,rev in LOCK['submodules'].items():extract(ROOT/'3rdparty'/name,rev,source/'3rdparty'/name)
    else:
        run(['git','-C',ROOT,'merge-base','--is-ancestor',LOCK['p1_commit'],'HEAD'])
    build=a.work/(label+'-build')
    prefix=f"{deps}/tbb/oneapi-tbb-2021.11.0/lib/cmake/tbb;{deps}/embree/lib/cmake/embree-4.4.0"
    # Embree archive is rooted directly at lib/, unlike the TBB archive.
    env=dict(os.environ,GITHUB_REF_NAME='2.0.0-alpha10')
    configure=['cmake','-S',source,'-B',build,'-G','Ninja','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DCMAKE_C_COMPILER=/usr/bin/cc','-DCMAKE_CXX_COMPILER=/usr/bin/c++','-DDISABLE_TESTS=ON','-DDISABLE_DOCS=ON','-DENABLE_LIGHTPREVIEW=OFF',f'-DCMAKE_PREFIX_PATH={prefix}',f'-DFETCHCONTENT_SOURCE_DIR_GOOGLETEST={gtest}',f'-DFETCHCONTENT_SOURCE_DIR_JSON={deps}/json/json','-DFETCHCONTENT_FULLY_DISCONNECTED=ON']
    run(configure,env=env);run(['cmake','--build',build,'--target',target,'-j',a.jobs])
    binary=build/'qbsp'/target
    identity=subprocess.run([str(binary),'-help'],capture_output=True,text=True)
    runtime={p.name:sha(p) for p in (build/'qbsp').glob('*.so*') if p.is_file()}
    manifest={'label':label,'upstream':LOCK['upstream'],'downstream':output(['git','-C',ROOT,'rev-parse','HEAD']),'tracked_changes':output(['git','-C',ROOT,'status','--porcelain','--untracked-files=no']),'toolchain':versions,'platform':output(['uname','-a']),'libc':output(['ldd','--version']).splitlines()[0],'lock':LOCK,'configure':list(map(str,configure)),'binary':str(binary),'binary_sha256':sha(binary),'runtime_sha256':runtime,'ldd':output(['ldd',binary]),'identity':identity.stdout,'cache_sha256':sha(build/'CMakeCache.txt')}
    (a.work/(label+'-manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    print(binary)
if __name__=='__main__':main()
