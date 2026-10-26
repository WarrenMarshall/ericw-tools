"""Packaging must preserve development symbols and bind validation to actual bytes."""
import contextlib,io,json,subprocess,tempfile,unittest
from pathlib import Path
from artifacts import elf_profile,load_artifact,prepare,sha

class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name);src=self.work/'test.cc'
        src.write_text('#include <cstdio>\nint main(){std::puts("Qartographer qqbsp, upstream=test, downstream=test, patches=P1");}\n')
        self.binary=self.work/'development/qqbsp';self.binary.parent.mkdir()
        subprocess.run(['c++','-O2','-g',str(src),'-o',str(self.binary)],check=True)
        self.original=sha(self.binary)
        identity=subprocess.check_output([str(self.binary),'-help'],text=True)
        self.manifest=self.work/'patched-manifest.json'
        self.manifest.write_text(json.dumps({'binary':str(self.binary),'binary_sha256':self.original,'identity':identity,'runtime_sha256':{}}))
        with contextlib.redirect_stdout(io.StringIO()):self.package=prepare(self.work)

    def test_preserves_debug_build_and_loaded_sections(self):
        deployed=Path(self.package['binary'])
        self.assertEqual(sha(self.binary),self.original)
        self.assertGreater(elf_profile(self.binary)['debug_bytes'],0)
        self.assertEqual(elf_profile(deployed)['debug_bytes'],0)
        self.assertEqual(elf_profile(self.binary)['alloc'],elf_profile(deployed)['alloc'])
        self.assertNotEqual(sha(deployed),self.original)
        self.assertLess(deployed.stat().st_size,self.binary.stat().st_size)
        self.assertEqual(load_artifact(self.work,'deployment')['binary_sha256'],sha(deployed))

    def test_rejects_tampered_deployment_artifact(self):
        with Path(self.package['binary']).open('ab') as f:f.write(b'changed')
        with self.assertRaises(AssertionError):load_artifact(self.work,'deployment')

    def test_rejects_stale_development_manifest(self):
        m=json.loads(self.manifest.read_text());m['changed']='new build record'
        self.manifest.write_text(json.dumps(m))
        with self.assertRaises(AssertionError):load_artifact(self.work,'deployment')

if __name__=='__main__':unittest.main()
