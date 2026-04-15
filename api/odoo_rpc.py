# © 2026 TechnoLibre (http://www.technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import xmlrpc.client


class OdooRPC:
    """Lightweight Odoo XML-RPC client."""

    def __init__(self, url, database, username, password):
        self.url = url.rstrip("/")
        self.database = database
        self.username = username
        self.password = password
        self._uid = None

    def _common(self):
        return xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common", allow_none=True
        )

    def _object(self):
        return xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object", allow_none=True
        )

    def authenticate(self):
        """Authenticate and cache uid. Returns uid or None."""
        try:
            self._uid = self._common().authenticate(
                self.database, self.username, self.password, {}
            )
        except Exception:
            self._uid = None
        return self._uid

    @property
    def uid(self):
        if self._uid is None:
            self.authenticate()
        return self._uid

    def search_count(self, model, domain=None):
        """Count records matching domain."""
        if self.uid is None:
            return None
        try:
            return self._object().execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                "search_count",
                [domain or []],
            )
        except Exception:
            return None

    def search_read(self, model, domain=None, fields=None, limit=0):
        """Search and read records."""
        if self.uid is None:
            return None
        try:
            return self._object().execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                "search_read",
                [domain or []],
                {"fields": fields or [], "limit": limit},
            )
        except Exception:
            return None

    def execute(self, model, method, record_ids):
        """Execute a method on records."""
        if self.uid is None:
            return None
        try:
            return self._object().execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                method,
                [record_ids],
            )
        except Exception as e:
            return {"error": str(e)}

    def is_alive(self):
        """Check if server responds."""
        try:
            self._common().version()
            return True
        except Exception:
            return False
