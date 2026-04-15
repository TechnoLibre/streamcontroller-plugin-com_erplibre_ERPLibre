# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
import os

from src.backend.PluginManager.ActionBase import ActionBase

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from api.odoo_rpc import OdooRPC

DEFAULT_URL = "http://localhost:8069"
DEFAULT_DATABASE = "test"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

PRESETS = {
    "sale_order": {
        "model": "sale.order",
        "domain": [["state", "=", "sale"]],
        "label": "SO",
        "color": [0, 100, 160, 255],
    },
    "invoice": {
        "model": "account.move",
        "domain": [["move_type", "=", "out_invoice"], ["state", "=", "posted"]],
        "label": "INV",
        "color": [0, 120, 60, 255],
    },
    "draft_invoice": {
        "model": "account.move",
        "domain": [["move_type", "=", "out_invoice"], ["state", "=", "draft"]],
        "label": "DINV",
        "color": [160, 120, 0, 255],
    },
    "purchase_order": {
        "model": "purchase.order",
        "domain": [["state", "=", "purchase"]],
        "label": "PO",
        "color": [120, 0, 120, 255],
    },
    "helpdesk_ticket": {
        "model": "helpdesk.ticket",
        "domain": [["stage_id.fold", "=", False]],
        "label": "TIX",
        "color": [160, 60, 0, 255],
    },
    "crm_lead": {
        "model": "crm.lead",
        "domain": [["type", "=", "opportunity"], ["active", "=", True]],
        "label": "CRM",
        "color": [0, 80, 80, 255],
    },
    "project_task": {
        "model": "project.task",
        "domain": [["stage_id.fold", "=", False]],
        "label": "TASK",
        "color": [80, 60, 120, 255],
    },
    "custom": {
        "model": "",
        "domain": [],
        "label": "?",
        "color": [80, 80, 80, 255],
    },
}

PRESET_NAMES = list(PRESETS.keys())


