import json
import unittest
from pathlib import Path

from prereqflow.graph import PrereqGraph
from prereqflow.io import save_graph_to_json, load_graph_from_json
from prereqflow.models import Course
from prereqflow.uploader import _process_json_upload


class TestUploaderJSON(unittest.TestCase):
    def test_process_json_upload_valid(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", credits=3))
        graph.add_course(Course(code="CS102", name="Next", credits=3))
        graph.add_prerequisite("CS102", "CS101")
        data = graph.to_dict()
        content = json.dumps(data).encode("utf-8")
        result = _process_json_upload(content, "test.json")
        self.assertIsNotNone(result)
        self.assertIn("CS101", result.courses)
        self.assertIn("CS102", result.courses)
        self.assertEqual(result.get_prerequisites("CS102"), {"CS101"})

    def test_process_json_upload_missing_courses_key(self):
        content = json.dumps({"name": "no courses"}).encode("utf-8")
        with self.assertRaises(ValueError):
            _process_json_upload(content, "bad.json")

    def test_process_json_upload_invalid_json(self):
        content = b"not json"
        with self.assertRaises(json.JSONDecodeError):
            _process_json_upload(content, "bad.json")

    def test_process_json_upload_empty(self):
        content = json.dumps({"courses": {}, "prerequisites": {}}).encode("utf-8")
        result = _process_json_upload(content, "empty.json")
        self.assertIsNotNone(result)
        self.assertEqual(len(result.courses), 0)

    def test_process_json_upload_with_prereqs(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="A", name="Alpha", credits=2))
        graph.add_course(Course(code="B", name="Beta", credits=2))
        graph.add_prerequisite("B", "A")
        data = graph.to_dict()
        content = json.dumps(data).encode("utf-8")
        result = _process_json_upload(content, "prereqs.json")
        self.assertEqual(result.get_prerequisites("B"), {"A"})


class TestUploaderCSV(unittest.TestCase):
    def test_csv_round_trip(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", credits=3))
        graph.add_course(Course(code="CS102", name="Next", credits=3))
        graph.add_prerequisite("CS102", "CS101")
        from prereqflow.io import save_graph_to_csv, load_graph_from_csv
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp_path = tmp.name
        try:
            save_graph_to_csv(graph, tmp_path)
            loaded = load_graph_from_csv(tmp_path)
            self.assertIn("CS101", loaded.courses)
            self.assertIn("CS102", loaded.courses)
            self.assertEqual(loaded.get_prerequisites("CS102"), {"CS101"})
        finally:
            import os
            os.unlink(tmp_path)
