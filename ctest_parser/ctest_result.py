from dataclasses import dataclass
from typing import List

@dataclass
class TestRun:
    name: str
    passed: bool
    time: float


class TestResult:

    def __init__(self, first_run: TestRun):
        self.name: str = first_run.name
        self.passed: bool = first_run.passed
        self.flake: bool = False
        self.avg_time: float = first_run.time
        self.runs: List[TestRun] = [first_run]

    def add_run(self, run: TestRun) -> None:
        if run.name != self.name:
            return
        self.flake = self.passed != run.passed
        self.passed |= run.passed
        self.runs.append(run)
        self.avg_time = (self.avg_time + run.time) / len(self.runs)

    def get_result_text(self) -> str:
        result_text = "Passed" if self.passed else "Failed"
        if self.flake:
            result_text = "Flake"
        return result_text

