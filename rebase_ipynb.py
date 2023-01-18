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
import tempfile
import subprocess

from typing import List, Tuple


# TODO : get the commit prior to the first commit
# TODO : start the temporary branch
# TODO : checkout each commit
# TODO : process the ipynb files
# TODO : add commit
# TODO : go checkout the next commit


def assert_git_repo(repo:pathlib.Path) -> bool:
    assert repo.exists()
    assert repo.is_dir()

    repo_git_path = repo / '.git'

    assert repo_git_path.exists()
    assert repo_git_path.is_dir()


def checkout_head(repo:pathlib.Path, commit:str, new_branch:str=None):
    assert_git_repo(repo)

    subprocess.run(get_checkout_head_cmd(commit, new_branch), cwd=repo)


def get_checkout_head_cmd(commit:str, new_branch:str) -> List[str]:
    cmd = ['git', 'checkout', commit+'^']

    if new_branch is not None:
        cmd += ['-b', new_branch]

    return cmd


def start_temporary_branch(repo:pathlib.Path, branch:str):
    assert_git_repo(repo)

    subprocess.run(['git', 'switch', '-c', branch], cwd=repo)


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


def get_git_log(repo:pathlib.Path, start:str, end:str) -> Tuple[str]:
    return tuple(
        subprocess.check_output(
            ['git', 'log', '--reverse', '--pretty=format:%H', f'{start}..{end}'],
            cwd=repo, encoding='utf-8'
        ).splitlines()
    )


def get_changed_files(repo:pathlib.Path, commit:str) -> Tuple[str]:
    return tuple(
        subprocess.check_output(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit],
            cwd=repo, encoding='utf-8'
        ).splitlines()
    )


def git_switch_c(repo:pathlib.Path, commit:str, branch:str):
    subprocess.run(['git', 'switch', commit, '-c', branch], cwd=repo)


def get_current_branch(repo:pathlib.Path) -> str:
    return subprocess.check_output(
        ['git', 'branch', '--show-current'],
        cwd=repo, encoding='utf-8'
    ).strip()


def get_branch_list(repo:pathlib.Path) -> Tuple[str]:
    return tuple(
        subprocess.check_output(
            ['git', 'branch'],
            cwd=repo, encoding='utf-8'
        ).splitlines()
    )


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

    remove_metadata_id(src_path, src_path)


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
