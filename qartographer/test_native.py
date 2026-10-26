"""Native-process acceptance failures must never become saved-state PASS."""
import json,signal,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
import native

class NativeProcessTests(unittest.TestCase):
    def run_failure(self,timeout):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);id1=root/'assets';id1.mkdir()
            for name in ['pak0.pak','pak1.pak']:(id1/name).write_bytes(b'test placeholder')
            ordinary=root/'ordinary.bsp';ordinary.write_bytes(b'test placeholder')
            out=root/'run'
            proc=Mock(pid=4321,returncode=-9 if timeout else 2)
            proc.wait.side_effect=[subprocess.TimeoutExpired('test engine',55),-9] if timeout else [2]
            compiled=subprocess.CompletedProcess([],0,'','')
            with patch.object(native.subprocess,'run',return_value=compiled),patch.object(native.subprocess,'Popen',return_value=proc),patch.object(native.os,'killpg') as kill:
                with self.assertRaises((RuntimeError,AssertionError)):
                    native.run_native(root/'stock',root/'fixed',root/'engine',id1,out,ordinary)
            result=json.loads((out/'process.json').read_text())
            self.assertEqual(result['acceptance'],'INCOMPLETE')
            self.assertEqual(result['timeout'],timeout)
            self.assertFalse((out/'results.json').exists())
            if timeout:kill.assert_called_once_with(4321,signal.SIGKILL)
            else:kill.assert_not_called()

    def test_timeout_kills_group_and_rejects_acceptance(self):self.run_failure(True)
    def test_nonzero_exit_rejects_acceptance(self):self.run_failure(False)

if __name__=='__main__':unittest.main()
