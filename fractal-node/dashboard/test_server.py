import unittest
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
        with patch.object(server, "status_snapshot", return_value=snapshot):
            page = server.render().decode()
        self.assertIn("Synchronizing", page)
        self.assertIn("50.0000%", page)
        self.assertIn("/Fractal:0.3.0/", page)

    def test_render_handles_unavailable_rpc(self):
        with (
            patch.object(server, "status_snapshot", side_effect=RuntimeError("offline")),
            patch.object(server, "directory_size", return_value=0),
        ):
            page = server.render().decode()
        self.assertIn("Starting", page)
        self.assertIn("RPC is not available", page)


if __name__ == "__main__":
    unittest.main()
