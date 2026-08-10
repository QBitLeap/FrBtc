import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import server


class DashboardTests(unittest.TestCase):
    def test_formats_storage(self):
        self.assertEqual(server.format_bytes(300 * 1024**3), "300.0 GiB")

    def test_render_reports_syncing_node(self):
        snapshot = {
            "blocks": 100,
            "headers": 200,
            "progress": 0.5,
            "pruned": True,
            "peers": 8,
            "version": "/Fractal:0.3.0/",
            "disk": 1024**3,
        }
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(server, "STATUS_CACHE_FILE", Path(directory) / "status.json"),
                patch.object(server, "status_snapshot", return_value=snapshot),
            ):
                page = server.render().decode()
        self.assertIn("Synchronizing", page)
        self.assertIn("50.0000%", page)
        self.assertIn("/Fractal:0.3.0/", page)

    def test_render_preserves_last_sync_status_when_rpc_is_busy(self):
        snapshot = {
            "blocks": 742629,
            "headers": 2019000,
            "progress": 0.936409,
            "pruned": True,
            "peers": 10,
            "version": "/Satoshi:0.3.0/",
            "disk": 100 * 1024**3,
        }
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(server, "STATUS_CACHE_FILE", Path(directory) / "status.json"),
                patch.object(server, "status_snapshot", return_value=snapshot),
            ):
                server.render()
                with (
                    patch.object(server, "status_snapshot", side_effect=TimeoutError("busy")),
                    patch.object(server, "directory_size", return_value=snapshot["disk"]),
                ):
                    page = server.render().decode()

        self.assertIn("Synchronizing (RPC busy)", page)
        self.assertIn("93.6409%", page)
        self.assertIn("742,629", page)
        self.assertIn("last successful RPC", page)
        self.assertNotIn(">Starting<", page)

    def test_render_without_cache_reports_rpc_unavailable_not_starting(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(server, "STATUS_CACHE_FILE", Path(directory) / "missing.json"),
                patch.object(server, "status_snapshot", side_effect=RuntimeError("offline")),
                patch.object(server, "directory_size", return_value=0),
            ):
                page = server.render().decode()
        self.assertIn("RPC unavailable", page)
        self.assertNotIn(">Starting<", page)

    def test_dashboard_refreshes_every_five_minutes(self):
        snapshot = {
            "blocks": 100,
            "headers": 100,
            "progress": 1.0,
            "pruned": True,
            "peers": 8,
            "version": "/Satoshi:0.3.0/",
            "disk": 1024**3,
        }
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(server, "STATUS_CACHE_FILE", Path(directory) / "status.json"),
                patch.object(server, "status_snapshot", return_value=snapshot),
            ):
                page = server.render().decode()

        self.assertIn('http-equiv="refresh" content="300"', page)
        self.assertIn("refreshes every 5 minutes", page)


if __name__ == "__main__":
    unittest.main()
