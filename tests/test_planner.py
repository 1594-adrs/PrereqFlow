import unittest

from prereqflow.graph import PrereqGraph
from prereqflow.models import Course
from prereqflow.planner import generate_study_plan


class TestSemesterPlanner(unittest.TestCase):
    def test_generate_study_plan_order(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro"))
        graph.add_course(Course(code="CS102", name="Next", credits=3))
        graph.add_prerequisite("CS102", "CS101")
        plan = generate_study_plan(graph, max_credits=6)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0][0].code, "CS101")
        self.assertEqual(plan[1][0].code, "CS102")

    def test_generate_study_plan_with_completed_courses(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro"))
        graph.add_course(Course(code="CS102", name="Next", credits=3))
        graph.add_prerequisite("CS102", "CS101")
        plan = generate_study_plan(graph, max_credits=6, completed=["CS101"])
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0][0].code, "CS102")

    def test_generate_study_plan_with_semester_offered(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", semester_offered=[1]))
        graph.add_course(Course(code="CS102", name="Next", credits=3, semester_offered=[2]))
        graph.add_prerequisite("CS102", "CS101")
        plan = generate_study_plan(graph, max_credits=6, max_semesters=3)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0][0].code, "CS101")
        self.assertEqual(plan[1][0].code, "CS102")

    def test_generate_study_plan_with_repeating_semester_offerings(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", credits=3, semester_offered=[1]))
        graph.add_course(Course(code="CS102", name="Next", credits=3, semester_offered=[2]))
        graph.add_course(Course(code="CS103", name="Final", credits=3, semester_offered=[1]))
        graph.add_prerequisite("CS102", "CS101")
        graph.add_prerequisite("CS103", "CS102")
        plan = generate_study_plan(graph, max_credits=9, max_semesters=4)
        self.assertEqual(len(plan), 3)
        self.assertEqual([course.code for course in plan[0]], ["CS101"])
        self.assertEqual([course.code for course in plan[1]], ["CS102"])
        self.assertEqual([course.code for course in plan[2]], ["CS103"])

    def test_generate_study_plan_with_min_completed_credits(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", credits=3))
        graph.add_course(Course(code="CS103", name="Capstone", credits=3, min_completed_credits=3))
        plan = generate_study_plan(graph, max_credits=6)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0][0].code, "CS101")
        self.assertEqual(plan[1][0].code, "CS103")

    def test_generate_study_plan_with_co_requisites(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", credits=3))
        graph.add_course(Course(code="CS102", name="Lab", credits=1, co_requisites={"CS101"}))
        plan = generate_study_plan(graph, max_credits=6)
        self.assertEqual(len(plan), 1)
        self.assertEqual({course.code for course in plan[0]}, {"CS101", "CS102"})

    def test_generate_study_plan_with_mutual_co_reqs(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="CS101", name="Intro", credits=3))
        graph.add_course(Course(code="CS102", name="Intermediate", credits=3, co_requisites={"CS103"}))
        graph.add_course(Course(code="CS103", name="Advanced Lab", credits=3, co_requisites={"CS102"}))
        graph.add_prerequisite("CS102", "CS101")
        plan = generate_study_plan(graph, max_credits=9)
        self.assertEqual(len(plan), 2)
        self.assertEqual([course.code for course in plan[0]], ["CS101"])
        self.assertEqual(set(course.code for course in plan[1]), {"CS102", "CS103"})
