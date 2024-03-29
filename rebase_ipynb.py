"""
Unify ipynb format

Input
=====
    * repository folder
    * first commit
    * last commit
    * temporary branch name

Result
======
    * temporary branch with all ipynb files in the unified format
    * remove all hash info

Example
=======
    $ python rebase_ipynb.py --repo /home/username/repo --first_commit 1234567890 --last_commit 0987654321 --new_branch temp_branch

"""

import argparse
import json
import os
import pathlib
import pprint
import shutil
import sys
import tempfile
import subprocess

from typing import Dict, List, Tuple

import nbformat


def process_commits(repo:pathlib.Path, first_commit:str, last_commit:str, new_branch:str):

    start_parent = git_parent_sha(repo=repo, commit=first_commit)

    commit_list = git_log_hash(repo=repo, start_parent=start_parent, end=last_commit)

    assert any(map(lambda x: x.startswith(first_commit), commit_list)), (first_commit, commit_list)
    assert any(map(lambda x: x.startswith(last_commit), commit_list)), (last_commit, commit_list)

    start_temporary_branch_head(repo=repo, start_parent=start_parent, new_branch=new_branch)

    for commit in commit_list:
        process_a_commit(repo=repo, commit=commit, new_branch=new_branch)


def process_a_commit(repo:pathlib.Path, commit:str, new_branch:str):
    """
    Checkout the commit
    Get the commit info
    Copy the changed files to a temporary folder
    Process the ipynb files
    Switch to the temporary branch
    Add the changed files
    """

    git_checkout(repo=repo, commit=commit)

    commit_info = git_show_info(repo=repo, commit=commit)

    changed_files = git_diff_fnames(repo=repo, commit=commit)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)

        assert tmp_path.exists()
        assert tmp_path.is_dir()

        for f in changed_files:
            src = repo / f
            dest = tmp_path / f

            assert src.exists()
            assert src.is_file()

            if not dest.parent.exists():
                dest.parent.mkdir(parents=True)

            assert dest.parent.exists()
            assert dest.parent.is_dir()

            shutil.copy(src, dest)

        switch_to_temporary_branch(repo, new_branch)

        for f in changed_files:

            src = tmp_path / f
            dest = repo / f

            assert src.exists()
            assert src.is_file()

            if not dest.parent.exists():
                dest.parent.mkdir(parents=True)

            assert dest.parent.exists()
            assert dest.parent.is_dir()

            shutil.copy(tmp_path / f, repo / f)

            if f.endswith('.ipynb'):
                process_ipynb(repo / f)

                assert verify_processed_ipynb(tmp_path / f, repo / f)

    git_add(repo=repo, files=changed_files)
    git_commit(
        repo=repo,
        commit_info=commit_info
    )


def git_checkout(repo:pathlib.Path, commit:str):
    check_output(get_checkout_cmd(commit), repo=repo)


def git_add(repo:pathlib.Path, files:List[str]):
    check_output(get_add_cmd(files), repo=repo)


def git_commit(repo:pathlib.Path, commit_info:Dict[str, str]):
    git_config_committer_name(repo, commit_info)
    git_config_committer_email(repo, commit_info)
    set_commit_date(commit_info)
    check_output(get_commit_cmd(commit_info), repo=repo)


def set_commit_date(commit_info:Dict[str, str]):
    """
    Set the commit date

    https://stackoverflow.com/questions/454734
    """
    os.environ["GIT_COMMITTER_DATE"] = commit_info["commit_date"]


def check_output(cmd:List[str], repo:pathlib.Path=None, stderr=None) -> str:
    return subprocess.check_output(cmd, cwd=repo, encoding='utf-8', stderr=stderr)


def get_checkout_cmd(commit):
    return ['git', '-c', "advice.detachedHead=false", 'checkout', commit]


def get_add_cmd(files:List[str]) -> List[str]:
    return ['git', 'add', *files]


def git_config_committer_name(repo:pathlib.Path, commit_info:Dict[str, str]) -> List[str]:
    return check_output([
        'git', 'config', 'user.name', commit_info["committer"],
    ], repo=repo)


def git_config_committer_email(repo:pathlib.Path, commit_info:Dict[str, str]) -> List[str]:
    return check_output([
        'git', 'config', 'user.email', commit_info["committer_email"],
    ], repo=repo)


def get_commit_cmd(commit_info) -> List[str]:
    return [
        'git', 'commit',
            '--allow-empty',
            '-m', commit_info["message"],
            '--date', commit_info["date"],
            '--author', f'{commit_info["author"]} <{commit_info["author_email"]}>',
    ]


