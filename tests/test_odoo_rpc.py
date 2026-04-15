# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import unittest
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from api.odoo_rpc import OdooRPC


class TestOdooRPCInit(unittest.TestCase):
    def test_init_stores_params(self):
        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        self.assertEqual(rpc.url, "http://localhost:8069")
        self.assertEqual(rpc.database, "test")
        self.assertEqual(rpc.username, "admin")
        self.assertEqual(rpc.password, "admin")
        self.assertIsNone(rpc._uid)

    def test_init_strips_trailing_slash(self):
        rpc = OdooRPC("http://localhost:8069/", "test", "admin", "admin")
        self.assertEqual(rpc.url, "http://localhost:8069")


class TestOdooRPCAuthenticate(unittest.TestCase):
    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_authenticate_success(self, mock_proxy_cls):
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 2
        mock_proxy_cls.return_value = mock_common

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        uid = rpc.authenticate()

        self.assertEqual(uid, 2)
        self.assertEqual(rpc._uid, 2)
        mock_common.authenticate.assert_called_once_with(
            "test", "admin", "admin", {}
        )

    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_authenticate_failure(self, mock_proxy_cls):
        mock_common = MagicMock()
        mock_common.authenticate.side_effect = ConnectionRefusedError
        mock_proxy_cls.return_value = mock_common

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        uid = rpc.authenticate()

        self.assertIsNone(uid)
        self.assertIsNone(rpc._uid)


class TestOdooRPCSearchCount(unittest.TestCase):
    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_search_count_success(self, mock_proxy_cls):
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = 2
        mock_proxy.execute_kw.return_value = 42
        mock_proxy_cls.return_value = mock_proxy

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        count = rpc.search_count("sale.order", [["state", "=", "sale"]])

        self.assertEqual(count, 42)

    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_search_count_no_auth(self, mock_proxy_cls):
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = None
        mock_proxy_cls.return_value = mock_proxy

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "wrong")
        count = rpc.search_count("sale.order")

        self.assertIsNone(count)

    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_search_count_default_domain(self, mock_proxy_cls):
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = 2
        mock_proxy.execute_kw.return_value = 10
        mock_proxy_cls.return_value = mock_proxy

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        count = rpc.search_count("res.partner")

        self.assertEqual(count, 10)
        mock_proxy.execute_kw.assert_called_once_with(
            "test", 2, "admin", "res.partner", "search_count", [[]]
        )


class TestOdooRPCSearchRead(unittest.TestCase):
    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_search_read_success(self, mock_proxy_cls):
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = 2
        mock_proxy.execute_kw.return_value = [
            {"id": 1, "name": "SO001"},
            {"id": 2, "name": "SO002"},
        ]
        mock_proxy_cls.return_value = mock_proxy

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        records = rpc.search_read(
            "sale.order", [["state", "=", "draft"]], fields=["name"]
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["name"], "SO001")


class TestOdooRPCExecute(unittest.TestCase):
    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_execute_success(self, mock_proxy_cls):
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = 2
        mock_proxy.execute_kw.return_value = True
        mock_proxy_cls.return_value = mock_proxy

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        result = rpc.execute("sale.order", "action_confirm", [1, 2, 3])

        self.assertTrue(result)
        mock_proxy.execute_kw.assert_called_with(
            "test", 2, "admin", "sale.order", "action_confirm", [[1, 2, 3]]
        )

    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_execute_error(self, mock_proxy_cls):
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = 2
        mock_proxy.execute_kw.side_effect = Exception("Access denied")
        mock_proxy_cls.return_value = mock_proxy

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        result = rpc.execute("sale.order", "action_confirm", [1])

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)


class TestOdooRPCIsAlive(unittest.TestCase):
    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_is_alive_true(self, mock_proxy_cls):
        mock_common = MagicMock()
        mock_common.version.return_value = {"server_version": "18.0"}
        mock_proxy_cls.return_value = mock_common

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        self.assertTrue(rpc.is_alive())

    @patch("api.odoo_rpc.xmlrpc.client.ServerProxy")
    def test_is_alive_false(self, mock_proxy_cls):
        mock_common = MagicMock()
        mock_common.version.side_effect = ConnectionRefusedError
        mock_proxy_cls.return_value = mock_common

        rpc = OdooRPC("http://localhost:8069", "test", "admin", "admin")
        self.assertFalse(rpc.is_alive())


if __name__ == "__main__":
    unittest.main()
