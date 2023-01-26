import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile

from typing import Tuple

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


@pytest.fixture()
def commits_original() -> Tuple[str]:
    return (
        "86ebb42000d7cdd9af0c320ee24be5dc2fa24a2f",
        "bae0691b9b6917d951f0161405063f401b058073",
        "c31c6b24632729a2fadb090ef37d9d879e30c696",
        "b41002e62d1dfe3ab4143a2f6ba1b5aeeab13e74",
        "e1c890a2f6dd6a7d6962b9e967527f40b48d89c5",
        "6a033e9fde2116f24bd62e403a73d69429408a31",
        "717ed6844017766e040d49e6dd562d153aa2bb44",
        "74af5773172c4bb7013a44527a688079f1364848",
        "86eaccc9b8c6bcd275f93fd7ba3d7d15c1b13843",
        "8e1ebe4b5cc34e86de4be066d93d3f9f6b4c0545",
        "253bb6edb3d0f1724292384bbab12068d8061133",
        "9acef1eb750c3e633281b39802511455c56ff0b8",
    )


def test_get_commit_info_from_show():
    git_show_msg = (
        "commit c759024d70d6719b33cc8e10533f2bcdbcd18abe (HEAD -> temporary-branch)\n"
        "Author: KangWon LEE <kangwon.lee@tukorea.ac.kr>\n"
        "Date:   Wed Jan 18 20:57:54 2023 +0900\n"
        "\n"
        "    checkout_head() -> start_temporary_branch_head()\n"
        "\n"
        "    also removed start_temporary_branch() to avoid confusion\n"
        "\n"
        "    for this application, the original intention was\n"
        "    to start the temporary branch at the HEAD of the first commit\n"
        "\n"
        " rebase_ipynb.py            |  8 +-------\n"
        " tests/test_rebase_ipynb.py | 11 +++++++----\n"
        " 2 files changed, 8 insertions(+), 11 deletions(-)\n"
    )

    result = rebase_ipynb.get_commit_info_from_show(git_show_msg)

    assert isinstance(result, dict)

    assert result['author'] == "KangWon LEE"
    assert result['author_email'] == "kangwon.lee@tukorea.ac.kr"
    assert result['date'] == "Wed Jan 18 20:57:54 2023 +0900"
    assert result['message'] == (
        "checkout_head() -> start_temporary_branch_head()\n"
        "\n"
        "also removed start_temporary_branch() to avoid confusion\n"
        "\n"
        "for this application, the original intention was\n"
        "to start the temporary branch at the HEAD of the first commit\n"
    )


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


def test_get_git_log(repo, commits_original):
    start = commits_original[0]
    end = commits_original[-1]

    result = rebase_ipynb.git_log_hash(repo, start, end)

    assert isinstance(result, tuple)

    assert set(result) == set(commits_original)


def test_get_changed_files():
    result = rebase_ipynb.git_diff_fnames(proj_folder, "e00de3f")

    assert isinstance(result, tuple)

    assert set(result) == set((
        'tests/eq_colab.ipynb',
        'tests/eq_local.ipynb',
        'tests/ne_colab.ipynb'
    ))


def test_get_hash_log_cmd():
    start = 'abc'
    end = 'xyz'

    result = rebase_ipynb.get_hash_log_cmd(start, end)

    assert isinstance(result, list)
    assert all(map(lambda x: isinstance(x, str), result))

    expected = ['git', 'log', '--reverse', '--pretty=format:%H', f'{start}..{end}']

    assert result == expected


def test_git_parent_sha(repo):
    result = rebase_ipynb.git_parent_sha(repo, 'bae0691b')

    assert result.startswith("86ebb42")


def test_process_commits(repo:pathlib.Path, commits_original:Tuple[str]):

    first_commit = '86ebb42'
    last_commit = '9acef1e'

    # get the commit before the first commit
    first_commit_parent = rebase_ipynb.git_parent_sha(repo, first_commit)

    # are the commits in the list?
    assert any(
        map(
            lambda x: x.startswith(first_commit),
            commits_original
        )
    ), f"first commit {first_commit} not found in {commits_original}"

    assert any(
        map(
            lambda x: x.startswith(last_commit),
            commits_original
        )
    ), f"last commit {last_commit} not found in {commits_original}"

    # new branch name with a random integer
    new_branch = f'test_branch_{random.randint(0, (2**4)**8):08x}'

    # commit info
    commit_info_inverted = []

    for commit in commits_original:
        commit_info_inverted.append(rebase_ipynb.git_show_info(repo, commit))

    try:

        #####################
        # function under test
        rebase_ipynb.process_commits(repo, first_commit, last_commit, new_branch)
        #####################

        # new branch exists?
        git_branch_result = subprocess.check_output(['git', 'branch',], cwd=repo, encoding='utf-8')
        branch_names = tuple(map(lambda x: x.strip(" *"), git_branch_result.splitlines()))
        assert new_branch in branch_names

        # commit hashes in new branch?
        commits_new = subprocess.check_output(
            ['git', 'log', '--reverse', '--pretty=format:%H', f'{first_commit_parent}..{new_branch}'],
            cwd=repo, encoding='utf-8'
        ).splitlines()[1:]

        # same number of commits?
        assert len(commits_new) == len(commits_original), (
            f"len(commits_new)={len(commits_new)} "
            f"!= len(commits_original)={len(commits_original)}\n"
            f"commits_new=\n{commits_new}\n"
            f"commits_original=\n{commits_original}\n"
        )

        # each commit same info?
        for sha_org, sha_new in zip(commits_original, commits_new):
            org_info = rebase_ipynb.git_show_info(repo, sha_org)
            new_info = rebase_ipynb.git_show_info(repo, sha_new)

            assert org_info == new_info, (
                f"org_info={org_info} != new_info={new_info}\n"
            )

        # each commit changed ipynb files produce same .py files?
        for sha_org, sha_new in zip(commits_original, commits_new):
            org_files = rebase_ipynb.git_diff_fnames(repo, sha_org)
            new_files = rebase_ipynb.git_diff_fnames(repo, sha_new)

            # changed files the same?
            assert set(org_files) == set(new_files), (
                f"org_files={org_files} != new_files={new_files}\n"
            )

            # each changed file produces same .py file?
            for fname in org_files:
                if fname.endswith('.ipynb'):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tmp_path = pathlib.Path(tmpdir)
                        # checkout the original sha
                        subprocess.check_call(['git', 'checkout', sha_org, fname], cwd=repo)
                        # original filename after copy
                        original_fname = tmp_path / ("org_" + fname)

                        # copy the original file to a temporary directory
                        shutil.copy(repo / fname, original_fname)

                        # checkout the new sha
                        subprocess.check_call(['git', 'checkout', sha_new, fname], cwd=repo)
                        # new filename after copy
                        new_fname = tmp_path / ("new_" + fname)

                        # copy the original file to a temporary directory
                        shutil.copy(repo / fname, new_fname)

                        assert rebase_ipynb.verify_processed_ipynb(original_fname, new_fname)

    finally:
        branch_names_finally = subprocess.check_output(['git', 'branch',], cwd=repo, encoding='utf-8')
        branch_names_finally_list = branch_names_finally.splitlines()

        was_branch_created = any(map(lambda x: x.strip(" *") == new_branch, branch_names_finally_list))

        if was_branch_created:
            subprocess.run(
                ['git', 'switch', "--force", 'main'],
                cwd=repo,
            )

            # delete the new branch
            subprocess.run(
                ['git', 'branch', '-D', new_branch],
                cwd=repo,
            )


if '__main__' == __name__:
    pytest.main([__file__])
