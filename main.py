# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os

from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from .actions.OdooStatus.OdooStatus import OdooStatus
from .actions.TodoLauncher.TodoLauncher import TodoLauncher
from .actions.MakeTarget.MakeTarget import MakeTarget


class ERPLibrePlugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.lm = self.locale_manager
        self.lm.set_to_os_default()
        self.lm.set_fallback_language("en_US")

        # Action: Odoo server status indicator
        self.odoo_status_holder = ActionHolder(
            plugin_base=self,
            action_base=OdooStatus,
            action_id_suffix="OdooStatus",
            action_name=self.lm.get("actions.odoo-status.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.odoo_status_holder)

        # Action: Launch todo.py
        self.todo_launcher_holder = ActionHolder(
            plugin_base=self,
            action_base=TodoLauncher,
            action_id_suffix="TodoLauncher",
            action_name=self.lm.get("actions.todo-launcher.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.todo_launcher_holder)

        # Action: Run Makefile target
        self.make_target_holder = ActionHolder(
            plugin_base=self,
            action_base=MakeTarget,
            action_id_suffix="MakeTarget",
            action_name=self.lm.get("actions.make-target.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.make_target_holder)

        self.register(
            plugin_name=self.lm.get("plugin.name"),
            github_repo="https://github.com/ERPLibre/streamcontroller-erplibre",
            plugin_version="0.1.0",
            app_version="1.5.0-beta.6",
        )
