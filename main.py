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
from .actions.DbAction.DbAction import DbAction
from .actions.ModuleAction.ModuleAction import ModuleAction
from .actions.OdooCounter.OdooCounter import OdooCounter
from .actions.OdooWorkflow.OdooWorkflow import OdooWorkflow
from .actions.WebcamAction.WebcamAction import WebcamAction
from .actions.BrightnessAction.BrightnessAction import BrightnessAction
from .actions.KeyboardAction.KeyboardAction import KeyboardAction


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

        # Action: Database operations (restore/drop/list)
        self.db_action_holder = ActionHolder(
            plugin_base=self,
            action_base=DbAction,
            action_id_suffix="DbAction",
            action_name=self.lm.get("actions.db-action.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.db_action_holder)

        # Action: Module install/update
        self.module_action_holder = ActionHolder(
            plugin_base=self,
            action_base=ModuleAction,
            action_id_suffix="ModuleAction",
            action_name=self.lm.get("actions.module-action.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.module_action_holder)

        # Action: Odoo record counter (sales, invoices, tickets...)
        self.odoo_counter_holder = ActionHolder(
            plugin_base=self,
            action_base=OdooCounter,
            action_id_suffix="OdooCounter",
            action_name=self.lm.get("actions.odoo-counter.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.odoo_counter_holder)

        # Action: Odoo workflow trigger (confirm SO, post invoice...)
        self.odoo_workflow_holder = ActionHolder(
            plugin_base=self,
            action_base=OdooWorkflow,
            action_id_suffix="OdooWorkflow",
            action_name=self.lm.get("actions.odoo-workflow.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.odoo_workflow_holder)

        # Action: Webcam feed on button (local or IP)
        self.webcam_holder = ActionHolder(
            plugin_base=self,
            action_base=WebcamAction,
            action_id_suffix="WebcamAction",
            action_name=self.lm.get("actions.webcam.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.webcam_holder)

        # Action: Brightness control
        self.brightness_holder = ActionHolder(
            plugin_base=self,
            action_base=BrightnessAction,
            action_id_suffix="BrightnessAction",
            action_name=self.lm.get("actions.brightness.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.brightness_holder)

        # Action: Keyboard automation (keyboard_talk.py)
        self.keyboard_holder = ActionHolder(
            plugin_base=self,
            action_base=KeyboardAction,
            action_id_suffix="KeyboardAction",
            action_name=self.lm.get("actions.keyboard.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.keyboard_holder)

        self.register(
            plugin_name=self.lm.get("plugin.name"),
            github_repo="https://github.com/ERPLibre/streamcontroller-erplibre",
            plugin_version="0.1.0",
            app_version="1.5.0-beta.6",
        )
