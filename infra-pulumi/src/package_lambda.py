"""Package python code into a zip file for AWS Lambdas."""
from pathlib import Path
from shutil import copytree, make_archive
from subprocess import run
from tempfile import TemporaryDirectory

from pulumi.asset import FileArchive


class NotPoetryProjectError(RuntimeError):
    """For when there's no poetry pyproject.toml in the project directory."""

    pass


class NotProjectCodeError(RuntimeError):
    """For when there's no code where the code should be."""

    pass


def package_lambda(root: Path, code: Path, final_dir: Path) -> FileArchive:
    """
    In the project `root` package the `code` into a zip that`s put in `final_dir`.

    This specifically only works with poetry projects where `root` is a path to the root of the poetry project. This
    doesn't yet read the pyproject.toml to know what needs to be installed where so it takes all the python files from
    code and copies it into the the root of `final_dir`.
    """
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise NotPoetryProjectError(root)
    if not code.is_dir():
        raise NotProjectCodeError(code)

    with TemporaryDirectory() as tmpname:
        tmpdir = Path(tmpname)
        run(["poetry", "export", f"--output={tmpdir/'require.txt'}"], check=True, cwd=root)
        run(["pip", "install", "--requirement=require.txt", "--target=code"], check=True, cwd=tmpdir)
        copytree(code, tmpdir / "code", dirs_exist_ok=True)
        make_archive(str(final_dir / "code"), "zip", tmpdir / "code")

    return FileArchive(str(final_dir / "code.zip"))
