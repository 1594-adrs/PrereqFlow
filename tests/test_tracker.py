import unittest

from prereqflow.graph import PrereqGraph
from prereqflow.models import Course
from prereqflow.tracker import (
    ElectiveGroup,
    ElectiveManager,
    ProgressTracker,
    StudentRecord,
)


class TestStudentRecord(unittest.TestCase):
    def test_default_record(self):
        record = StudentRecord()
        self.assertEqual(record.completed_courses, set())
        self.assertEqual(record.current_semester, 0)
        self.assertEqual(record.total_credits, 0)

    def test_record_with_data(self):
        record = StudentRecord(
            completed_courses={"CS101", "CS102"},
            current_semester=2,
            total_credits=9,
        )
        self.assertEqual(len(record.completed_courses), 2)
        self.assertEqual(record.current_semester, 2)


class TestElectiveGroup(unittest.TestCase):
    def test_elective_group_defaults(self):
        group = ElectiveGroup(name="Test Group")
        self.assertEqual(group.course_codes, set())
        self.assertIsNone(group.min_select)

    def test_elective_group_with_rules(self):
        group = ElectiveGroup(
            name="Test Group",
            min_select=1,
            max_select=3,
            min_credits=6,
        )
        self.assertEqual(group.min_select, 1)
        self.assertEqual(group.max_select, 3)
        self.assertEqual(group.min_credits, 6)


class TestElectiveManager(unittest.TestCase):
    def setUp(self):
        self.manager = ElectiveManager()
        self.group = ElectiveGroup(
            name="Tecnologías",
            course_codes={"SIS053"},
            course_credits={"SIS053": 4},
            min_select=1,
            max_select=2,
            min_credits=3,
        )
        self.manager.add_group(self.group)

    def test_add_group(self):
        self.assertIn("Tecnologías", self.manager.elective_groups)

    def test_add_course_to_group(self):
        self.manager.add_course_to_group("Tecnologías", "SIS999")
        self.assertIn("SIS999", self.manager.elective_groups["Tecnologías"].course_codes)

    def test_validate_selection_valid(self):
        errors = self.manager.validate_selection("Tecnologías", {"SIS053"})
        self.assertEqual(errors, [])

    def test_validate_selection_nonexistent_group(self):
        errors = self.manager.validate_selection("Ghost", {"X"})
        self.assertGreater(len(errors), 0)

    def test_validate_selection_invalid_course(self):
        errors = self.manager.validate_selection("Tecnologías", {"SIS999"})
        self.assertGreater(len(errors), 0)

    def test_validate_selection_min_select_not_met(self):
        group = ElectiveGroup(name="Strict", min_select=2)
        group.course_codes = {"A", "B"}
        group.course_credits = {"A": 3, "B": 3}
        manager = ElectiveManager()
        manager.add_group(group)
        errors = manager.validate_selection("Strict", {"A"})
        self.assertGreater(len(errors), 0)

    def test_get_available_electives(self):
        graph = PrereqGraph()
        graph.add_course(Course(code="SIS053", name="Nuevas Tecnologías", credits=4))
        completed = set()
        available = self.manager.get_available_electives(graph, completed)
        self.assertIn("Tecnologías", available)

    def test_get_available_electives_no_graph_course(self):
        graph = PrereqGraph()
        completed = set()
        available = self.manager.get_available_electives(graph, completed)
        self.assertEqual(available, {})


class TestProgressTracker(unittest.TestCase):
    def setUp(self):
        self.graph = PrereqGraph()
        self.graph.add_course(Course(code="CS101", name="Intro", credits=3))
        self.graph.add_course(Course(code="CS102", name="Next", credits=3))
        self.graph.add_prerequisite("CS102", "CS101")
        self.tracker = ProgressTracker(self.graph)

    def test_initial_state(self):
        self.assertEqual(self.tracker.record.current_semester, 0)
        self.assertEqual(self.tracker.get_completed_courses(), set())

    def test_complete_semester(self):
        self.tracker.complete_semester(["CS101"], semester_number=1)
        self.assertIn("CS101", self.tracker.get_completed_courses())
        self.assertEqual(self.tracker.get_completed_credits(), 3)
        self.assertEqual(self.tracker.record.current_semester, 1)

    def test_complete_semester_with_prereqs(self):
        self.tracker.complete_semester(["CS101"], semester_number=1)
        self.tracker.complete_semester(["CS102"], semester_number=2)
        self.assertIn("CS102", self.tracker.get_completed_courses())
        self.assertEqual(self.tracker.get_completed_credits(), 6)

    def test_complete_semester_missing_prereq(self):
        with self.assertRaises(ValueError):
            self.tracker.complete_semester(["CS102"], semester_number=1)

    def test_complete_semester_nonexistent_course(self):
        with self.assertRaises(ValueError):
            self.tracker.complete_semester(["CS999"], semester_number=1)

    def test_complete_semester_auto_semester_number(self):
        self.tracker.complete_semester(["CS101"])
        self.assertEqual(self.tracker.record.current_semester, 1)

    def test_get_progress_summary(self):
        summary = self.tracker.get_progress_summary()
        self.assertIn("semestre_actual", summary)
        self.assertIn("porcentaje_avance", summary)
        self.assertEqual(summary["semestre_actual"], 0)

    def test_simulate_semester(self):
        result = self.tracker.simulate_semester(["CS101"], semester=1)
        self.assertEqual(result["nuevos_aprobados"], ["CS101"])
        self.assertIn("CS102", result["cursos_elegibles"])

    def test_get_eligible_courses(self):
        self.tracker.complete_semester(["CS101"])
        eligible = self.tracker.get_eligible_courses(semester=2)
        codes = [c.code for c in eligible]
        self.assertIn("CS102", codes)

    def test_get_elective_requirements_status_empty(self):
        manager = ElectiveManager()
        status = self.tracker.get_elective_requirements_status(manager)
        self.assertEqual(status, {})

    def test_select_elective(self):
        manager = ElectiveManager()
        group = ElectiveGroup(
            name="Test",
            course_codes={"CS101"},
            course_credits={"CS101": 3},
            min_select=1,
        )
        manager.add_group(group)
        errors = self.tracker.select_elective("Test", "CS101", manager)
        self.assertEqual(errors, [])
        self.assertIn("Test", self.tracker.record.elective_selections)
