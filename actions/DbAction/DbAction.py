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

DB_OPERATIONS = [
    "restore",
    "drop",
    "list",
]


class DbAction(ActionBase):
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
        operation = settings.get("operation", "restore")
        image = settings.get("image", "")

        if operation == "restore":
            cmd = f"./script/database/db_restore.py --database {database}"
            if image:
                cmd += f" --image {image}"
        elif operation == "drop":
            cmd = f"./odoo_bin.sh db --drop --database {database}"
        elif operation == "list":
            cmd = "./odoo_bin.sh db --list"
        else:
            return

        self._running = True
        self.set_background_color([200, 120, 0, 255])
        self.set_center_label("...", font_size=16, color=[255, 255, 255])

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
        operation = settings.get("operation", "restore")
        database = settings.get("database", DEFAULT_DATABASE)

        label_map = {
            "restore": "RST",
            "drop": "DROP",
            "list": "LIST",
        }
        label = label_map.get(operation, operation[:4].upper())

        color_map = {
            "restore": [0, 100, 60, 255],
            "drop": [160, 0, 0, 255],
            "list": [60, 60, 120, 255],
        }
        bg = color_map.get(operation, [60, 60, 60, 255])

        self.set_background_color(bg)
        self.set_top_label(label, font_size=14, color=[255, 255, 255])
        self.set_center_label(database, font_size=12, color=[200, 200, 200])

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        # Operation selector
        self.operation_combo = Adw.ComboRow(
            title=lm.get("actions.db-action.config.operation")
        )
        model = Gtk.StringList()
        for op in DB_OPERATIONS:
            model.append(op)
        self.operation_combo.set_model(model)
        current_op = settings.get("operation", "restore")
        if current_op in DB_OPERATIONS:
            self.operation_combo.set_selected(DB_OPERATIONS.index(current_op))
        self.operation_combo.connect(
            "notify::selected", self._on_operation_changed
        )

        # Database name
        self.db_entry = Adw.EntryRow(
            title=lm.get("actions.db-action.config.database")
        )
        self.db_entry.set_text(settings.get("database", DEFAULT_DATABASE))
        self.db_entry.connect("notify::text", self._on_db_changed)

        # Image name (for restore)
        self.image_entry = Adw.EntryRow(
            title=lm.get("actions.db-action.config.image")
        )
        self.image_entry.set_text(settings.get("image", ""))
        self.image_entry.connect("notify::text", self._on_image_changed)

        # ERPLibre path
        self.path_entry = Adw.EntryRow(
            title=lm.get("actions.db-action.config.erplibre-path")
        )
        self.path_entry.set_text(
            settings.get("erplibre_path", DEFAULT_ERPLIBRE_PATH)
        )
        self.path_entry.connect("notify::text", self._on_path_changed)

        return [
            self.operation_combo,
            self.db_entry,
            self.image_entry,
            self.path_entry,
        ]

    def _on_operation_changed(self, combo, *args):
        settings = self.get_settings()
        settings["operation"] = DB_OPERATIONS[combo.get_selected()]
        self.set_settings(settings)
        self._update_label()

    def _on_db_changed(self, entry, *args):
        settings = self.get_settings()
        settings["database"] = entry.get_text()
        self.set_settings(settings)
        self._update_label()

    def _on_image_changed(self, entry, *args):
        settings = self.get_settings()
        settings["image"] = entry.get_text()
        self.set_settings(settings)

    def _on_path_changed(self, entry, *args):
        settings = self.get_settings()
        settings["erplibre_path"] = entry.get_text()
        self.set_settings(settings)
