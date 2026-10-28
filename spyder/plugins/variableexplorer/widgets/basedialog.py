# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Base variable explorer dialog
"""

# Third party imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog
import qstylizer.style

# Local imports
from spyder.utils.stylesheet import MAC


class BaseDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # Set style of all QPushButton's inside the dialog.
        css = qstylizer.style.StyleSheet()
        css.QPushButton.setValues(
            padding='3px 15px 3px 15px',
        )
        self.setStyleSheet(css.toString())

    def setup_window(self):
        """
        Make the dialog act as a separate window.

        Notes
        -----
        This must be called before the dialog is shown because, on macOS,
        the attribute set here only takes effect when the native window is
        created.
        """
        if MAC:
            # Tool windows are hidden by default when Spyder loses focus, so
            # this prevents that.
            # Fixes spyder-ide/spyder#17718
            self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)

            # This makes the dialog stay on top of Spyder's main window.
            # See spyder-ide/spyder#9051, spyder-ide/spyder#12825 and
            # spyder-ide/spyder#22901
            self.setWindowFlags(Qt.Tool)
        else:
            self.setWindowFlags(Qt.Window)

    def set_dynamic_width_and_height(self, screen_geometry, width_ratio=0.5,
                                     height_ratio=0.5):
        """
        Update width and height using an updated screen geometry.
        Use a ratio for the width and height of the dialog.
        """
        screen_width = int(screen_geometry.width() * width_ratio)
        screen_height = int(screen_geometry.height() * height_ratio)
        self.resize(screen_width, screen_height)

        # Make the dialog window appear in the center of the screen
        x = int(screen_geometry.center().x() - self.width() / 2)
        y = int(screen_geometry.center().y() - self.height() / 2)
        self.move(x, y)

    def show(self):
        super().show()
        window = self.window()
        windowHandle = window.windowHandle()
        screen = windowHandle.screen()
        geometry = screen.geometry()
        self.set_dynamic_width_and_height(geometry)
        screen.geometryChanged.connect(self.set_dynamic_width_and_height)
