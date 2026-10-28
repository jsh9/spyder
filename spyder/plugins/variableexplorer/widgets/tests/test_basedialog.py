# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#

"""
Tests for basedialog.py
"""

# Third party imports
import pytest
from qtpy.QtCore import Qt

# Local imports
from spyder.plugins.variableexplorer.widgets import basedialog
from spyder.plugins.variableexplorer.widgets.basedialog import BaseDialog


@pytest.mark.parametrize("mac", [True, False])
def test_setup_window(qtbot, monkeypatch, mac):
    """
    Check the window type and attributes set by setup_window.

    This is a regression test for spyder-ide/spyder#17718.
    """
    monkeypatch.setattr(basedialog, "MAC", mac)

    dialog = BaseDialog()
    qtbot.addWidget(dialog)
    dialog.setup_window()

    if mac:
        # Dialogs need to stay on top of the main window and not be hidden
        # when Spyder loses focus.
        assert dialog.windowType() == Qt.Tool
        assert dialog.testAttribute(Qt.WA_MacAlwaysShowToolWindow)
    else:
        assert dialog.windowType() == Qt.Window
        assert not dialog.testAttribute(Qt.WA_MacAlwaysShowToolWindow)


if __name__ == "__main__":
    pytest.main()
