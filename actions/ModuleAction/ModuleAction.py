# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os
import subprocess
import threading

from src.backend.PluginManager.ActionBase import ActionBase

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

DEFAULT_ERPLIBRE_PATH = os.path.expanduser("~/erplibre01")
DEFAULT_DATABASE = "test"
DEFAULT_MODULE = ""

MODULE_OPERATIONS = [
    "install",
    "update",
    "update_all",
]


class ModuleAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self._running = False

    def on_ready(self):
        self._update_label()

    def on_key_down(self):
        if self._running:
            return

        settings = self.get_settings()
        erplibre_path = settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        database = settings.get("database", DEFAULT_DATABASE)
        module = settings.get("module", DEFAULT_MODULE)
        operation = settings.get("operation", "install")

        if operation in ("install", "update") and not module:
            self.set_center_label("ERR", font_size=14, color=[255, 0, 0])
            self.show_error(duration=3)
            return

        if operation == "install":
            cmd = f"./script/addons/install_addons_dev.sh {database} {module}"
        elif operation == "update":
            cmd = (
                f"./run.sh --no-http --stop-after-init"
                f" -d {database} -u {module}"
            )
        elif operation == "update_all":
            cmd = f"./script/addons/update_addons_all.sh {database}"
        else:
            return

        self._running = True
        self.set_background_color([200, 120, 0, 255])
        self.set_center_label("...", font_size=14, color=[255, 255, 255])

        def _run():
            try:
                subprocess.Popen(
                    [
                        "gnome-terminal",
                        "--",
                        "bash",
                        "-c",
                        f"cd {erplibre_path} && {cmd}; echo ''; echo 'Press enter to close...'; read",
                    ],
                )
            finally:
                self._running = False
                self._update_label()

        threading.Thread(target=_run, daemon=True).start()

    def on_key_up(self):
        if not self._running:
            self._update_label()

    def _update_label(self):
        settings = self.get_settings()
        operation = settings.get("operation", "install")
        module = settings.get("module", DEFAULT_MODULE)

        label_map = {
            "install": "INST",
            "update": "UPD",
            "update_all": "UPD*",
        }
        label = label_map.get(operation, operation[:4].upper())

        color_map = {
            "install": [0, 80, 160, 255],
            "update": [80, 80, 0, 255],
            "update_all": [120, 60, 0, 255],
        }
        bg = color_map.get(operation, [60, 60, 60, 255])

        self.set_background_color(bg)
        self.set_top_label(label, font_size=14, color=[255, 255, 255])
        display = module if module else "all"
        self.set_center_label(display, font_size=11, color=[200, 200, 200])

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        # Operation selector
        self.operation_combo = Adw.ComboRow(
            title=lm.get("actions.module-action.config.operation")
        )
        model = Gtk.StringList()
        for op in MODULE_OPERATIONS:
            model.append(op)
        self.operation_combo.set_model(model)
        current_op = settings.get("operation", "install")
        if current_op in MODULE_OPERATIONS:
            self.operation_combo.set_selected(
                MODULE_OPERATIONS.index(current_op)
            )
        self.operation_combo.connect(
            "notify::selected", self._on_operation_changed
        )

        # Module name
        self.module_entry = Adw.EntryRow(
            title=lm.get("actions.module-action.config.module")
        )
        self.module_entry.set_text(settings.get("module", DEFAULT_MODULE))
        self.module_entry.connect("notify::text", self._on_module_changed)

        # Database name
        self.db_entry = Adw.EntryRow(
            title=lm.get("actions.module-action.config.database")
        )
        self.db_entry.set_text(settings.get("database", DEFAULT_DATABASE))
        self.db_entry.connect("notify::text", self._on_db_changed)

        # ERPLibre path
        self.path_entry = Adw.EntryRow(
            title=lm.get("actions.module-action.config.erplibre-path")
        )
        self.path_entry.set_text(
            settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        )
        self.path_entry.connect("notify::text", self._on_path_changed)

        return [
            self.operation_combo,
            self.module_entry,
            self.db_entry,
            self.path_entry,
        ]

    def _on_operation_changed(self, combo, *args):
        settings = self.get_settings()
        settings["operation"] = MODULE_OPERATIONS[combo.get_selected()]
        self.set_settings(settings)
        self._update_label()

    def _on_module_changed(self, entry, *args):
        settings = self.get_settings()
        settings["module"] = entry.get_text()
        self.set_settings(settings)
        self._update_label()

    def _on_db_changed(self, entry, *args):
        settings = self.get_settings()
        settings["database"] = entry.get_text()
        self.set_settings(settings)

    def _on_path_changed(self, entry, *args):
        settings = self.get_settings()
        settings["erplibre_path"] = entry.get_text()
        self.set_settings(settings)
