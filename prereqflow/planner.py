from typing import Dict, Iterable, List, Optional, Set

from .graph import PrereqGraph
from .models import Course


class SemesterPlanner:
    def __init__(
        self,
        graph: PrereqGraph,
        max_credits: int = 18,
        max_semesters: int = 12,
        plan_type: str = "balanced",
    ) -> None:
        self.graph = graph
        self.max_credits = max_credits
        self.max_semesters = max_semesters
        self.plan_type = plan_type

    def _course_priority(self, course: Course) -> tuple:
        depth = self.graph.course_dependency_depth(course.code)
        dependents = len(self.graph.get_dependents(course.code))
        if self.plan_type == "fast":
            return (-depth, course.credits, course.difficulty, course.code)
        if self.plan_type == "low_risk":
            return (course.difficulty, -dependents, course.credits, course.code)
        return (course.semester or 999, course.difficulty, -depth, course.code)

    def _completed_credits(self, completed: Set[str]) -> int:
        return sum(
            self.graph.courses[code].credits
            for code in completed
            if code in self.graph.courses
        )

    def _co_requisite_closure(self, course_code: str, completed: Set[str]) -> Set[str]:
        closure: Set[str] = set()

        def visit(code: str) -> None:
            for co_req in self.graph.get_co_requisites(code):
                co_req = co_req.strip().upper()
                if co_req not in completed and co_req not in closure:
                    closure.add(co_req)
                    visit(co_req)

        visit(course_code)
        return closure

    def _is_co_requisite_eligible(
        self,
        course: Course,
        completed: Set[str],
        semester: int,
        completed_credits: int,
        additional_completed: Optional[Set[str]] = None,
    ) -> bool:
        prereqs = self.graph.get_prerequisites(course.code)
        effective_completed = set(completed)
        if additional_completed is not None:
            effective_completed |= additional_completed
        if not prereqs.issubset(effective_completed):
            return False
        if not course.is_offered_in_semester(semester):
            return False
        if course.min_completed_credits is not None and completed_credits < course.min_completed_credits:
            return False
        return True

    def _is_available(
        self,
        course: Course,
        completed: Set[str],
        semester: int,
        completed_credits: int,
    ) -> bool:
        prereqs = self.graph.get_prerequisites(course.code)
        if not prereqs.issubset(completed):
            return False
        if not course.is_offered_in_semester(semester):
            return False
        if course.min_completed_credits is not None and completed_credits < course.min_completed_credits:
            return False

        closure = self._co_requisite_closure(course.code, completed)
        candidate_codes = {course.code} | closure
        candidate_pool = completed | candidate_codes

        for candidate_code in candidate_codes:
            candidate_course = self.graph.courses.get(candidate_code)
            if candidate_course is None:
                return False
            if not candidate_course.is_offered_in_semester(semester):
                return False
            if candidate_course.min_completed_credits is not None and completed_credits < candidate_course.min_completed_credits:
                return False
            candidate_prereqs = self.graph.get_prerequisites(candidate_code)
            if not candidate_prereqs.issubset(candidate_pool):
                return False

        return True

    def _available_courses(self, completed: Set[str], semester: int, completed_credits: int) -> List[Course]:
        return sorted(
            [
                course
                for code, course in self.graph.courses.items()
                if code not in completed and self._is_available(course, completed, semester, completed_credits)
            ],
            key=self._course_priority,
        )

    def plan(self, completed: Optional[Iterable[str]] = None) -> List[List[Course]]:
        if self.graph.detect_cycle():
            raise ValueError("Cannot generate a plan for a graph with prerequisite cycles")

        completed_set: Set[str] = {code.strip().upper() for code in (completed or set())}
        remaining: Dict[str, Course] = {
            code: course
            for code, course in self.graph.courses.items()
            if code not in completed_set
        }
        plan: List[List[Course]] = []
        current_semester = 1
        completed_credits = self._completed_credits(completed_set)

        while remaining and current_semester <= self.max_semesters:
            available = self._available_courses(completed_set, current_semester, completed_credits)
            if not available:
                break
            semester_courses: List[Course] = []
            semester_credits = 0
            selected_codes: Set[str] = set()
            for course in available:
                if course.code in selected_codes:
                    continue
                closure_courses = self._co_requisite_closure(course.code, completed_set)
                candidate_codes = {course.code} | closure_courses
                candidate_courses = [self.graph.courses[code] for code in sorted(candidate_codes)]
                candidate_credits = sum(item.credits for item in candidate_courses)
                if semester_credits + candidate_credits > self.max_credits:
                    continue
                if any(code in completed_set for code in candidate_codes):
                    candidate_courses = [item for item in candidate_courses if item.code not in completed_set]
                for item in candidate_courses:
                    if item.code not in selected_codes:
                        semester_courses.append(item)
                        semester_credits += item.credits
                        selected_codes.add(item.code)
                if semester_credits >= self.max_credits:
                    break
            if not semester_courses:
                raise ValueError("A single course exceeds the maximum credit limit")
            plan.append(semester_courses)
            for course in semester_courses:
                completed_set.add(course.code)
                completed_credits += course.credits
                remaining.pop(course.code, None)
            current_semester += 1

        if remaining:
            raise ValueError("No feasible study plan could be completed within the semester limit")

        return plan


def generate_study_plan(
    graph: PrereqGraph,
    max_credits: int = 18,
    max_semesters: int = 12,
    plan_type: str = "balanced",
    completed: Optional[Iterable[str]] = None,
) -> List[List[Course]]:
    planner = SemesterPlanner(graph, max_credits=max_credits, max_semesters=max_semesters, plan_type=plan_type)
    return planner.plan(completed=completed)
