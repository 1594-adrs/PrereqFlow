from typing import Dict, List, Optional, Set

from .models import Course


class PrereqGraph:
    def __init__(self) -> None:
        self.courses: Dict[str, Course] = {}
        self.prerequisites: Dict[str, Set[str]] = {}
        self.dependents: Dict[str, Set[str]] = {}
        self.co_requisites: Dict[str, Set[str]] = {}

    def add_course(self, course: Course) -> None:
        if not course.code:
            raise ValueError("Course code is required")
        code = course.code.strip().upper()
        course.code = code
        self.courses[code] = course
        self.prerequisites.setdefault(code, set())
        self.dependents.setdefault(code, set())
        self.co_requisites.setdefault(code, set())
        for co_req in course.co_requisites:
            self.co_requisites.setdefault(co_req.strip().upper(), set()).add(code)

    def add_prerequisite(self, course_code: str, prereq_code: str) -> None:
        course_code = course_code.strip().upper()
        prereq_code = prereq_code.strip().upper()
        if course_code == prereq_code:
            raise ValueError("A course cannot be its own prerequisite")
        if course_code not in self.courses or prereq_code not in self.courses:
            raise KeyError("Both course and prerequisite must exist in the graph")
        self.prerequisites.setdefault(course_code, set()).add(prereq_code)
        self.dependents.setdefault(prereq_code, set()).add(course_code)

    def add_co_requisite(self, course_code: str, co_req_code: str) -> None:
        course_code = course_code.strip().upper()
        co_req_code = co_req_code.strip().upper()
        if course_code == co_req_code:
            raise ValueError("A course cannot be its own co-requisite")
        if course_code not in self.courses or co_req_code not in self.courses:
            raise KeyError("Both course and co-requisite must exist in the graph")
        self.co_requisites.setdefault(course_code, set()).add(co_req_code)
        self.co_requisites.setdefault(co_req_code, set()).add(course_code)

    def remove_course(self, course_code: str) -> None:
        course_code = course_code.strip().upper()
        if course_code not in self.courses:
            return
        for prereq in self.prerequisites.get(course_code, set()):
            self.dependents.get(prereq, set()).discard(course_code)
        for dependent in self.dependents.get(course_code, set()):
            self.prerequisites.get(dependent, set()).discard(course_code)
        for co_req in self.co_requisites.get(course_code, set()):
            self.co_requisites.get(co_req, set()).discard(course_code)
        self.prerequisites.pop(course_code, None)
        self.dependents.pop(course_code, None)
        self.co_requisites.pop(course_code, None)
        self.courses.pop(course_code, None)

    def remove_prerequisite(self, course_code: str, prereq_code: str) -> None:
        course_code = course_code.strip().upper()
        prereq_code = prereq_code.strip().upper()
        self.prerequisites.get(course_code, set()).discard(prereq_code)
        self.dependents.get(prereq_code, set()).discard(course_code)

    def remove_co_requisite(self, course_code: str, co_req_code: str) -> None:
        course_code = course_code.strip().upper()
        co_req_code = co_req_code.strip().upper()
        self.co_requisites.get(course_code, set()).discard(co_req_code)
        self.co_requisites.get(co_req_code, set()).discard(course_code)

    def get_prerequisites(self, course_code: str) -> Set[str]:
        return set(self.prerequisites.get(course_code.strip().upper(), set()))

    def get_dependents(self, course_code: str) -> Set[str]:
        return set(self.dependents.get(course_code.strip().upper(), set()))

    def get_co_requisites(self, course_code: str) -> Set[str]:
        return set(self.co_requisites.get(course_code.strip().upper(), set()))

    def get_prerequisite_closure(self, course_code: str) -> Set[str]:
        closure: Set[str] = set()

        def visit(node: str) -> None:
            for prereq in self.get_prerequisites(node):
                if prereq not in closure:
                    closure.add(prereq)
                    visit(prereq)

        visit(course_code.strip().upper())
        return closure

    def course_dependency_depth(self, course_code: str) -> int:
        course_code = course_code.strip().upper()
        if not self.get_prerequisites(course_code):
            return 0
        return 1 + max(self.course_dependency_depth(prereq) for prereq in self.get_prerequisites(course_code))

    def completed_credits(self, completed: Set[str]) -> int:
        return sum(
            self.courses[code].credits
            for code in completed
            if code in self.courses
        )

    def critical_courses(self) -> List[Course]:
        return sorted(
            self.courses.values(),
            key=lambda course: (
                self.course_dependency_depth(course.code),
                len(self.get_dependents(course.code)),
                course.difficulty,
            ),
            reverse=True,
        )

    def detect_cycle(self) -> bool:
        visited: Set[str] = set()
        stack: Set[str] = set()

        def visit(node: str) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for prereq in self.prerequisites.get(node, set()):
                if visit(prereq):
                    return True
            stack.remove(node)
            return False

        return any(visit(node) for node in self.courses)

    def topological_sort(self) -> List[Course]:
        if self.detect_cycle():
            raise ValueError("The course graph contains a cycle and cannot be sorted")
        visited: Set[str] = set()
        ordered: List[Course] = []

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for prereq in sorted(self.prerequisites.get(node, set())):
                visit(prereq)
            ordered.append(self.courses[node])

        for node in sorted(self.courses):
            visit(node)

        return ordered

    def eligible_courses(
        self,
        completed: Optional[Set[str]] = None,
        semester: Optional[int] = None,
        completed_credits: Optional[int] = None,
    ) -> List[Course]:
        completed = {code.strip().upper() for code in (completed or set())}
        if completed_credits is None:
            completed_credits = self.completed_credits(completed)
        eligible: List[Course] = []
        for code, course in self.courses.items():
            if code in completed:
                continue
            prereqs = self.get_prerequisites(code)
            if not prereqs.issubset(completed):
                continue
            if course.min_completed_credits is not None and completed_credits < course.min_completed_credits:
                continue
            if semester is not None and not course.is_offered_in_semester(semester):
                continue
            missing_co_reqs = [
                co_req
                for co_req in self.get_co_requisites(code)
                if co_req not in completed
            ]
            can_take = True
            for co_req_code in missing_co_reqs:
                co_req_course = self.courses.get(co_req_code)
                if co_req_course is None:
                    can_take = False
                    break
                co_prereqs = self.get_prerequisites(co_req_code)
                if not co_prereqs.issubset(completed):
                    can_take = False
                    break
                if semester is not None and not co_req_course.is_offered_in_semester(semester):
                    can_take = False
                    break
                if co_req_course.min_completed_credits is not None and completed_credits < co_req_course.min_completed_credits:
                    can_take = False
                    break
            if not can_take:
                continue
            eligible.append(course)
        return sorted(eligible, key=lambda c: c.code)

    def to_dict(self) -> Dict[str, object]:
        return {
            "courses": [course.to_dict() for course in self.courses.values()],
            "prerequisites": [
                {"course": course, "prereq": prereq}
                for course, prereqs in self.prerequisites.items()
                for prereq in prereqs
            ],
            "co_requisites": [
                {"course": course, "co_req": co_req}
                for course, co_reqs in self.co_requisites.items()
                for co_req in co_reqs
            ],
        }

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "PrereqGraph":
        graph = PrereqGraph()
        for entry in data.get("courses", []):
            course = Course.from_dict(entry)
            graph.add_course(course)
        for edge in data.get("prerequisites", []):
            graph.add_prerequisite(str(edge["course"]), str(edge["prereq"]))
        for edge in data.get("co_requisites", []):
            graph.add_co_requisite(str(edge["course"]), str(edge["co_req"]))
        return graph
