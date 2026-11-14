import unittest
from unittest.mock import patch, mock_open
from fastapi.testclient import TestClient

from src.api import app
from src.api import save_error_history

client = TestClient(app)


class TestAPI(unittest.TestCase):

    @patch("src.api.generate_transactions")
    def test_metrics_endpoint_returns_expected_fields(
        self, mock_generate
    ):
        mock_generate.return_value = [
            {
                "order_id": 1,
                "product": "Laptop",
                "sales_amount": 1200.00,
                "tax_amount": 120.00,
                "timestamp": "2026-10-16T10:00:00+00:00",
            }
        ]

        response = client.get("/api/metrics")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("total_transactions", data)
        self.assertIn("valid_transactions", data)
        self.assertIn("quality_errors", data)
        self.assertIn("pipeline_status", data)
        self.assertIn("error_rate_percent", data)
        self.assertIn("circuit_breaker_triggered", data)

    @patch("src.api.generate_transactions")
    @patch("src.api.get_quarantine_count")
    def test_metrics_returns_saved_quarantine_count(
        self, mock_quarantine_count, mock_generate
    ):
        mock_generate.return_value = [
            {
                "order_id": 1,
                "product": "Laptop",
                "sales_amount": 1200.00,
                "tax_amount": 120.00,
                "timestamp": "2026-10-16T10:00:00+00:00",
            }
        ]
        mock_quarantine_count.return_value = 212

        response = client.get("/api/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["quarantined_records"], 212
        )

    @patch("src.api.QUARANTINE_FILE")
    def test_quarantine_endpoint_returns_records(self, mock_file):
        mock_file.exists.return_value = False

        response = client.get("/api/quarantine")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"total_records": 0, "records": []},
        )

    @patch("src.api.QUARANTINE_FILE")
    def test_quarantine_endpoint_reads_existing_records(self, mock_file):
        mock_file.exists.return_value = True

        saved_records = [
            {
                "order_id": 101,
                "product": "Laptop",
                "sales_amount": 1200.00,
                "tax_amount": None,
                "timestamp": "2026-10-16T10:00:00+00:00",
            }
        ]

        mock_file.open.return_value.__enter__.return_value.read.return_value = (
            __import__("json").dumps(saved_records)
        )

        with patch(
            "builtins.open",
            unittest.mock.mock_open(
                read_data=__import__("json").dumps(saved_records)
            ),
        ):
            response = client.get("/api/quarantine")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_records"], 1)
        self.assertEqual(data["records"], saved_records)

    @patch("src.api.QUARANTINE_FILE")
    def test_quarantine_endpoint_handles_non_list_json(self, mock_file):
        mock_file.exists.return_value = True
        mock_file.open.return_value.__enter__.return_value.read.return_value = (
            "{}"
        )

        response = client.get("/api/quarantine")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"total_records": 0, "records": []},
        )

    @patch("src.api.QUARANTINE_FILE")
    def test_quarantine_endpoint_handles_read_error(self, mock_file):
        mock_file.exists.return_value = True
        mock_file.open.side_effect = OSError("File cannot be read")

        response = client.get("/api/quarantine")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["total_records"],
            0,
        )
        self.assertEqual(
            response.json()["records"],
            [],
        )
        self.assertEqual(
            response.json()["error"],
            "Unable to read quarantine records.",
        )

    @patch("src.api.ERROR_HISTORY_FILE")
    def test_error_history_endpoint_returns_empty_history(self, mock_file):
        mock_file.exists.return_value = False

        response = client.get("/api/error-history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"total_records": 0, "history": []},
        )

    @patch("src.api.ERROR_HISTORY_FILE")
    def test_error_history_endpoint_returns_saved_records(self, mock_file):
        import json
        from unittest.mock import mock_open

        saved_history = [
            {
                "timestamp": "2026-11-08T06:40:00+05:30",
                "error_rate_percent": 7.0,
            }
        ]

        mock_file.exists.return_value = True
        mock_file.open.return_value = mock_open(
            read_data=json.dumps(saved_history)
        ).return_value

        response = client.get("/api/error-history")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_records"], 1)
        self.assertEqual(data["history"], saved_history)

    @patch("src.api.ERROR_HISTORY_FILE")
    @patch("src.api.TEMP_ERROR_HISTORY_FILE")
    def test_save_error_history_appends_record(
        self, mock_temp_file, mock_history_file
    ):
        import json
        from unittest.mock import mock_open

        existing_history = [
            {
                "timestamp": "2026-11-08T06:40:00+05:30",
                "error_rate_percent": 7.0,
            }
        ]

        mock_history_file.exists.return_value = True
        mock_history_file.open.return_value = mock_open(
            read_data=json.dumps(existing_history)
        ).return_value

        mock_temp_file.open.return_value = mock_open().return_value

        with patch("src.api.os.fsync"), patch("src.api.os.replace") as mock_replace:
            save_error_history(8.0)

        mock_replace.assert_called_once_with(
            mock_temp_file, mock_history_file
        )
        mock_temp_file.open.assert_called_once_with(
            "w", encoding="utf-8"
        )
        mock_history_file.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )

   
  
    def test_save_error_history_preserves_existing_records(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        existing_history = [
            {
                "timestamp": "2026-11-08T06:40:00+05:30",
                "error_rate_percent": 7.0,
            }
        ]

        with TemporaryDirectory() as directory:
            history_file = Path(directory) / "error_history.json"
            temp_file = history_file.with_suffix(".tmp")

            history_file.write_text(
                json.dumps(existing_history),
                encoding="utf-8",
            )

            with (
                patch("src.api.ERROR_HISTORY_FILE", history_file),
                patch("src.api.TEMP_ERROR_HISTORY_FILE", temp_file),
            ):
                save_error_history(8.0)

            saved_history = json.loads(
                history_file.read_text(encoding="utf-8")
            )

            self.assertEqual(len(saved_history), 2)
            self.assertEqual(saved_history[0], existing_history[0])
            self.assertEqual(
                saved_history[1]["error_rate_percent"], 8.0
            )
            self.assertIn("timestamp", saved_history[1])
            self.assertFalse(temp_file.exists())

    def test_save_error_history_handles_invalid_json(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as directory:
            history_file = Path(directory) / "error_history.json"
            temp_file = history_file.with_suffix(".tmp")

            history_file.write_text(
                "{invalid json",
                encoding="utf-8",
            )

            with (
                patch("src.api.ERROR_HISTORY_FILE", history_file),
                patch("src.api.TEMP_ERROR_HISTORY_FILE", temp_file),
            ):
                save_error_history(8.0)

            self.assertEqual(
                history_file.read_text(encoding="utf-8"),
                "{invalid json",
            )
            self.assertFalse(temp_file.exists())

    def test_save_error_history_handles_non_list_json(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        with TemporaryDirectory() as directory:
            history_file = Path(directory) / "error_history.json"
            temp_file = history_file.with_suffix(".tmp")

            original_content = {"unexpected": "object"}
            history_file.write_text(
                json.dumps(original_content),
                encoding="utf-8",
            )

            with (
                patch("src.api.ERROR_HISTORY_FILE", history_file),
                patch("src.api.TEMP_ERROR_HISTORY_FILE", temp_file),
            ):
                save_error_history(8.0)

            saved_content = json.loads(
                history_file.read_text(encoding="utf-8")
            )

            self.assertEqual(saved_content, original_content)
            self.assertFalse(temp_file.exists())

    @patch("src.api.TEMP_ERROR_HISTORY_FILE")
    @patch("src.api.ERROR_HISTORY_FILE")
    def test_save_error_history_handles_write_failure(
        self, mock_history_file, mock_temp_file
    ):
        mock_history_file.exists.return_value = False
        mock_temp_file.open.side_effect = OSError(
            "Unable to write temporary file"
        )

        save_error_history(8.0)

        mock_temp_file.open.assert_called_once_with(
            "w", encoding="utf-8"
        )

    @patch("src.api.os.replace")
    def test_save_error_history_handles_replace_failure(self, mock_replace):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            history_file = Path(directory) / "error_history.json"
            temp_file = history_file.with_suffix(".tmp")

            with (
                patch("src.api.ERROR_HISTORY_FILE", history_file),
                patch("src.api.TEMP_ERROR_HISTORY_FILE", temp_file),
            ):
                mock_replace.side_effect = OSError(
                    "Unable to replace history file"
                )

                save_error_history(8.0)

                mock_replace.assert_called_once_with(
                    temp_file, history_file
                )
                self.assertFalse(temp_file.exists())

    @patch("src.api.ERROR_HISTORY_FILE")
    def test_save_error_history_handles_directory_creation_failure(
        self, mock_history_file
    ):
        mock_history_file.parent.mkdir.side_effect = OSError(
            "Unable to create directory"
        )

        save_error_history(8.0)

        mock_history_file.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
   
if __name__ == "__main__":
    unittest.main()