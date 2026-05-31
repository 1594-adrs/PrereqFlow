import unittest

from prereqflow.graph import PrereqGraph
from prereqflow.models import Course
from prereqflow.editor import _add_course_to_graph


class TestEditorAddCourse(unittest.TestCase):
    def setUp(self):
        self.graph = PrereqGraph()
        self.graph.add_course(Course(code="CS101", name="Intro", credits=3))

    def test_add_valid_course(self):
        self.graph.add_course(Course(code="CS102", name="Next", credits=3))
        self.assertIn("CS102", self.graph.courses)
        self.assertEqual(self.graph.courses["CS102"].name, "Next")

    def test_add_duplicate_course(self):
        self.graph.add_course(Course(code="CS101", name="Duplicate", credits=3))
        self.assertEqual(self.graph.courses["CS101"].name, "Duplicate")

    def test_remove_course(self):
        self.graph.remove_course("CS101")
        self.assertNotIn("CS101", self.graph.courses)

    def test_add_prerequisite(self):
        self.graph.add_course(Course(code="CS102", name="Next", credits=3))
        self.graph.add_prerequisite("CS102", "CS101")
        self.assertEqual(self.graph.get_prerequisites("CS102"), {"CS101"})

    def test_add_prerequisite_creates_cycle(self):
        self.graph.add_course(Course(code="CS102", name="Next", credits=3))
        self.graph.add_prerequisite("CS102", "CS101")
        self.graph.add_prerequisite("CS101", "CS102")
        self.assertTrue(self.graph.detect_cycle())

    def test_remove_prerequisite(self):
        self.graph.add_course(Course(code="CS102", name="Next", credits=3))
        self.graph.add_prerequisite("CS102", "CS101")
        self.graph.remove_prerequisite("CS102", "CS101")
        self.assertEqual(self.graph.get_prerequisites("CS102"), set())

    def test_add_co_requisite(self):
        self.graph.add_course(Course(code="CS102", name="Lab", credits=1))
        self.graph.add_co_requisite("CS101", "CS102")
        self.assertIn("CS102", self.graph.get_co_requisites("CS101"))
        self.assertIn("CS101", self.graph.get_co_requisites("CS102"))

    def test_remove_co_requisite(self):
        self.graph.add_course(Course(code="CS102", name="Lab", credits=1))
        self.graph.add_co_requisite("CS101", "CS102")
        self.graph.remove_co_requisite("CS101", "CS102")
        self.assertEqual(self.graph.get_co_requisites("CS101"), set())
        self.assertEqual(self.graph.get_co_requisites("CS102"), set())
