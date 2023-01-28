import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import urllib.parse as up

from typing import Dict, List, Tuple, Union

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

Commit_log = Union[List[str], Tuple[str]]
Repo_Info = Dict[str, Union[pathlib.Path, str, Commit_log]]


def commits_original_sieve() -> Commit_log:
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


def commits_original_nmisp() -> Commit_log:
    return (
        "7c73e39800254559363a139b282902b42af85cab",
        "cb9d69afa8885e7fc6411470cd62416ed1dadaa3",
        "dad8ada84ab13e83d680f3341840582ddef988b7",
        "379f39d6a217cf3e2f3ff7e28aeea90f3e3df5ea",
        "d6cab0beb7085678970814dc91617012dcfb41f8",
        "402a3cacba5c00d7e4fc56c95173701501969e13",
        "c7fdb8239c83326351e1d51b994c5b2a0f3ea5db",
        "9939350b317a1e393858c16e770b379c7675242b",
        "25ecbe9e4ec64a0139a2e10da15048e0d6ed14f7",
        "787d31e45076f40f583865bb32af077af5fb3a39",
        "922e8b9b1d2ab2765e125a411d1456579c721402",
        "facad888eb2606c10f0a20f4a8fc4797b7acb79a",
        "11edb838d45cb645412a5d8f8c32fe4a1534aa61",
        "8b2ece1d1eb7f6da4eb7edd051ccf5d75a45974e",
        "6fd8222acff8a456681ce04955046b85c7fac6d8",
        "b52e7cf7b7e99a2b83f4e0038ba2027afe8d8cd4",
        "1d38c296f22d4c9913d2eec77b4cb9ad4a441071",
        "1ca8df45c34f3776b6878bd2be0dd31581000fd0",
        "2780538d412bd93baa1536d949d94bc2c5cbae06",
        "1f429d3d30df13c3b61ba6c0475c23e90f84406a",
        "15628eb937c8bed2df85b7e9223304b6cd587de2",
        "baf99312b344bf7619ed9c30fa5c8b9051a25449",
        "661025a32c2561050ed5920acbe5476ea66e1f1c",
        "e4ccb17c0f31cb05be7fbd1b39d2dc0ecd38ecfb",
        "59fe94c9654906960bd1202bd202f1fe5ac6967f",
        "8078178275d6146968547c1bbe4cf201c9080b7c",
        "b64a10bfbb41676a06023676418130611084302d",
        "9fa28b97da0148be1c94fd449cc4bd790705356a",
        "cd943166841624d99e2ef7ad60d8c071d2f84bc5",
        "98630891e5e879e6a988fc44908f30fa49db0ddb",
        "2aed47a285af76bfc2bd8220a094b2d6e0160a93",
        "139b8b07d9d6c34cc69fd59aee5069f9a4442ce7",
        "83e099187f9e979245635a70cfcb511a7b6ee2df",
        "efa5862f650a23e8ad748158e7460f7acbe65587",
        "35ed39504cf69318d9f23d72b6ca42de1582a3a9",
        "497a75c1ab6425ca1c3eb6b599624aa0befc151f",
        "3a0cb8b0eb9b1d7d1e764b9736c9c32efbd7d6fd",
        "828db88d1ae397aaa752b824a5eb2037bf55e052",
        "335868d72ecfd19e841894bd24aef94638d91126",
        "c1ea231fa250a743d86489a34eb1c632a91c62cb",
        "f319dd7edc840759143731fead9e17af1ebf06fc",
        "b9de027b795106e248e344b8e8a9c86e343f15ad",
        "c2219fc6e1eabeb725cac58df9bc960d2ac70bbb",
        "b327d3c7be207ce27b6cc11f16701691f384acef",
        "882d9a78d8245ecf6089d3c9996eedb0a334dd15",
        "54cd0315ed21f9180acc9be84de76e7766710b79",
        "a607b2be68f113b3a33d683962fe7ffd1e74760e",
        "3626b33df02f222d4b9a656df07476adcbef5279",
        "a7f6f455f1470ac39dee5c0be85fcd44b35a9565",
        "913a1c5538a8035ac8a295b298dbfdf3444ca7dc",
        "e74d63e6844ce350091e00ff0f61ebbea7bc5150",
        "b752c683e460228d66fb96ab986cc33cae6f2991",
        "dd4b283e21a7f3fe77f23cc2a2aa68181950fb3e",
        "bc13d845555fe6054329edbc914bc012c9323cf1",
        "031db6e6ae298c6761baa1fe28c489b7d44b487b",
        "4d4136e02afcd8502e73c8f29ca0dba9e10dfd4d",
        "98b1e33537f51f8dba402c128866c39f8a74f04e",
        "390fc239ccabc71f0607dcd6d9603a6a09b482bb",
        "9b302eb08174112cc679ba978376d747fe9a24d3",
        "30b00f17dece019652068e5186017ad23e0d3d64",
        "bdac07abd421ed4fc72adb784a28e9c2c30f0726",
        "c0b1a033159e08e500a39a77e285e21ef8a2706f",
        "f25d7ec47cce435a1e6607842d63002eb8c1a4a1",
        "36b26bc3e1e8c85d7edaa40f6a816c26172d6c11",
    )


