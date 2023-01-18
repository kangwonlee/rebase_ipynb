import json
import pathlib
import subprocess
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


@pytest.fixture(scope='session')
def repo() -> pathlib.Path:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        subprocess.run(['git', 'clone', 'https://github.com/kangwonlee/sieve'], cwd=tmpdir)

        test_repo_path = tmpdir / 'sieve'

        test_repo_git_path = test_repo_path / '.git'
        assert test_repo_git_path.exists(), test_repo_path.absolute()

        yield test_repo_path


def test_start_temporary_branch_head__switch_to_temporary_branch(repo:pathlib.Path):
    new_branch_name = 'rebase_ipynb_test'

    # function under test 1
    rebase_ipynb.start_temporary_branch_head(repo, commit="HEAD", new_branch=new_branch_name)

    # list of branch names
    output = subprocess.check_output(['git', 'branch'], cwd=repo, encoding='utf-8')
    output_lines = tuple(map(lambda s:s.strip(), output.splitlines()))
    assert any(map(lambda s:s.endswith(new_branch_name), output_lines)), f"output_lines = {output_lines}"

    # function under test 2
    rebase_ipynb.switch_to_temporary_branch(repo, "main")
    output = subprocess.check_output(['git', 'branch'], cwd=repo, encoding='utf-8')

    # get current branch name
    output_lines = tuple(map(lambda s:s.strip(), output.splitlines()))
    current_branch = tuple(filter(lambda s:s.startswith('*'), output_lines))[0][2:]

    assert current_branch == 'main', current_branch


def test_get_checkout_head_cmd():
    commit = '1234567890'
    new_branch = 'rebase_ipynb_test'
    result = rebase_ipynb.get_checkout_head_cmd(commit, new_branch)

    assert result == f'git checkout {commit}^ -b {new_branch}'.split()


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

    assert set(result) == set((
        '1bfd7a0a542f6401140bb81cac2614dd128f579e',
        '56f552ffc89e7de4ba372d7357bf0194a1c5a0d3',
        '96ae54de2fd152fa9dd7919f492a95744e5c45ff',
        'da52480de58641c2b3c5b22f4b6aa59fe1d85952',
        'e00de3f2d957986799abd533e13644152a31e80c',
    ))


def test_get_changed_files():
    result = rebase_ipynb.get_changed_files(proj_folder, "e00de3f")

    assert isinstance(result, tuple)

    assert set(result) == set((
        'tests/eq_colab.ipynb',
        'tests/eq_local.ipynb',
        'tests/ne_colab.ipynb'
    ))


if '__main__' == __name__:
    pytest.main([__file__])
