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

"""

import argparse
import json
import pathlib
import shutil
import tempfile
import subprocess

from typing import Dict, List, Tuple


def process_commits(repo:pathlib.Path, first_commit:str, last_commit:str, new_branch:str):
    commit_list = git_log_hash(repo=repo, start=first_commit, end=last_commit)

    if first_commit not in commit_list:
        commit_list.insert(0, first_commit)

    start_temporary_branch_head(repo=repo, commit=first_commit, new_branch=new_branch)

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

    commit_info = get_commit_info(repo=repo, commit=commit)

    changed_files = git_diff_fnames(repo=repo, commit=commit)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        for f in changed_files:
            shutil.copy(repo / f, tmpdir / f)
            if f.endswith('.ipynb'):
                process_ipynb(tmpdir/f)

        switch_to_temporary_branch(repo, new_branch)

        for f in changed_files:
            shutil.copy(tmpdir / f, repo / f)

    git_add(repo=repo, files=changed_files)
    git_commit(
        repo=repo,
        commit_info=commit_info
    )


def git_checkout(repo:pathlib.Path, commit:str):
    git(get_checkout_cmd(commit), repo=repo)


def git_add(repo:pathlib.Path, files:List[str]):
    git(get_add_cmd(files), repo=repo)


def git_commit(repo:pathlib.Path, commit_info:Dict[str, str]):
    git(get_commit_cmd(commit_info), repo=repo)


def git(cmd:List[str], repo:pathlib.Path) -> str:
    return subprocess.check_output(cmd, cwd=repo, encoding='utf-8')


def get_checkout_cmd(commit):
    return ['git', 'checkout', commit]


def get_add_cmd(files:List[str]) -> List[str]:
    return ['git', 'add', *files]


def get_commit_cmd(commit_info) -> List[str]:
    return [
        'git', 'commit',
            '-m', commit_info["message"],
            '--date', commit_info["date"],
            '--author', f'{commit_info["author"]} <{commit_info["author_email"]}>'
    ]


def get_commit_info(repo:pathlib.Path, commit:str) -> Dict[str, str]:
    return get_commit_info_from_show(
        subprocess.check_output(
            ['git', 'show', '--stat', commit],
            cwd=repo, encoding='utf-8'
        )
    )

def get_commit_info_from_show(output:str) -> Dict[str, str]:
    lines = output.splitlines()

    body = get_commit_message_body(lines)

    result = {
        "author": lines[1].split('Author:')[1].strip().split('<')[0].strip(),
        "author_email": lines[1].split('<')[1].strip().strip('>'),
        "date": lines[2].split('Date:')[1].strip(),
        'message': body,
    }

    return result


def get_commit_message_body(lines:List[str]) -> str:
    last_line = lines[-1].strip()
    n_files_str = last_line.split('files')[0].strip()
    assert n_files_str.isnumeric(), (last_line, last_line.split('files'))

    n_files = int(n_files_str)
    body = '\n'.join(
        map(
            lambda s:s.strip(),
            lines[4:-n_files-1]
        )
    )

    return body


def assert_git_repo(repo:pathlib.Path) -> bool:
    assert repo.exists()
    assert repo.is_dir()

    repo_git_path = repo / '.git'

    assert repo_git_path.exists()
    assert repo_git_path.is_dir()


def start_temporary_branch_head(repo:pathlib.Path, commit:str, new_branch:str=None):
    assert_git_repo(repo)

    subprocess.run(get_checkout_head_cmd(commit, new_branch), cwd=repo)


def get_checkout_head_cmd(commit:str, new_branch:str) -> List[str]:
    cmd = ['git', 'checkout', commit+'^']

    if new_branch is not None:
        cmd += ['-b', new_branch]

    return cmd


def switch_to_temporary_branch(repo:pathlib.Path, branch:str):
    assert_git_repo(repo)

    subprocess.run(get_switch_cmd(branch), cwd=repo)


def get_switch_cmd(branch:str) -> List[str]:
    return ['git', 'switch', branch]


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


def get_repo_folder_path(parsed:argparse.Namespace) -> pathlib.Path:
    p = pathlib.Path(parsed.repo).resolve(strict=True)

    assert p.exists()
    assert p.is_dir()

    p_git = p / '.git'
    assert p_git.exists()
    assert p.is_dir()

    return p


def git_log_hash(repo:pathlib.Path, start:str, end:str) -> Tuple[str]:
    return tuple(
        subprocess.check_output(
            get_hash_log_cmd(start, end),
            cwd=repo, encoding='utf-8'
        ).splitlines()
    )


def get_hash_log_cmd(start:str, end:str) -> List[str]:
    return ['git', 'log', '--reverse', '--pretty=format:%H', f'{start}..{end}']


def git_diff_fnames(repo:pathlib.Path, commit:str) -> Tuple[str]:
    return tuple(
        git(get_chg_files_cmd(commit), repo=repo).splitlines()
    )


def get_chg_files_cmd(commit:str) -> List[str]:
    return ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit]


def git_switch_c(repo:pathlib.Path, commit:str, branch:str):
    git(get_switch_c_cmd(commit, branch), repo=repo)


def get_switch_c_cmd(commit:str, branch:str) -> List[str]:
    return ['git', 'switch', commit, '-c', branch]


def get_current_branch(repo:pathlib.Path) -> str:
    return git(
        get_current_branch_cmd(),
        repo=repo
    ).strip()


def get_current_branch_cmd() -> List[str]:
    return ['git', 'branch', '--show-current']


def git_branch(repo:pathlib.Path) -> Tuple[str]:
    return tuple(
        git(get_branch_cmd(), repo=repo).splitlines()
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

        subprocess.run(get_nbconvert_ipynb_cmd(src_path, src_after_ipynb_path))

    remove_metadata_id(src_path, src_path)


def get_nbconvert_ipynb_cmd(src_path:pathlib.Path, src_after_ipynb_path:pathlib.Path) -> List[str]:
    return ['jupyter', 'nbconvert', "--to", "notebook", str(src_after_ipynb_path), "--output", str(src_path)]


def remove_metadata_id(src_path:pathlib.Path, dest_path:pathlib.Path):
    ipynb_json = json.loads(src_path.read_text())

    for cell in ipynb_json["cells"]:
        if "metadata" in cell:
            if "id" in cell["metadata"]:
                del cell["metadata"]["id"]

    with dest_path.open('w') as f:
        json.dump(ipynb_json, f)


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

        subprocess.run(get_nbconvert_python_cmd(src_ipynb_path, src_py_path))
        subprocess.run(get_nbconvert_python_cmd(dest_ipynb_path, dest_py_path))

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
    assert len(ipynb_json['cells']) > 0

    link_text = "https://colab.research.google.com/github/"

    if ipynb_json['cells'][0]['cell_type'] == 'markdown':
        if link_text in ipynb_json['cells'][0]['source'][0]:
            ipynb_json['cells'].pop(0)

    with dest_ipynb_path.open('w') as f:
        json.dump(ipynb_json, f)
