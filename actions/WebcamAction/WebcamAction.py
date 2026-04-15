# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os
import io
import threading
import time

from src.backend.PluginManager.ActionBase import ActionBase

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from PIL import Image

SOURCE_TYPES = ["local", "ip"]
DEFAULT_FPS = 10
DEFAULT_CAMERA_INDEX = 0
DEFAULT_IP_URL = "http://192.168.1.1:8080/shot.jpg"


class WebcamAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self._streaming = False
        self._thread = None
        self._cam = None

    def on_ready(self):
        self.set_background_color([30, 30, 30, 255])
        self.set_center_label("CAM", font_size=16, color=[200, 200, 200])

    def on_key_down(self):
        if self._streaming:
            self._streaming = False
            self.set_background_color([30, 30, 30, 255])
            self.set_center_label("CAM", font_size=16, color=[200, 200, 200])
            return

        settings = self.get_settings()
        source = settings.get("source", "local")

        if source == "local" and not HAS_CV2:
            self.set_center_label("NO CV2", font_size=12, color=[255, 0, 0])
            self.show_error(duration=3)
            return

        if source == "ip" and not HAS_REQUESTS:
            self.set_center_label("NO REQ", font_size=12, color=[255, 0, 0])
            self.show_error(duration=3)
            return

        self._streaming = True
        self._thread = threading.Thread(
            target=self._stream_loop, daemon=True
        )
        self._thread.start()

    def _stream_loop(self):
        settings = self.get_settings()
        source = settings.get("source", "local")
        fps = settings.get("fps", DEFAULT_FPS)
        camera_index = settings.get("camera_index", DEFAULT_CAMERA_INDEX)
        ip_url = settings.get("ip_url", DEFAULT_IP_URL)
        frame_time = 1.0 / max(fps, 1)

        if source == "local":
            self._cam = cv2.VideoCapture(camera_index)
            if not self._cam.isOpened():
                self._streaming = False
                self.set_center_label("ERR", font_size=14, color=[255, 0, 0])
                return

        while self._streaming:
            start = time.monotonic()
            pil_image = None

            try:
                if source == "local" and self._cam is not None:
                    ret, frame = self._cam.read()
                    if ret:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(rgb)
                elif source == "ip":
                    resp = requests.get(ip_url, timeout=2)
                    if resp.status_code == 200:
                        pil_image = Image.open(io.BytesIO(resp.content))
            except Exception:
                pass

            if pil_image is not None:
                try:
                    self.set_media(image=pil_image, size=1)
                except Exception:
                    self._streaming = False
                    break

            elapsed = time.monotonic() - start
            sleep = frame_time - elapsed
            if sleep > 0:
                time.sleep(sleep)

        # Cleanup
        if self._cam is not None:
            self._cam.release()
            self._cam = None

    def on_key_up(self):
        pass

    def get_config_rows(self):
        lm = self.plugin_base.lm
        settings = self.get_settings()

        # Source type
        self.source_combo = Adw.ComboRow(
            title=lm.get("actions.webcam.config.source")
        )
        model = Gtk.StringList()
        for s in SOURCE_TYPES:
            model.append(s)
        self.source_combo.set_model(model)
        current = settings.get("source", "local")
        if current in SOURCE_TYPES:
            self.source_combo.set_selected(SOURCE_TYPES.index(current))
        self.source_combo.connect(
            "notify::selected", self._on_source_changed
        )

        # Camera index
        self.camera_spin = Adw.SpinRow.new_with_range(0, 10, 1)
        self.camera_spin.set_title(
            lm.get("actions.webcam.config.camera-index")
        )
        self.camera_spin.set_value(
            settings.get("camera_index", DEFAULT_CAMERA_INDEX)
        )
        self.camera_spin.connect("notify::value", self._on_camera_changed)

        # IP URL
        self.ip_entry = Adw.EntryRow(
            title=lm.get("actions.webcam.config.ip-url")
        )
        self.ip_entry.set_text(settings.get("ip_url", DEFAULT_IP_URL))
        self.ip_entry.connect("notify::text", self._on_ip_changed)

        # FPS
        self.fps_spin = Adw.SpinRow.new_with_range(1, 30, 1)
        self.fps_spin.set_title(lm.get("actions.webcam.config.fps"))
        self.fps_spin.set_value(settings.get("fps", DEFAULT_FPS))
        self.fps_spin.connect("notify::value", self._on_fps_changed)

        return [
            self.source_combo,
            self.camera_spin,
            self.ip_entry,
            self.fps_spin,
        ]

    def _on_source_changed(self, combo, *args):
        settings = self.get_settings()
        settings["source"] = SOURCE_TYPES[combo.get_selected()]
        self.set_settings(settings)

    def _on_camera_changed(self, spin, *args):
        settings = self.get_settings()
        settings["camera_index"] = int(spin.get_value())
        self.set_settings(settings)

    def _on_ip_changed(self, entry, *args):
        settings = self.get_settings()
        settings["ip_url"] = entry.get_text()
        self.set_settings(settings)

    def _on_fps_changed(self, spin, *args):
        settings = self.get_settings()
        settings["fps"] = int(spin.get_value())
        self.set_settings(settings)
