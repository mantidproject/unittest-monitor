from dataclasses import dataclass
from typing import Dict


@dataclass
class RunResult:
    job_name: str
    run_number: str
    finish_time: str
    os: str
    test_results: Dict[str, "TestResult"]
