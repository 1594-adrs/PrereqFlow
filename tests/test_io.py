import csv
import tempfile
import unittest
from pathlib import Path

from prereqflow.graph import PrereqGraph
from prereqflow.io import load_graph_from_csv, load_graph_from_json, save_graph_to_csv, save_graph_to_json
from prereqflow.models import Course


class TestIO(unittest.TestCase):
    def test_save_and_load_graph_to_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            graph = PrereqGraph()
            graph.add_course(Course(code="CS101", name="Intro", credits=3))
            graph.add_course(Course(code="CS102", name="Next", credits=3, area="Matemáticas"))
            graph.add_prerequisite("CS102", "CS101")

            json_path = tmp_path / "graph.json"
            save_graph_to_json(graph, str(json_path))
            loaded = load_graph_from_json(str(json_path))

            self.assertIn("CS101", loaded.courses)
            self.assertIn("CS102", loaded.courses)
            self.assertEqual(loaded.get_prerequisites("CS102"), {"CS101"})
            self.assertEqual(loaded.courses["CS102"].area, "Matemáticas")

    def test_load_graph_from_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            csv_path = tmp_path / "graph.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "code",
                    "name",
                    "credits",
                    "semester",
                    "area",
                    "semester_offered",
                    "min_completed_credits",
                    "co_requisites",
                    "required",
                    "prerequisites",
                ])
                writer.writerow(["CS101", "Intro", 3, 1, "Matemáticas", "", "", "", 1, ""])
                writer.writerow(["CS102", "Next", 3, 2, "Computación", "", "", "CS101", 1, "CS101"])

            loaded = load_graph_from_csv(str(csv_path))
            self.assertIn("CS101", loaded.courses)
            self.assertIn("CS102", loaded.courses)
            self.assertEqual(loaded.courses["CS102"].semester, 2)
            self.assertEqual(loaded.courses["CS102"].area, "Computación")
            self.assertEqual(loaded.courses["CS102"].co_requisites, {"CS101"})
            self.assertEqual(loaded.get_prerequisites("CS102"), {"CS101"})

    def test_load_utp_curriculum_json(self):
        path = Path(__file__).resolve().parent.parent / "data" / "utp_sistemas.json"
        graph = load_graph_from_json(str(path))
        self.assertGreater(len(graph.courses), 50)
        self.assertIn("SIS001", graph.courses)
        self.assertEqual(graph.courses["SIS001"].semester, 1)
        self.assertEqual(graph.courses["SIS064"].semester, 10)