def git_show_info(repo:pathlib.Path, commit:str) -> Dict[str, str]:
    return get_commit_info_from_show(
        check_output(
            get_show_stat_commit(commit),
            repo=repo
        )
    )


def get_show_stat_commit(commit:str) -> List[str]:
    return ['git', 'show', '--stat', "--format=fuller",commit]


def git_parent_sha(repo:pathlib.Path, commit:str) -> str:
    return git_show_info(repo, commit+'^')["sha"]


def get_commit_info_from_show(output:str) -> Dict[str, str]:
    lines = output.splitlines()

    body = get_commit_message_body(lines)

    result = {
        "sha": lines[0].split('commit')[1].strip(),
        "author": lines[1].split('Author:')[1].strip().split('<')[0].strip(),
        "author_email": lines[1].split('<')[1].strip().strip('>'),
        "date": lines[2].split('Date:')[1].strip(),
        "committer": lines[3].split('Commit:')[1].strip().split('<')[0].strip(),
        "committer_email": lines[3].split('<')[1].strip().strip('>'),
        "commit_date": lines[4].split('Date:')[1].strip(),
        'message': body,
    }

    return result


def get_commit_message_body(lines:List[str]) -> str:
    last_line = lines[-1].strip()

    if ("file changed" in last_line) or ("files changed" in last_line):
        n_files_str = last_line.split('file')[0].strip()

        assert n_files_str.isnumeric(), (
            pprint.pformat(lines),
            last_line,
            last_line.split('files')
        )

        n_files = int(n_files_str)

        body = '\n'.join(
            map(
                lambda s:s.strip(),
                lines[5:-n_files-1]
            )
        ).strip()

    else:
        # if no file changed
        body = '\n'.join(
            map(
                lambda s:s.strip(),
                lines[5:]
            )
        ).strip()

    return body


def assert_git_repo(repo:pathlib.Path) -> bool:
    assert repo.exists()
    assert repo.is_dir()

    repo_git_path = repo / '.git'

    assert repo_git_path.exists()
    assert repo_git_path.is_dir()


def start_temporary_branch_head(repo:pathlib.Path, start_parent:str, new_branch:str=None):
    assert_git_repo(repo)

    check_output(get_checkout_head_cmd(start_parent, new_branch), repo=repo)


def get_checkout_head_cmd(start_parent:str, new_branch:str=None) -> List[str]:
    cmd = ['git', 'checkout', start_parent]

    if new_branch is not None:
        cmd += ['-b', new_branch]

    return cmd


def switch_to_temporary_branch(repo:pathlib.Path, branch:str):
    assert_git_repo(repo)

    check_output(get_switch_cmd(branch), repo=repo)


def get_switch_cmd(branch:str) -> List[str]:
    return ['git', 'switch', branch]


def get_repo_folder_path(parsed:argparse.Namespace) -> pathlib.Path:
    p = pathlib.Path(parsed.repo).resolve(strict=True)

    assert p.exists()
    assert p.is_dir()

    p_git = p / '.git'
    assert p_git.exists()
    assert p.is_dir()

    return p


def git_log_hash(repo:pathlib.Path, start_parent:str, end:str) -> Tuple[str]:
    return tuple(
        check_output(get_hash_log_cmd(start_parent, end), repo=repo).splitlines()
    )


def get_hash_log_cmd(start_parent:str, end:str) -> List[str]:
    return ['git', 'log', '--reverse', '--pretty=format:%H', f'{start_parent}..{end}']


def git_diff_fnames(repo:pathlib.Path, commit:str) -> Tuple[str]:
    return tuple(
        check_output(get_chg_files_cmd(commit), repo=repo).splitlines()
    )


def get_chg_files_cmd(commit:str) -> List[str]:
    return ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit]


def git_switch_c(repo:pathlib.Path, commit:str, branch:str):
    check_output(get_switch_c_cmd(commit, branch), repo=repo)


def get_switch_c_cmd(commit:str, branch:str) -> List[str]:
    return ['git', 'switch', commit, '-c', branch]


def get_current_branch(repo:pathlib.Path) -> str:
    return check_output(
        get_current_branch_cmd(),
        repo=repo
    ).strip()


def get_current_branch_cmd() -> List[str]:
    return ['git', 'branch', '--show-current']


def git_branch(repo:pathlib.Path) -> Tuple[str]:
    return tuple(
        check_output(get_branch_cmd(), repo=repo).splitlines()
    )


