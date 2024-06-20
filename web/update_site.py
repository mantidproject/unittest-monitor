import argparse
from collections import defaultdict
from dataclasses import astuple, dataclass
from jinja2 import Template

from database_handler import DatabaseHandler


@dataclass
class ResultInfo:
    job_name: str
    build_number: str
    os: str
    result: str

    def __iter__(self):
        return iter(astuple(self))


def main():
    args = parse_args()
    results = get_test_results(args.db_path)
    format_templates(results)


def get_test_results(db_path: str):
    db_handler = DatabaseHandler(db_path)
    results = db_handler.get_all_test_results()
    results_per_test = defaultdict(list)
    for job_name, build_number, test_name, os, result in results:
        info = ResultInfo(job_name, build_number, os, result)
        results_per_test[test_name].append(info)

    return results_per_test


def format_templates(test_results):
    pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-db', '--database_path', type=str, help="path to the test results database")
    return parser.parse_args()


if __name__ == '__main__':
    main()
