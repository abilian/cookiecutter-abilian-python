from contextlib import contextmanager
import shlex
import os
import sys
import subprocess
import datetime
from cookiecutter.utils import rmtree


@contextmanager
def inside_dir(dirpath: str) -> None:
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    try:
        yield result
    finally:
        rmtree(str(result.project))


def run_inside_dir(command: str, dirpath: str) -> int:
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command: str, dirpath: str) -> bytes:
    "Run a command from inside a given directory, returning the command output"
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_year_compute_in_license_file(cookies):
    with bake_in_temp_dir(cookies) as result:
        license_file_path = result.project.join('LICENSE')
        now = datetime.datetime.now()
        assert str(now.year) in license_file_path.read()


def project_info(result):
    """Get toplevel dir, project_slug, and project dir from baked cookies"""
    project_path = str(result.project)
    project_slug = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, project_slug)
    return project_path, project_slug, project_dir


def test_bake_with_defaults(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project.isdir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files = [f.basename for f in result.project.listdir()]
        assert 'src' in found_toplevel_files
        assert 'tests' in found_toplevel_files
        assert 'tox.ini' in found_toplevel_files
        assert 'pyproject.toml' in found_toplevel_files


def test_bake_and_run_tests(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project.isdir()
        assert run_inside_dir('pytest tests', result.project) == 0


def test_bake_withspecialchars_and_run_tests(cookies):
    """Ensure that a `full_name` with double quotes does not break setup.py"""
    with bake_in_temp_dir(
        cookies,
        extra_context={'full_name': 'name "quote" name'}
    ) as result:
        assert result.project.isdir()
        assert run_inside_dir('pytest tests', result.project) == 0


def test_bake_with_apostrophe_and_run_tests(cookies):
    """Ensure that a `full_name` with apostrophes does not break setup.py"""
    with bake_in_temp_dir(
        cookies,
        extra_context={'full_name': "O'connor"}
    ) as result:
        assert result.project.isdir()
        assert run_inside_dir('pytest tests', result.project) == 0


# def test_make_help(cookies):
#     with bake_in_temp_dir(cookies) as result:
#         # The supplied Makefile does not support win32
#         if sys.platform != "win32":
#             output = check_output_inside_dir(
#                 'make help',
#                 result.project
#             )
#             assert b"check code coverage quickly with the default Python" in \
#                 output


# def test_bake_selecting_license(cookies):
#     license_strings = {
#         'MIT license': 'MIT ',
#         'BSD license': 'Redistributions of source code must retain the ' +
#                        'above copyright notice, this',
#         'ISC license': 'ISC License',
#         'Apache Software License 2.0':
#             'Licensed under the Apache License, Version 2.0',
#         'GNU General Public License v3': 'GNU GENERAL PUBLIC LICENSE',
#     }
#     for license, target_string in license_strings.items():
#         with bake_in_temp_dir(
#             cookies,
#             extra_context={'open_source_license': license}
#         ) as result:
#             assert target_string in result.project.join('LICENSE').read()
#             assert license in result.project.join('pyproject.toml').read()
#
#
# def test_bake_not_open_source(cookies):
#     with bake_in_temp_dir(
#         cookies,
#         extra_context={'open_source_license': 'Not open source'}
#     ) as result:
#         found_toplevel_files = [f.basename for f in result.project.listdir()]
#         assert 'LICENSE' not in found_toplevel_files
#         assert 'License' not in result.project.join('README.rst').read()
