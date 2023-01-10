import json
import pathlib
import sys
import tempfile

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


def test_verify_processed_ipynb__without_colab_links__equal_with_button():
    src_ipynb_path = test_folder / 'eq_colab.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    dest_ipynb_path = test_folder / 'eq_local_with_button.ipynb'
    assert dest_ipynb_path.exists()
    assert dest_ipynb_path.is_file()
    assert dest_ipynb_path.suffix == '.ipynb'

    assert rebase_ipynb.verify_processed_ipynb__without_colab_links(src_ipynb_path, dest_ipynb_path)


def test_verify_processed_ipynb__without_colab_links__equal_without_button():
    src_ipynb_path = test_folder / 'eq_colab.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    dest_ipynb_path = test_folder / 'eq_local_without_button.ipynb'
    assert dest_ipynb_path.exists()
    assert dest_ipynb_path.is_file()
    assert dest_ipynb_path.suffix == '.ipynb'

    assert rebase_ipynb.verify_processed_ipynb__without_colab_links(src_ipynb_path, dest_ipynb_path)


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


def test_remove_colab_button__eq_local():
    src_ipynb_path = test_folder / 'eq_local_with_button.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    ref_ipynb_path = test_folder / 'eq_local_without_button.ipynb'
    assert ref_ipynb_path.exists()
    assert ref_ipynb_path.is_file()
    assert ref_ipynb_path.suffix == '.ipynb'

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)

        dest_ipynb_path = tmpdir_path / 'eq_local_with_button.ipynb'

        rebase_ipynb.remove_colab_button(src_ipynb_path, dest_ipynb_path)

        assert rebase_ipynb.verify_processed_ipynb(dest_ipynb_path, ref_ipynb_path)


def test_remove_metadata_id__eq_local():
    src_ipynb_path = test_folder / 'eq_local_without_button.ipynb'
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    src_ipynb_json = json.loads(src_ipynb_path.read_text())
    # has hash values?

    result = False
    for cell in src_ipynb_json["cells"]:
        if "metadata" in cell:
            if "id" in cell["metadata"]:
                result = True

    assert result, "no hash values found in source ipynb file"


    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)

        dest_ipynb_path = tmpdir_path / 'eq_local_with_button.ipynb'

        rebase_ipynb.remove_metadata_id(src_ipynb_path, dest_ipynb_path)

        dest_ipynb_json = json.loads(dest_ipynb_path.read_text())

        # still has hash values?
        for cell in dest_ipynb_json["cells"]:
            if "metadata" in cell:
                assert "id" not in cell["metadata"], cell

        # content changes?
        assert rebase_ipynb.verify_processed_ipynb(dest_ipynb_path, src_ipynb_path)


def test_get_git_log():
    start = "dfecfb3"
    end = "e00de3f"
    result = rebase_ipynb.get_git_log(proj_folder, start, end)

    assert isinstance(result, tuple)

    set(result) == set((
        '1bfd7a0a542f6401140bb81cac2614dd128f579e',
        '56f552ffc89e7de4ba372d7357bf0194a1c5a0d3',
        '96ae54de2fd152fa9dd7919f492a95744e5c45ff',
        'da52480de58641c2b3c5b22f4b6aa59fe1d85952',
        'e00de3f2d957986799abd533e13644152a31e80c',
    ))


if '__main__' == __name__:
    pytest.main([__file__])
