import pathlib
import sys

import pytest

proj_folder = pathlib.Path(__file__).parent.parent.absolute()
assert proj_folder.exists(), proj_folder.absolute()
assert proj_folder.is_dir(), proj_folder.absolute()

test_folder = proj_folder / 'tests'
assert test_folder.exists(), test_folder.absolute()
assert test_folder.is_dir(), test_folder.absolute()

sys.path.insert(0,
    str(proj_folder)
)


import rebase_ipynb


def test_verify_processed_ipynb__equal_with_button():
    src_ipynb_path = test_folder / 'eq_colab.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    dest_ipynb_path = test_folder / 'eq_local_with_button.ipynb'
    assert dest_ipynb_path.exists()
    assert dest_ipynb_path.is_file()
    assert dest_ipynb_path.suffix == '.ipynb'

    assert rebase_ipynb.verify_processed_ipynb(src_ipynb_path, dest_ipynb_path)


def test_verify_processed_ipynb__equal_without_button():
    src_ipynb_path = test_folder / 'eq_colab.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    dest_ipynb_path = test_folder / 'eq_local_without_button.ipynb'
    assert dest_ipynb_path.exists()
    assert dest_ipynb_path.is_file()
    assert dest_ipynb_path.suffix == '.ipynb'

    assert rebase_ipynb.verify_processed_ipynb(src_ipynb_path, dest_ipynb_path)


def test_verify_processed_ipynb__not_equal():
    src_ipynb_path = test_folder / 'ne_colab.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    dest_ipynb_path = test_folder / 'eq_local_with_button.ipynb'
    assert dest_ipynb_path.exists()
    assert dest_ipynb_path.is_file()
    assert dest_ipynb_path.suffix == '.ipynb'

    assert not rebase_ipynb.verify_processed_ipynb(src_ipynb_path, dest_ipynb_path)


if '__main__' == __name__:
    pytest.main([__file__])
