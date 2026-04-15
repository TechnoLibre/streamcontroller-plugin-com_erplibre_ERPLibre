# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os
import subprocess

from src.backend.PluginManager.ActionBase import ActionBase

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

DEFAULT_ERPLIBRE_PATH = os.path.expanduser("~/erplibre01")


class TodoLauncher(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True

    def on_ready(self):
        self.set_center_label("TODO", font_size=18, color=[255, 255, 255])
        self.set_background_color([40, 40, 120, 255])

    def on_key_down(self):
        settings = self.get_settings()
        erplibre_path = settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        todo_script = os.path.join(erplibre_path, "script", "todo", "source_todo.sh")

        if os.path.isfile(todo_script):
            subprocess.Popen(
                ["gnome-terminal", "--", "bash", "-c", todo_script],
                cwd=erplibre_path,
            )
            self.set_center_label("OK", font_size=18, color=[0, 255, 0])
        else:
            self.set_center_label("ERR", font_size=18, color=[255, 0, 0])
            self.show_error(duration=3)

    def on_key_up(self):
        self.set_center_label("TODO", font_size=18, color=[255, 255, 255])

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        self.path_entry = Adw.EntryRow(
            title=lm.get("actions.todo-launcher.config.erplibre-path")
        )
        self.path_entry.set_text(
            settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        )
        self.path_entry.connect("notify::text", self._on_path_changed)

        return [self.path_entry]

    def _on_path_changed(self, entry, *args):
        settings = self.get_settings()
        settings["erplibre_path"] = entry.get_text()
        self.set_settings(settings)
