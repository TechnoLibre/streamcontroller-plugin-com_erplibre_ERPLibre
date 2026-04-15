# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
import os
import unittest

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..")


class TestPluginManifest(unittest.TestCase):
    def test_manifest_exists(self):
        path = os.path.join(PLUGIN_DIR, "manifest.json")
        self.assertTrue(os.path.isfile(path))

    def test_manifest_valid_json(self):
        path = os.path.join(PLUGIN_DIR, "manifest.json")
        with open(path) as f:
            data = json.load(f)
        self.assertIn("id", data)
        self.assertIn("version", data)
        self.assertIn("name", data)
        self.assertIn("github", data)

    def test_manifest_has_descriptions(self):
        path = os.path.join(PLUGIN_DIR, "manifest.json")
        with open(path) as f:
            data = json.load(f)
        self.assertIn("descriptions", data)
        self.assertIn("en_US", data["descriptions"])
        self.assertIn("fr_FR", data["descriptions"])

    def test_manifest_has_short_descriptions(self):
        path = os.path.join(PLUGIN_DIR, "manifest.json")
        with open(path) as f:
            data = json.load(f)
        self.assertIn("short-descriptions", data)
        self.assertIn("en_US", data["short-descriptions"])


class TestPluginRequiredFiles(unittest.TestCase):
    def test_main_py_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN_DIR, "main.py")))

    def test_attribution_exists(self):
        path = os.path.join(PLUGIN_DIR, "attribution.json")
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            data = json.load(f)
        self.assertIn("generic", data)

    def test_about_exists(self):
        path = os.path.join(PLUGIN_DIR, "about.json")
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            data = json.load(f)
        self.assertIn("author", data)


class TestLocales(unittest.TestCase):
    def setUp(self):
        en_path = os.path.join(PLUGIN_DIR, "locales", "en_US.json")
        fr_path = os.path.join(PLUGIN_DIR, "locales", "fr_FR.json")
        with open(en_path) as f:
            self.en = json.load(f)
        with open(fr_path) as f:
            self.fr = json.load(f)

    def test_locales_exist(self):
        self.assertTrue(len(self.en) > 0)
        self.assertTrue(len(self.fr) > 0)

    def test_same_keys(self):
        en_keys = set(self.en.keys())
        fr_keys = set(self.fr.keys())
        missing_in_fr = en_keys - fr_keys
        missing_in_en = fr_keys - en_keys
        self.assertEqual(
            missing_in_fr, set(), f"Keys missing in fr_FR: {missing_in_fr}"
        )
        self.assertEqual(
            missing_in_en, set(), f"Keys missing in en_US: {missing_in_en}"
        )

    def test_no_empty_values(self):
        for key, value in self.en.items():
            self.assertTrue(
                len(value.strip()) > 0, f"Empty en_US value for '{key}'"
            )
        for key, value in self.fr.items():
            self.assertTrue(
                len(value.strip()) > 0, f"Empty fr_FR value for '{key}'"
            )


class TestActionStructure(unittest.TestCase):
    EXPECTED_ACTIONS = [
        "OdooStatus",
        "OdooCounter",
        "OdooWorkflow",
        "TodoLauncher",
        "MakeTarget",
        "DbAction",
        "ModuleAction",
        "WebcamAction",
        "BrightnessAction",
        "KeyboardAction",
    ]

    def test_all_actions_have_directory(self):
        actions_dir = os.path.join(PLUGIN_DIR, "actions")
        for action in self.EXPECTED_ACTIONS:
            action_dir = os.path.join(actions_dir, action)
            self.assertTrue(
                os.path.isdir(action_dir), f"Missing action dir: {action}"
            )

    def test_all_actions_have_py_file(self):
        actions_dir = os.path.join(PLUGIN_DIR, "actions")
        for action in self.EXPECTED_ACTIONS:
            py_file = os.path.join(actions_dir, action, f"{action}.py")
            self.assertTrue(
                os.path.isfile(py_file), f"Missing file: {py_file}"
            )

    def test_action_files_compile(self):
        actions_dir = os.path.join(PLUGIN_DIR, "actions")
        for action in self.EXPECTED_ACTIONS:
            py_file = os.path.join(actions_dir, action, f"{action}.py")
            with open(py_file) as f:
                source = f.read()
            try:
                compile(source, py_file, "exec")
            except SyntaxError as e:
                self.fail(f"Syntax error in {action}: {e}")

    def test_main_py_compiles(self):
        main_file = os.path.join(PLUGIN_DIR, "main.py")
        with open(main_file) as f:
            source = f.read()
        try:
            compile(source, main_file, "exec")
        except SyntaxError as e:
            self.fail(f"Syntax error in main.py: {e}")

    def test_api_odoo_rpc_compiles(self):
        rpc_file = os.path.join(PLUGIN_DIR, "api", "odoo_rpc.py")
        with open(rpc_file) as f:
            source = f.read()
        try:
            compile(source, rpc_file, "exec")
        except SyntaxError as e:
            self.fail(f"Syntax error in odoo_rpc.py: {e}")


if __name__ == "__main__":
    unittest.main()
