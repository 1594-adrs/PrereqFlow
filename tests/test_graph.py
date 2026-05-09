import unittest

from prereqflow.graph import PrereqGraph
from prereqflow.models import Course


class TestPrereqGraph(unittest.TestCase):
    def test_graph_cycle_detection(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="A", name="Course A"))
        graph.add_course(Course(code="B", name="Course B"))
        graph.add_prerequisite("B", "A")
        graph.add_prerequisite("A", "B")
        self.assertTrue(graph.detect_cycle())

    def test_topological_sort_simple(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="A", name="Course A"))
        graph.add_course(Course(code="B", name="Course B"))
        graph.add_prerequisite("B", "A")
        sorted_courses = graph.topological_sort()
        self.assertEqual([course.code for course in sorted_courses], ["A", "B"])

    def test_prerequisite_closure_and_depth(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="A", name="Course A"))
        graph.add_course(Course(code="B", name="Course B"))
        graph.add_course(Course(code="C", name="Course C"))
        graph.add_prerequisite("B", "A")
        graph.add_prerequisite("C", "B")
        closure = graph.get_prerequisite_closure("C")
        self.assertEqual(closure, {"A", "B"})
        self.assertEqual(graph.course_dependency_depth("C"), 2)