class OdooCounter(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self._count = None
        self._rpc = None

    def _get_rpc(self):
        settings = self.get_settings()
        url = settings.get("url", DEFAULT_URL)
        database = settings.get("database", DEFAULT_DATABASE)
        username = settings.get("username", DEFAULT_USERNAME)
        password = settings.get("password", DEFAULT_PASSWORD)

        if (
            self._rpc is None
            or self._rpc.url != url
            or self._rpc.database != database
            or self._rpc.username != username
        ):
            self._rpc = OdooRPC(url, database, username, password)

        return self._rpc

    def _get_preset(self):
        settings = self.get_settings()
        preset_name = settings.get("preset", "sale_order")
        return PRESETS.get(preset_name, PRESETS["custom"])

    def on_ready(self):
        self._refresh()

    def on_tick(self):
        self._refresh()

    def on_key_down(self):
        self._rpc = None
        self._refresh()

    def _refresh(self):
        settings = self.get_settings()
        preset = self._get_preset()
        preset_name = settings.get("preset", "sale_order")

        if preset_name == "custom":
            model = settings.get("custom_model", "")
            label = settings.get("custom_label", "?")
            bg = [80, 80, 80, 255]
        else:
            model = preset["model"]
            label = preset["label"]
            bg = preset["color"]

        if not model:
            self.set_background_color([80, 80, 80, 255])
            self.set_top_label(label, font_size=12, color=[255, 255, 255])
            self.set_center_label("N/A", font_size=16, color=[200, 200, 200])
            return

        rpc = self._get_rpc()

        if preset_name == "custom":
            domain_str = settings.get("custom_domain", "[]")
            try:
                domain = json.loads(domain_str)
            except (json.JSONDecodeError, ValueError):
                domain = []
        else:
            domain = preset["domain"]

        count = rpc.search_count(model, domain)

        if count is not None:
            self._count = count
            self.set_background_color(bg)
            self.set_top_label(label, font_size=12, color=[255, 255, 255])
            self.set_center_label(
                str(count), font_size=24, color=[255, 255, 255]
            )
        else:
            self.set_background_color([100, 0, 0, 255])
            self.set_top_label(label, font_size=12, color=[255, 255, 255])
            self.set_center_label("ERR", font_size=16, color=[255, 100, 100])

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        # Preset selector
        self.preset_combo = Adw.ComboRow(
            title=lm.get("actions.odoo-counter.config.preset")
        )
        model = Gtk.StringList()
        for name in PRESET_NAMES:
            model.append(name)
        self.preset_combo.set_model(model)
        current = settings.get("preset", "sale_order")
        if current in PRESET_NAMES:
            self.preset_combo.set_selected(PRESET_NAMES.index(current))
        self.preset_combo.connect(
            "notify::selected", self._on_preset_changed
        )

        # URL
        self.url_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-counter.config.url")
        )
        self.url_entry.set_text(settings.get("url", DEFAULT_URL))
        self.url_entry.connect("notify::text", self._on_url_changed)

        # Database
        self.db_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-counter.config.database")
        )
        self.db_entry.set_text(settings.get("database", DEFAULT_DATABASE))
        self.db_entry.connect("notify::text", self._on_db_changed)

        # Username
        self.user_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-counter.config.username")
        )
        self.user_entry.set_text(settings.get("username", DEFAULT_USERNAME))
        self.user_entry.connect("notify::text", self._on_user_changed)

        # Password
        self.pass_entry = Adw.PasswordEntryRow(
            title=lm.get("actions.odoo-counter.config.password")
        )
        self.pass_entry.set_text(settings.get("password", DEFAULT_PASSWORD))
        self.pass_entry.connect("notify::text", self._on_pass_changed)

        # Custom model
        self.custom_model_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-counter.config.custom-model")
        )
        self.custom_model_entry.set_text(
            settings.get("custom_model", "")
        )
        self.custom_model_entry.connect(
            "notify::text", self._on_custom_model_changed
        )

        # Custom label
        self.custom_label_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-counter.config.custom-label")
        )
        self.custom_label_entry.set_text(
            settings.get("custom_label", "?")
        )
        self.custom_label_entry.connect(
            "notify::text", self._on_custom_label_changed
        )

        # Custom domain (JSON format)
        self.custom_domain_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-counter.config.custom-domain")
        )
        self.custom_domain_entry.set_text(
            settings.get("custom_domain", "[]")
        )
        self.custom_domain_entry.connect(
            "notify::text", self._on_custom_domain_changed
        )

        return [
            self.preset_combo,
            self.url_entry,
            self.db_entry,
            self.user_entry,
            self.pass_entry,
            self.custom_model_entry,
            self.custom_label_entry,
            self.custom_domain_entry,
        ]

    def _on_preset_changed(self, combo, *args):
        settings = self.get_settings()
        settings["preset"] = PRESET_NAMES[combo.get_selected()]
        self.set_settings(settings)

    def _on_url_changed(self, entry, *args):
        settings = self.get_settings()
        settings["url"] = entry.get_text()
        self.set_settings(settings)
        self._rpc = None

    def _on_db_changed(self, entry, *args):
        settings = self.get_settings()
        settings["database"] = entry.get_text()
        self.set_settings(settings)
        self._rpc = None

    def _on_user_changed(self, entry, *args):
        settings = self.get_settings()
        settings["username"] = entry.get_text()
        self.set_settings(settings)
        self._rpc = None

    def _on_pass_changed(self, entry, *args):
        settings = self.get_settings()
        settings["password"] = entry.get_text()
        self.set_settings(settings)
        self._rpc = None

    def _on_custom_model_changed(self, entry, *args):
        settings = self.get_settings()
        settings["custom_model"] = entry.get_text()
        self.set_settings(settings)

    def _on_custom_label_changed(self, entry, *args):
        settings = self.get_settings()
        settings["custom_label"] = entry.get_text()
        self.set_settings(settings)

    def _on_custom_domain_changed(self, entry, *args):
        settings = self.get_settings()
        settings["custom_domain"] = entry.get_text()
        self.set_settings(settings)