@pytest.fixture(
    scope='session',
    params=[
        {
            'url':'https://github.com/kangwonlee/sieve',
            'first': '86ebb42',
            'last': '9acef1e',
            'commits_original': commits_original_sieve(),
            'chg': {'sha': "717ed68", "files": ("sieve.ipynb",)}
        },
        {
            'url':'https://github.com/kangwonlee/nmisp',
            'first': '7c73e398002',
            'last': '36b26bc3e1e8c',
            'commits_original': commits_original_nmisp(),
            'chg': {'sha': "922e8b9", "files": ("00_introduction/20_python_review.ipynb",)}
        },
    ]
)
def repo_info(request) -> Repo_Info:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        subprocess.run(['git', 'clone', request.param['url']], cwd=tmpdir)

        test_repo_path = tmpdir / (up.urlparse(request.param['url']).path.split('/')[-1])

        test_repo_git_path = test_repo_path / '.git'
        assert test_repo_git_path.exists(), test_repo_path.absolute()

        yield {
            'path': test_repo_path,
            'first': request.param['first'],
            'last': request.param['last'],
            'commits_original': request.param['commits_original'],
            'chg': request.param['chg'],
        }


def test_get_commit_info_from_show__two_files_changed():
    git_show_msg = (
        "commit c759024d70d6719b33cc8e10533f2bcdbcd18abe\n"
        "Author:     KangWon LEE <kangwon.lee@tukorea.ac.kr>\n"
        "AuthorDate: Wed Jan 18 20:57:54 2023 +0900\n"
        "Commit:     KangWon LEE <kangwon.lee@tukorea.ac.kr>\n"
        "CommitDate: Wed Jan 18 20:57:54 2023 +0900\n"
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
    assert result['committer'] == "KangWon LEE"
    assert result['committer_email'] == "kangwon.lee@tukorea.ac.kr"
    assert result['commit_date'] == "Wed Jan 18 20:57:54 2023 +0900"
    assert result['message'] == (
        "checkout_head() -> start_temporary_branch_head()\n"
        "\n"
        "also removed start_temporary_branch() to avoid confusion\n"
        "\n"
        "for this application, the original intention was\n"
        "to start the temporary branch at the HEAD of the first commit"
    )


def test_get_commit_info_from_show__one_file_changed():
    git_show_msg = (
        "commit 717ed6844017766e040d49e6dd562d153aa2bb44\n"
        "Author:     KangWon LEE <kangwon.lee@tukorea.ac.kr>\n"
        "AuthorDate: Sat Nov 19 09:55:32 2022 +0900\n"
        "Commit:     KangWon LEE <kangwon.lee@tukorea.ac.kr>\n"
        "CommitDate: Sat Nov 19 09:55:32 2022 +0900\n"
        "\n"
        "    init_other_columns()\n"
        "\n"
        " sieve.ipynb | 33 ++++++++++++++++++++++++---------\n"
        " 1 file changed, 24 insertions(+), 9 deletions(-)\n"
    )

    result = rebase_ipynb.get_commit_info_from_show(git_show_msg)

    assert isinstance(result, dict)

    assert result['author'] == "KangWon LEE"
    assert result['author_email'] == "kangwon.lee@tukorea.ac.kr"
    assert result['date'] == "Sat Nov 19 09:55:32 2022 +0900"
    assert result['message'] == (
        "init_other_columns()"
    )


def test_start_temporary_branch_head__switch_to_temporary_branch(repo_info:Repo_Info):
    new_branch_name = 'rebase_ipynb_test'

    repo_info = repo_info["path"]

    # function under test 1
    rebase_ipynb.start_temporary_branch_head(repo_info, start_parent="HEAD^", new_branch=new_branch_name)

    # list of branch names
    output = subprocess.check_output(['git', 'branch'], cwd=repo_info, encoding='utf-8')
    output_lines = tuple(map(lambda s:s.strip(), output.splitlines()))
    assert any(map(lambda s:s.endswith(new_branch_name), output_lines)), f"output_lines = {output_lines}"

    # function under test 2
    rebase_ipynb.git_switch(repo_info, "main")
    output = subprocess.check_output(['git', 'branch'], cwd=repo_info, encoding='utf-8')

    # get current branch name
    output_lines = tuple(map(lambda s:s.strip(), output.splitlines()))
    current_branch = tuple(filter(lambda s:s.startswith('*'), output_lines))[0][2:]

    assert current_branch == 'main', current_branch


def test_get_checkout_head_cmd():
    commit = '1234567890'
    new_branch = 'rebase_ipynb_test'
    result = rebase_ipynb.get_checkout_head_cmd(
        start_parent=commit+'^',
        new_branch=new_branch
    )

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

    src_ipynb_json = json.loads(src_ipynb_path.read_text(encoding="utf-8"))
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


def test_get_git_log(repo_info: Repo_Info):

    repo = repo_info["path"]

    commits_original = repo_info["commits_original"]

    start_parent = commits_original[0]
    end = commits_original[-1]

    result = rebase_ipynb.git_log_hash(repo, start_parent, end)

    assert isinstance(result, tuple)

    assert result == commits_original[1:], subprocess.check_output(
        ['git', 'log', '--oneline', '--graph', "--all"],
        cwd=repo, encoding="utf-8"
    )


def test_get_changed_files(repo_info: Repo_Info):

    repo = repo_info["path"]

    result = rebase_ipynb.git_diff_fnames(repo, repo_info["chg"]["sha"])

    assert isinstance(result, tuple)

    assert set(result) == set(repo_info["chg"]["files"])


def test_get_hash_log_cmd():
    start_parent = 'abc'
    end = 'xyz'

    result = rebase_ipynb.get_hash_log_cmd(start_parent, end)

    assert isinstance(result, list)
    assert all(map(lambda x: isinstance(x, str), result))

    expected = ['git', 'log', '--reverse', '--pretty=format:%H', f'{start_parent}..{end}']

    assert result == expected


def test_git_parent_sha(repo_info:Repo_Info):
    repo = repo_info["path"]

    commits_original = repo_info["commits_original"]

    result = rebase_ipynb.git_parent_sha(repo, commits_original[-1])

    assert result.startswith(commits_original[-2])


def test_fixture_first_last_commit(repo_info:Repo_Info):
    # get the commit before the first commit
    start_parent = rebase_ipynb.git_parent_sha(repo_info["path"], repo_info["first"])

    # get the commits between the first and the last commit
    sha_log = rebase_ipynb.git_log_hash(repo_info["path"], start_parent, repo_info["last"])

    assert sha_log[0].startswith(repo_info["first"]), (repo_info["first"], sha_log)
    assert sha_log[-1].startswith(repo_info["last"]), (sha_log, repo_info["last"])


def test_process_commits(repo_info:Repo_Info):

    repo = repo_info["path"]

    first_commit = repo_info["first"]
    last_commit = repo_info["last"]

    # get the commit before the first commit
    start_parent = rebase_ipynb.git_parent_sha(repo, first_commit)

    # get the commits between the first and the last commit
    commits_original = rebase_ipynb.git_log_hash(repo, start_parent, last_commit)

    # all commits until the last_commit
    all_sha_inv_org = subprocess.check_output(
        ['git', 'log', '--pretty=format:%H', last_commit],
        cwd=repo, encoding="utf-8"
    ).splitlines()

    # first commit in the all_sha_inv_org
    assert all_sha_inv_org[len(commits_original)-1].startswith(first_commit)

    n_sha_inv_org = all_sha_inv_org[:len(commits_original)]

    assert set(n_sha_inv_org) == set(commits_original)

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

        # all commits until the end of the new branch
        all_sha_inv_new = subprocess.check_output(
            ['git', 'log', '--pretty=format:%H', new_branch],
            cwd=repo, encoding="utf-8"
        ).splitlines()

        n_sha_inv_new = all_sha_inv_new[:len(commits_original)]

        # each commit same info?
        for sha_org, sha_new in zip(n_sha_inv_org, n_sha_inv_new):
            compare_commit_info(repo, sha_org, sha_new)

        # each commit changed ipynb files produce same .py files?
        for sha_org, sha_new in zip(n_sha_inv_org, n_sha_inv_new):
            compare_ipynb_py(repo, sha_org, sha_new)

        # first commits are different?
        assert all_sha_inv_org[len(commits_original)-1] != all_sha_inv_new[len(commits_original)-1], (
            '\n' +
            subprocess.check_output(
                ['git', 'log', '--graph', '--oneline', '--all'],
                cwd=repo, encoding="utf-8"
            )
        )

        # both branches have the same parent?
        assert all_sha_inv_org[len(commits_original)] == all_sha_inv_new[len(commits_original)], (
            '\n' +
            subprocess.check_output(
                ['git', 'log', '--graph', '--oneline', '--all'],
                cwd=repo, encoding="utf-8"
            )
        )

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


def compare_ipynb_py(repo, sha_org, sha_new):
    org_files = rebase_ipynb.git_diff_fnames(repo, sha_org)
    new_files = rebase_ipynb.git_diff_fnames(repo, sha_new)

            # check extensions
    assert all(map(lambda x: x.endswith('.ipynb'), org_files)), (org_files,)
    assert all(map(lambda x: x.endswith('.py'), new_files)), (new_files,)

            # check number of changed files
    assert len(org_files) == len(new_files)

            # all files converted?
    org_name_set = set(map(lambda x: x[:-6], org_files))
    new_name_set = set(map(lambda x: x[:-3], new_files))

    assert org_name_set == new_name_set

            # each changed file produces same .py file?
    for fname in org_files:
        if fname.endswith('.ipynb'):
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = pathlib.Path(tmpdir)
                        # checkout the original sha
                subprocess.check_call(
                            ['git', '-c', "advice.detachedHead=false", 'checkout', sha_org, fname],
                            cwd=repo
                        )
                        # original filename after copy
                ipynb_fname_from_org_branch = tmp_path / ("org_" + fname)

                if not ipynb_fname_from_org_branch.parent.exists():
                    ipynb_fname_from_org_branch.parent.mkdir(parents=True)

                        # copy the original file to a temporary directory
                shutil.copy(repo / fname, ipynb_fname_from_org_branch)

                py_fname_from_org_branch = ipynb_fname_from_org_branch.with_suffix('.py')

                subprocess.check_output(
                            [
                                'jupyter', 'nbconvert', '--to', "python",
                                str(ipynb_fname_from_org_branch.absolute()),
                                '--output', str(py_fname_from_org_branch.absolute())
                            ],
                            cwd=tmp_path, stderr=subprocess.DEVNULL, encoding='utf-8'
                        )

                assert py_fname_from_org_branch.exists()
                assert py_fname_from_org_branch.is_file()

                        # compare the two .py files
                org_branch_txt = py_fname_from_org_branch.read_text(encoding="utf-8")
                assert isinstance(org_branch_txt, str)

                    # new filename after copy
            py_name_in_repo = fname[:-6] + '.py'

                    # checkout the new sha
            subprocess.check_call(
                        ['git', '-c', "advice.detachedHead=false", 'checkout', sha_new, py_name_in_repo],
                        cwd=repo
                    )
            py_path_in_repo = repo / py_name_in_repo

            assert py_path_in_repo.exists()
            assert py_path_in_repo.is_file()

            new_branch_txt = py_path_in_repo.read_text(encoding="utf-8")

            assert org_branch_txt == new_branch_txt, (
                        f"org: {sha_org} -- {fname} != new: {sha_new} -- {py_name_in_repo}"
                    )


def compare_commit_info(repo, sha_org, sha_new):
    org_info = rebase_ipynb.git_show_info(repo, sha_org)
    new_info = rebase_ipynb.git_show_info(repo, sha_new)

    # cannot be the same
    del org_info['sha']
    del new_info['sha']

    assert org_info == new_info, (
        f"org_info={org_info} != new_info={new_info}\n"
    )


@pytest.fixture
def commit_output_sample() -> Dict[str, str]:

    branch = "bbb"
    sha = "123abc"
    msg = "msgmsgmsg"
    fname = "fname.txt"

    git_commit_output = (
        f"[{branch} {sha}] {msg}\n"
        " 1 file changed, 0 insertions(+), 0 deletions(-)\n"
        f" create mode 100644 {fname}\n"
    )

    return {
        'branch': branch,
        'sha': sha,
        'msg': msg,
        'fname': fname,
        'git_commit_output': git_commit_output,
    }


def test_get_pattern_branch_sha_msg__one_file_changed(commit_output_sample):

    # functun under test
    result = rebase_ipynb.get_pattern_branch_sha_msg()

    r = result.match(commit_output_sample['git_commit_output'].splitlines()[0])

    assert r is not None
    assert r.group('branch') == commit_output_sample['branch']
    assert r.group('sha') == commit_output_sample['sha']
    assert r.group('message') == commit_output_sample['msg']


def test_get_branch_sha_msg__one_file_changed(commit_output_sample):

    # functun under test
    result = rebase_ipynb.get_branch_sha_msg(commit_output_sample['git_commit_output'])

    assert result['branch'] == commit_output_sample['branch']
    assert result['sha'] == commit_output_sample['sha']
    assert result['message'] == commit_output_sample['msg']


if '__main__' == __name__:
    pytest.main([__file__])
