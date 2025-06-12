import subprocess
import sys


def test_manage_py_check():
    result = subprocess.run([sys.executable, "manage.py", "check"], capture_output=True)
    assert result.returncode == 0, result.stderr.decode()
