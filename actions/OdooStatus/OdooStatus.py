# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os
import xmlrpc.client

from src.backend.PluginManager.ActionBase import ActionBase

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

DEFAULT_URL = "http://localhost:8069"
DEFAULT_DATABASE = "test"


class OdooStatus(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self._is_online = False

    def on_ready(self):
        self._check_status()
        self._update_display()

    def on_tick(self):
        self._check_status()
        self._update_display()

    def on_key_down(self):
        self._check_status()
        self._update_display()

    def _get_url(self):
        settings = self.get_settings()
        return settings.get("url", DEFAULT_URL)

    def _check_status(self):
        url = self._get_url()
        try:
            common = xmlrpc.client.ServerProxy(
                f"{url}/xmlrpc/2/common", allow_none=True
            )
            common.version()
            self._is_online = True
        except Exception:
            self._is_online = False

    def _update_display(self):
        lm = self.plugin_base.lm
        if self._is_online:
            self.set_background_color([0, 120, 0, 255])
            self.set_center_label(
                lm.get("actions.odoo-status.label.online"),
                font_size=16,
                color=[255, 255, 255],
            )
        else:
            self.set_background_color([160, 0, 0, 255])
            self.set_center_label(
                lm.get("actions.odoo-status.label.offline"),
                font_size=16,
                color=[255, 255, 255],
            )

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        self.url_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-status.config.url")
        )
        self.url_entry.set_text(settings.get("url", DEFAULT_URL))
        self.url_entry.connect("notify::text", self._on_url_changed)

        self.db_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-status.config.database")
        )
        self.db_entry.set_text(settings.get("database", DEFAULT_DATABASE))
        self.db_entry.connect("notify::text", self._on_db_changed)

        return [self.url_entry, self.db_entry]

    def _on_url_changed(self, entry, *args):
        settings = self.get_settings()
        settings["url"] = entry.get_text()
        self.set_settings(settings)

    def _on_db_changed(self, entry, *args):
        settings = self.get_settings()
        settings["database"] = entry.get_text()
        self.set_settings(settings)
