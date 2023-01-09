"""
Unify ipynb format

Input
=====
    * first commit
    * last commit
    * temporary branch name

Result
======
    * temporary branch with all ipynb files in the unified format
    * remove all hash info

"""

import json
import pathlib
import tempfile
import subprocess


def process_ipynb(src_path:pathlib.Path):
    """
    rewrite ipynb file using `jupyter nbconver --to notebook`
    """
    assert src_path.exists()
    assert src_path.is_file()
    assert src_path.suffix == '.ipynb'

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        src_after_ipynb_path = tmpdir / (src_path.name)

        remove_colab_button(src_path, src_after_ipynb_path)

        subprocess.run(['jupyter', 'nbconvert', "--to", "notebook", str(src_after_ipynb_path), "--output", str(src_path)])


def verify_processed_ipynb__without_colab_links(src_before_ipynb_path:pathlib.Path, dest_before_ipynb_path:pathlib.Path) -> bool:
    """
    After removing the possible top link,
    verify that the processed ipynb is the equivalent to the original
    """
    assert src_before_ipynb_path.exists()
    assert src_before_ipynb_path.is_file()
    assert src_before_ipynb_path.suffix == '.ipynb'

    assert dest_before_ipynb_path.exists()
    assert dest_before_ipynb_path.is_file()
    assert dest_before_ipynb_path.suffix == '.ipynb'

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        src_after_ipynb_path = tmpdir / (src_before_ipynb_path.name)
        dest_after_ipynb_path = tmpdir / (dest_before_ipynb_path.name)

        remove_colab_button(src_before_ipynb_path, src_after_ipynb_path)
        remove_colab_button(dest_before_ipynb_path, dest_after_ipynb_path)

        result = verify_processed_ipynb(src_after_ipynb_path, dest_after_ipynb_path)

    return result


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


def remove_colab_button(src_ipynb_path:pathlib.Path, dest_ipynb_path:pathlib.Path):
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    ipynb_json = json.loads(src_ipynb_path.read_text())

    assert 'cells' in ipynb_json
    assert isinstance(ipynb_json['cells'], list)
    assert len(ipynb_json['cells']) > 0

    link_text = "https://colab.research.google.com/github/"

    if ipynb_json['cells'][0]['cell_type'] == 'markdown':
        if link_text in ipynb_json['cells'][0]['source'][0]:
            ipynb_json['cells'].pop(0)

    with dest_ipynb_path.open('w') as f:
        json.dump(ipynb_json, f)
