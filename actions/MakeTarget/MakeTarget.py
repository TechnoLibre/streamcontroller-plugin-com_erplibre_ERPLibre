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
DEFAULT_TARGET = "run"


class MakeTarget(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self._running = False

    def on_ready(self):
        settings = self.get_settings()
        target = settings.get("target", DEFAULT_TARGET)
        self.set_center_label(target, font_size=14, color=[255, 255, 255])
        self.set_background_color([60, 60, 60, 255])

    def on_key_down(self):
        if self._running:
            return

        settings = self.get_settings()
        erplibre_path = settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        target = settings.get("target", DEFAULT_TARGET)

        makefile = os.path.join(erplibre_path, "Makefile")
        if not os.path.isfile(makefile):
            self.set_center_label("ERR", font_size=14, color=[255, 0, 0])
            self.show_error(duration=3)
            return

        self._running = True
        self.set_background_color([0, 80, 160, 255])
        self.set_center_label(target, font_size=14, color=[200, 255, 200])

        subprocess.Popen(
            ["gnome-terminal", "--", "bash", "-c", f"make {target}; bash"],
            cwd=erplibre_path,
        )
        self._running = False

    def on_key_up(self):
        settings = self.get_settings()
        target = settings.get("target", DEFAULT_TARGET)
        self.set_center_label(target, font_size=14, color=[255, 255, 255])
        self.set_background_color([60, 60, 60, 255])

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        self.target_entry = Adw.EntryRow(
            title=lm.get("actions.make-target.config.target")
        )
        self.target_entry.set_text(settings.get("target", DEFAULT_TARGET))
        self.target_entry.connect("notify::text", self._on_target_changed)

        self.path_entry = Adw.EntryRow(
            title=lm.get("actions.make-target.config.erplibre-path")
        )
        self.path_entry.set_text(
            settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        )
        self.path_entry.connect("notify::text", self._on_path_changed)

        return [self.target_entry, self.path_entry]

    def _on_target_changed(self, entry, *args):
        settings = self.get_settings()
        settings["target"] = entry.get_text()
        self.set_settings(settings)

    def _on_path_changed(self, entry, *args):
        settings = self.get_settings()
        settings["erplibre_path"] = entry.get_text()
        self.set_settings(settings)
