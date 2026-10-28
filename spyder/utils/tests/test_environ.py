# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""
Tests for environ.py
"""

# Standard library imports
import os

# Test library imports
import pytest

# Third party imports
from qtpy.QtCore import QTimer

# Local imports
from spyder.utils.environ import (
    amend_user_shell_init,
    get_shell_startup_errors,
    get_user_environment_variables,
    get_user_environment_variables_and_errors,
    UserEnvDialog,
)
from spyder.utils.test import close_message_box


@pytest.fixture
def environ_dialog(qtbot):
    """Setup the Environment variables Dialog."""
    QTimer.singleShot(1000, lambda: close_message_box(qtbot))
    dialog = UserEnvDialog()
    qtbot.addWidget(dialog)

    return dialog


def test_get_user_environment_variables():
    """Test get_user_environment_variables function"""
    # All platforms should have a path environment variable, but
    # Windows may have mixed case.
    keys = {k.lower() for k in get_user_environment_variables().result()}
    assert "path" in keys or "shlvl" in keys


@pytest.mark.skipif(os.name == "nt", reason="Does not apply to Windows")
def test_get_user_env_polluted_shell_init(restore_user_env):
    """
    Test for polluted shell init scripts
    """
    # Test variable value with newline characters.
    # Regression test for spyder-ide/spyder#20097.
    text = "myfunc() {  echo hello;\n echo world\n}\nexport -f myfunc"
    amend_user_shell_init(text)
    user_env = get_user_environment_variables().result()
    assert user_env.pop('BASH_FUNC_myfunc%%') in text

    # Test print to stdout in shell startups.
    # Regression test for spyder-ide/spyder#25263
    amend_user_shell_init("echo Hello World")  # This should pollute stdout
    user_env2 = get_user_environment_variables().result()
    assert user_env2 == user_env


def test_get_shell_startup_errors():
    """
    Test that we detect the errors that make bash and zsh stop reading a
    startup file.
    """
    stderr = (
        # Messages that bash prints when started in interactive mode
        "bash: cannot set terminal process group (-1): Inappropriate ioctl "
        "for device\n"
        "bash: no job control in this shell\n"
        # Errors that make bash stop reading a file
        "bash: /home/user/.bashrc: line 4: syntax error near unexpected "
        "token `fi'\n"
        "bash: /home/user/.bashrc: line 4: `fi'\n"
        "/home/user/.bash_profile: line 9: syntax error: unexpected end of "
        "file\n"
        "bash: /home/user/.bashrc: line 2: unexpected EOF while looking for "
        "matching `\"'\n"
        # Errors that make zsh stop reading a file
        "/home/user/.zshrc:4: parse error near `fi'\n"
        "/home/user/.zshrc:6: unmatched \"\n"
        "/home/user/.bashrc:8: bad substitution\n"
        # Errors after which the shells keep reading the file
        "/home/user/.bash_profile: line 2: pyenv: command not found\n"
        "/home/user/.bashrc:2: command not found: complete\n"
        "bash: ${(L)X}: bad substitution\n"
        # Text written by other programs to stderr
        "Some warning: something happened\n"
        "/opt/conda/lib/python3.12/site-packages/foo.py:12: UserWarning: "
        "unmatched brackets"
    )

    assert get_shell_startup_errors(stderr) == [
        "bash: /home/user/.bashrc: line 4: syntax error near unexpected "
        "token `fi'",
        "/home/user/.bash_profile: line 9: syntax error: unexpected end of "
        "file",
        "bash: /home/user/.bashrc: line 2: unexpected EOF while looking for "
        "matching `\"'",
        "/home/user/.zshrc:4: parse error near `fi'",
        "/home/user/.zshrc:6: unmatched \"",
        "/home/user/.bashrc:8: bad substitution",
    ]

    # No errors
    assert get_shell_startup_errors("bash: no job control in this shell") == []


@pytest.mark.skipif(os.name == "nt", reason="Does not apply to Windows")
def test_get_user_env_shell_init_errors(restore_user_env):
    """
    Test that errors in shell startup files are reported.

    Regression test for spyder-ide/spyder#25263
    """
    amend_user_shell_init("export SPY_BEFORE_ERROR=1\nfi")
    user_env, errors = get_user_environment_variables_and_errors().result()

    # Variables defined before the error are loaded
    assert user_env["SPY_BEFORE_ERROR"] == "1"

    # The error is reported
    assert len(errors) > 0

    # The error is not reported after fixing the startup file
    amend_user_shell_init("export SPY_BEFORE_ERROR=1")
    __, errors_after_fix = get_user_environment_variables_and_errors().result()
    assert len(errors_after_fix) < len(errors)


def test_environ(environ_dialog, qtbot):
    """Test the environment variables dialog."""
    environ_dialog.show()
    assert environ_dialog

    # Wait for data to arrive
    qtbot.waitUntil(lambda: not environ_dialog.get_value() == {})

    # All platforms should have a path environment variable, but
    # Windows may have mixed case.
    keys = {k.lower() for k in environ_dialog.get_value()}
    assert "path" in keys or "shlvl" in keys


if __name__ == "__main__":
    pytest.main()
