#!/usr/bin/env python

import logging
import os

from gi.repository import Gtk, Gdk


from gaphor.action import action
from gaphor.misc import get_config_dir
from gaphor.abc import ActionProvider
from gaphor.ui.abc import UIComponent
from gaphor.misc.console import GTKInterpreterConsole

log = logging.getLogger(__name__)


class ConsoleWindow(UIComponent, ActionProvider):

    title = "Gaphor Console"
    size = (400, 400)

    def __init__(self, component_registry, main_window, tools_menu):
        self.component_registry = component_registry
        self.main_window = main_window
        tools_menu.add_actions(self)
        self.window = None

    def load_console_py(self, console):
        """Load default script for console. Saves some repetitive typing."""

        console_py = os.path.join(get_config_dir(), "console.py")
        try:
            with open(console_py) as f:
                for line in f:
                    console.push(line)
        except OSError:
            log.info(f"No initiation script {console_py}")

    @action(name="console-window-open", label="_Console")
    def open_console(self):
        if not self.window:
            self.open()
        else:
            self.window.set_property("has-focus", True)

    def open(self):
        console = self.construct()
        self.load_console_py(console)

    # @action(
    #     name="console-window-close",
    #     label="_Close",
    #     icon_name="window-close",
    #     accel="<Primary><Shift>w",
    # )
    def close(self, widget=None):
        if self.window:
            self.window.destroy()
            self.window = None

    def construct(self):
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.main_window.window)
        window.set_title(self.title)

        console = GTKInterpreterConsole(
            locals={"service": self.component_registry.get_service}
        )
        console.show()
        window.add(console)
        window.show()

        self.window = window

        def key_event(widget, event):
            if (
                event.keyval == Gdk.KEY_d
                and event.get_state() & Gdk.ModifierType.CONTROL_MASK
            ):
                window.destroy()
            return False

        window.connect("key_press_event", key_event)

        window.connect("destroy", self.close)

        return console
