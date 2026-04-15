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
    "confirm_sale": {
        "model": "sale.order",
        "method": "action_confirm",
        "domain": [["state", "=", "draft"]],
        "label": "Confirm SO",
        "short": "CSO",
        "color": [0, 100, 60, 255],
    },
    "confirm_purchase": {
        "model": "purchase.order",
        "method": "button_confirm",
        "domain": [["state", "=", "draft"]],
        "label": "Confirm PO",
        "short": "CPO",
        "color": [100, 0, 100, 255],
    },
    "validate_invoice": {
        "model": "account.move",
        "method": "action_post",
        "domain": [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "draft"],
        ],
        "label": "Post Invoice",
        "short": "PINV",
        "color": [0, 120, 60, 255],
    },
    "cancel_sale": {
        "model": "sale.order",
        "method": "_action_cancel",
        "domain": [["state", "=", "draft"]],
        "label": "Cancel SO",
        "short": "XSO",
        "color": [160, 0, 0, 255],
    },
    "custom": {
        "model": "",
        "method": "",
        "domain": [],
        "label": "Custom",
        "short": "?",
        "color": [80, 80, 80, 255],
    },
}

PRESET_NAMES = list(PRESETS.keys())


class OdooWorkflow(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self._rpc = None
        self._running = False

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
        preset_name = settings.get("preset", "confirm_sale")
        return PRESETS.get(preset_name, PRESETS["custom"])

    def on_ready(self):
        self._update_display()

    def on_tick(self):
        self._update_display()

    def _update_display(self):
        settings = self.get_settings()
        preset = self._get_preset()
        preset_name = settings.get("preset", "confirm_sale")

        if preset_name == "custom":
            label = settings.get("custom_label", "?")
            bg = [80, 80, 80, 255]
            model = settings.get("custom_model", "")
            domain_str = settings.get("custom_domain", "[]")
            try:
                domain = json.loads(domain_str)
            except (json.JSONDecodeError, ValueError):
                domain = []
        else:
            label = preset["short"]
            bg = preset["color"]
            model = preset["model"]
            domain = preset["domain"]

        if not model:
            self.set_background_color(bg)
            self.set_center_label(label, font_size=14, color=[255, 255, 255])
            return

        rpc = self._get_rpc()
        count = rpc.search_count(model, domain)

        self.set_background_color(bg)
        self.set_top_label(label, font_size=11, color=[255, 255, 255])
        if count is not None:
            self.set_center_label(
                str(count), font_size=20, color=[255, 255, 255]
            )
        else:
            self.set_center_label("?", font_size=20, color=[200, 200, 200])

    def on_key_down(self):
        if self._running:
            return

        self._running = True
        settings = self.get_settings()
        preset = self._get_preset()
        preset_name = settings.get("preset", "confirm_sale")

        if preset_name == "custom":
            model = settings.get("custom_model", "")
            method = settings.get("custom_method", "")
            domain_str = settings.get("custom_domain", "[]")
            try:
                domain = json.loads(domain_str)
            except (json.JSONDecodeError, ValueError):
                domain = []
        else:
            model = preset["model"]
            method = preset["method"]
            domain = preset["domain"]

        if not model or not method:
            self._running = False
            self.show_error(duration=2)
            return

        self.set_background_color([200, 120, 0, 255])
        self.set_center_label("...", font_size=16, color=[255, 255, 255])

        rpc = self._get_rpc()

        # Find matching records
        records = rpc.search_read(model, domain, fields=["id"], limit=0)
        if not records:
            self.set_center_label("0", font_size=16, color=[200, 200, 200])
            self._running = False
            self._update_display()
            return

        record_ids = [r["id"] for r in records]
        result = rpc.execute(model, method, record_ids)

        if result is not None and not isinstance(result, dict):
            self.set_background_color([0, 160, 0, 255])
            self.set_center_label(
                f"OK:{len(record_ids)}", font_size=12, color=[255, 255, 255]
            )
        elif isinstance(result, dict) and "error" in result:
            self.set_background_color([160, 0, 0, 255])
            self.set_center_label("FAIL", font_size=14, color=[255, 255, 255])
        else:
            self.set_background_color([0, 160, 0, 255])
            self.set_center_label(
                f"OK:{len(record_ids)}", font_size=12, color=[255, 255, 255]
            )

        self._running = False

    def on_key_up(self):
        self._update_display()

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        # Preset selector
        self.preset_combo = Adw.ComboRow(
            title=lm.get("actions.odoo-workflow.config.preset")
        )
        model = Gtk.StringList()
        for name in PRESET_NAMES:
            model.append(name)
        self.preset_combo.set_model(model)
        current = settings.get("preset", "confirm_sale")
        if current in PRESET_NAMES:
            self.preset_combo.set_selected(PRESET_NAMES.index(current))
        self.preset_combo.connect(
            "notify::selected", self._on_preset_changed
        )

        # URL
        self.url_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.url")
        )
        self.url_entry.set_text(settings.get("url", DEFAULT_URL))
        self.url_entry.connect("notify::text", self._on_url_changed)

        # Database
        self.db_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.database")
        )
        self.db_entry.set_text(settings.get("database", DEFAULT_DATABASE))
        self.db_entry.connect("notify::text", self._on_db_changed)

        # Username
        self.user_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.username")
        )
        self.user_entry.set_text(settings.get("username", DEFAULT_USERNAME))
        self.user_entry.connect("notify::text", self._on_user_changed)

        # Password
        self.pass_entry = Adw.PasswordEntryRow(
            title=lm.get("actions.odoo-workflow.config.password")
        )
        self.pass_entry.set_text(settings.get("password", DEFAULT_PASSWORD))
        self.pass_entry.connect("notify::text", self._on_pass_changed)

        # Custom model
        self.custom_model_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.custom-model")
        )
        self.custom_model_entry.set_text(
            settings.get("custom_model", "")
        )
        self.custom_model_entry.connect(
            "notify::text", self._on_custom_model_changed
        )

        # Custom method
        self.custom_method_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.custom-method")
        )
        self.custom_method_entry.set_text(
            settings.get("custom_method", "")
        )
        self.custom_method_entry.connect(
            "notify::text", self._on_custom_method_changed
        )

        # Custom label
        self.custom_label_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.custom-label")
        )
        self.custom_label_entry.set_text(
            settings.get("custom_label", "?")
        )
        self.custom_label_entry.connect(
            "notify::text", self._on_custom_label_changed
        )

        # Custom domain (JSON)
        self.custom_domain_entry = Adw.EntryRow(
            title=lm.get("actions.odoo-workflow.config.custom-domain")
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
            self.custom_method_entry,
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

    def _on_custom_method_changed(self, entry, *args):
        settings = self.get_settings()
        settings["custom_method"] = entry.get_text()
        self.set_settings(settings)

    def _on_custom_label_changed(self, entry, *args):
        settings = self.get_settings()
        settings["custom_label"] = entry.get_text()
        self.set_settings(settings)

    def _on_custom_domain_changed(self, entry, *args):
        settings = self.get_settings()
        settings["custom_domain"] = entry.get_text()
        self.set_settings(settings)
