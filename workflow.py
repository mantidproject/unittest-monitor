from typing import List, Dict, Tuple
import urllib.request
import urllib.error

from database_handler import DatabaseHandler
from jenkins_handler import JenkinsHandler
from run_result import RunResult
from ctest_log_parser import CtestOutputParser


db_handler = DatabaseHandler("testResults.db")
jenkins_handler = JenkinsHandler("https://builds.mantidproject.org")
os_names_to_log_names = {'Windows': 'ctest_msys.log',
                         'Linux': 'ctest_linux-gnu.log',
                         'MacOS': 'ctest_dawin22.log'}
jenkins_jobs = {'main_nightly_deployment', 'release-next_nightly_deployment'}


def main():
    for job in jenkins_jobs:
        for run_number, finish_time in job_builds_to_be_parsed(job):
            logs = retrieve_log_files(job, run_number)
            for os, log_file in logs:
                parser = CtestOutputParser(log_file)
                results = parser.parse()
                run_result = RunResult(job, run_number, finish_time, os, results)
                db_handler.ingest_results(run_result)

    return 0


def job_builds_to_be_parsed(job_name: str) -> List[Tuple[str, str]]:
    """
    :param job_name: str name of the jenkins job
    :return: List of tuples of runs and finish times that have taken place since the last data ingest
    """
    _, finish_time = db_handler.get_latest_build(job_name)
    return jenkins_handler.get_all_builds_after_timestamp(job_name, int(finish_time))


def retrieve_log_files(job_name: str, run_number: str) -> Dict[str, str]:
    """
    :param job_name: str name of the jenkins job
    :param run_number: str run number
    :return: Dictionary of str os names to their respective downloaded log files
    """
    local_log_files = {}
    # this url works for pipeline jobs, pr jobs don't have a 'source' directory
    base_url = f"https://builds.mantidproject.org/job/{job_name}/{run_number}/artifact/source/build/test_logs/"
    for os_name, log_file_name in os_names_to_log_names.items():
        log_file_url = base_url + log_file_name
        local_log_file_path = f"./log_files/{job_name}_{run_number}_{log_file_name}"
        try:
            urllib.request.urlretrieve(log_file_url, local_log_file_path)
        except urllib.error.HTTPError as e:
            if str(e) == "HTTP Error 404: Not Found":
                print(f"{os_name} log not found for {job_name} run number {run_number}")
                continue
            else:
                raise e

        local_log_files[os_name] = local_log_file_path

    return local_log_files


if __name__ == "main":
    main()
