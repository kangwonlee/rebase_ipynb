"""
Unify ipynb format
"""

import pathlib
import tempfile
import subprocess


def process_ipynb(src_path:pathlib.Path):
    assert src_path.exists()
    assert src_path.is_file()
    assert src_path.suffix == '.ipynb'


def verify_processed_ipynb(src_ipynb_path:pathlib.Path, dest_ipynb_path:pathlib.Path) -> bool:
    """
    Verify that the processed ipynb is the equivalent to the original
    """
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    assert dest_ipynb_path.exists()
    assert dest_ipynb_path.is_file()
    assert dest_ipynb_path.suffix == '.ipynb'

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        src_py_path = tmpdir / (src_ipynb_path.stem + '.py')
        dest_py_path = tmpdir / (dest_ipynb_path.stem + '.py')

        subprocess.run(['jupyter', 'nbconvert', "--to", "python", str(src_ipynb_path), "--output", str(src_py_path)])
        subprocess.run(['jupyter', 'nbconvert', "--to", "python", str(dest_ipynb_path), "--output", str(dest_py_path)])

        assert src_py_path.exists()
        assert src_py_path.is_file()

        assert dest_py_path.exists()
        assert dest_py_path.is_file()

        txt1 = src_py_path.read_text()
        txt2 = dest_py_path.read_text()

    return txt1 == txt2