def get_branch_cmd() -> List[str]:
    return ['git', 'branch']


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

    remove_id_from_file(src_path, src_path)


def jupyter_nbconvert_notebook(input_path:pathlib.Path, output_path:pathlib.Path, my_null):
    check_output(get_nbconvert_ipynb_cmd(input_path, output_path), stderr=my_null)


def get_nbconvert_ipynb_cmd(input_path:pathlib.Path, output_path:pathlib.Path) -> List[str]:
    return ['jupyter', 'nbconvert', "--to", "notebook", str(input_path), "--output", str(output_path)]


def remove_id_from_file(src_path:pathlib.Path, dest_path:pathlib.Path, allowed:Tuple[str]=('view-in-github',)):
    ipynb_json = json.loads(src_path.read_text())

    for cell in ipynb_json["cells"]:
        remove_metadata_id_from_cell(cell, allowed)
        remove_id_from_cell(cell)
        remove_output_id_from_cell(cell)

    for cell in ipynb_json["cells"]:
        assert "id" not in cell

    with dest_path.open('w', encoding="utf-8") as f:
        json.dump(ipynb_json, f, indent=1, ensure_ascii=False)


def remove_id_from_cell(cell:nbformat.NotebookNode):
    if cell.get("cell_type") in ("markdown", "code"):
        if "id" in cell:
            del cell["id"]


def remove_output_id_from_cell(cell:nbformat.NotebookNode, allowed:Tuple[str]=('view-in-github',)):
    if "metadata" in cell:
        if "colab" in cell["metadata"]:
            del cell["metadata"]["colab"]
        if "outputId" in cell["metadata"]:
            del cell["metadata"]["outputId"]


def remove_metadata_id_from_cell(cell:nbformat.NotebookNode, allowed:Tuple[str]=('view-in-github',)):
    if "metadata" in cell:
        if "id" in cell["metadata"]:
            if cell["metadata"]["id"] not in allowed:
                del cell["metadata"]["id"]


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

        check_output(get_nbconvert_python_cmd(src_ipynb_path, src_py_path))
        check_output(get_nbconvert_python_cmd(dest_ipynb_path, dest_py_path))

        assert src_py_path.exists()
        assert src_py_path.is_file()

        assert dest_py_path.exists()
        assert dest_py_path.is_file()

        txt1 = src_py_path.read_text()
        txt2 = dest_py_path.read_text()

    return txt1 == txt2


def get_nbconvert_python_cmd(ipynb_path:pathlib.Path, py_path:pathlib.Path) -> List[str]:
    return ['jupyter', 'nbconvert', "--to", "python", str(ipynb_path), "--output", str(py_path)]


def remove_colab_button(src_ipynb_path:pathlib.Path, dest_ipynb_path:pathlib.Path):
    assert src_ipynb_path.exists()
    assert src_ipynb_path.is_file()
    assert src_ipynb_path.suffix == '.ipynb'

    ipynb_json = json.loads(src_ipynb_path.read_text())

    assert 'cells' in ipynb_json
    assert isinstance(ipynb_json['cells'], list)
    # assert len(ipynb_json['cells']) > 0, (
    #     "ipynb file is empty\n",
    #     ipynb_json
    #     )

    link_text = "https://colab.research.google.com/github/"

    if (len(ipynb_json['cells']) > 0):
        if ipynb_json['cells'][0]['cell_type'] == 'markdown':
            if link_text in ipynb_json['cells'][0]['source'][0]:
                ipynb_json['cells'].pop(0)

    with dest_ipynb_path.open('w', encoding="utf-8") as f:
        json.dump(ipynb_json, f, indent=1, ensure_ascii=False)


def get_commiter_info_hash(repo, sha:str):
    commit = repo.commit(sha)
    return commit.committer.email, commit.committer.name, commit.committer.date


def parse_argv(argv:List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unify ipynb format")

    parser.add_argument(
        "-r", "--repo", type=str, required=True,
        help="repository folder"
    )
    parser.add_argument(
        "-f", "--first", type=str, required=True,
        help="first commit"
    )
    parser.add_argument(
        "-l", "--last", type=str, required=True,
        help="last commit"
    )
    parser.add_argument(
        "-b", "--branch", type=str, required=True,
        help="temporary branch name"
    )

    return parser.parse_args(argv)


def main(argv:List[str]):
    parsed = parse_argv(argv[1:])

    process_commits(pathlib.Path(parsed.repo).absolute(), parsed.first, parsed.last, parsed.branch)


if __name__ == '__main__':
    main(sys.argv)
