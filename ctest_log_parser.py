import logging
import re
from typing import Dict

from ctest_result import TestRun, TestResult

logger = logging.getLogger("CtestOutputParser")


class CtestOutputParser:

    def __init__(self, path_to_log_file: str):
        self.log_path: str = path_to_log_file
        self.test_results: Dict[str, TestResult] = {}
        self.result_regex = re.compile(r".*Test *\#\d+: ([a-zA-Z0-9_\.]+) [\.\*]+( {3}Passed|Failed) +(\d+\.\d+) sec")

    def parse(self) -> Dict[str, TestResult]:
        logger.info(f"Parsing {self.log_path}")
        with open(self.log_path, "r") as log_reader:
            results_line_matches = [self.result_regex.match(line) for line in log_reader.readlines() if self.result_regex.match(line)]

        for match in results_line_matches:
            name, result, time_taken = match.groups()
            run = TestRun(name, (result.strip() == "Passed"), float(time_taken))
            if name in self.test_results:
                self.test_results[name].add_run(run)
            else:
                # first run
                self.test_results[name] = TestResult(run)

        logging.info(f"Found {len(self.test_results)} test results")
        return self.test_results

    def get_failures(self) -> Dict[str, TestResult]:
        return {name: result for (name, result) in self.test_results.items() if not result.passed}

    def get_flakes(self) -> Dict[str, TestResult]:
        return {name: result for (name, result) in self.test_results.items() if result.flake}
