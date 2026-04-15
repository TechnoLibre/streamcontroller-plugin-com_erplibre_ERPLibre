# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from src.backend.PluginManager.ActionBase import ActionBase

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

DEFAULT_STEP = 10
DEFAULT_DIRECTION = "up"
DIRECTIONS = ["up", "down"]


class BrightnessAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True

    def on_ready(self):
        self._update_label()

    def on_key_down(self):
        settings = self.get_settings()
        direction = settings.get("direction", DEFAULT_DIRECTION)
        step = settings.get("step", DEFAULT_STEP)

        key = self.get_own_key()
        if key is None:
            return

        controller = key.controller_input.deck_controller
        deck = controller.deck

        try:
            current = deck.get_brightness()
        except Exception:
            current = 50

        if direction == "up":
            new = min(100, current + step)
        else:
            new = max(5, current - step)

        try:
            deck.set_brightness(new)
        except Exception:
            self.show_error(duration=2)
            return

        self.set_center_label(
            f"{new}%", font_size=16, color=[255, 255, 255]
        )

    def on_key_up(self):
        self._update_label()

    def _update_label(self):
        settings = self.get_settings()
        direction = settings.get("direction", DEFAULT_DIRECTION)

        if direction == "up":
            self.set_background_color([80, 80, 0, 255])
            self.set_center_label(
                "BRT+", font_size=14, color=[255, 255, 200]
            )
        else:
            self.set_background_color([40, 40, 0, 255])
            self.set_center_label(
                "BRT-", font_size=14, color=[200, 200, 150]
            )

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        # Direction
        self.direction_combo = Adw.ComboRow(
            title=lm.get("actions.brightness.config.direction")
        )
        model = Gtk.StringList()
        for d in DIRECTIONS:
            model.append(d)
        self.direction_combo.set_model(model)
        current = settings.get("direction", DEFAULT_DIRECTION)
        if current in DIRECTIONS:
            self.direction_combo.set_selected(DIRECTIONS.index(current))
        self.direction_combo.connect(
            "notify::selected", self._on_direction_changed
        )

        # Step
        self.step_spin = Adw.SpinRow.new_with_range(5, 50, 5)
        self.step_spin.set_title(
            lm.get("actions.brightness.config.step")
        )
        self.step_spin.set_value(settings.get("step", DEFAULT_STEP))
        self.step_spin.connect("notify::value", self._on_step_changed)

        return [self.direction_combo, self.step_spin]

    def _on_direction_changed(self, combo, *args):
        settings = self.get_settings()
        settings["direction"] = DIRECTIONS[combo.get_selected()]
        self.set_settings(settings)
        self._update_label()

    def _on_step_changed(self, spin, *args):
        settings = self.get_settings()
        settings["step"] = int(spin.get_value())
        self.set_settings(settings)
