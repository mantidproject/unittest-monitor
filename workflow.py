import argparse
import os
import sys
from datetime import datetime
import logging
from typing import List, Dict, Tuple
import urllib.request
import urllib.error

from database_handler import DatabaseHandler
from jenkins_handler import JenkinsHandler
from run_result import RunResult
from ctest_log_parser import CtestOutputParser


os_names_to_log_names = {'Windows': 'ctest_msys.log',
                         'Linux': 'ctest_linux-gnu.log',
                         'MacOS': 'ctest_dawin22.log'}
logger = logging.getLogger("workflow")
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def main():
    args = parse_args()
    db_handler = DatabaseHandler("testResults.db")

    for job in args.jobs:
        logger.info(f"Searching for new builds in {job}")
        for build_number, finish_time in job_builds_to_be_parsed(job, args.jenkins_server, db_handler):
            logs = retrieve_log_files(job, build_number)
            for os, log_file in logs.items():
                parser = CtestOutputParser(log_file)
                results = parser.parse()
                run_result = RunResult(job, build_number, finish_time, os, results)
                db_handler.ingest_results(run_result)

    return 0


def job_builds_to_be_parsed(job_name: str, jenkins_url: str, db_handler: DatabaseHandler) -> List[Tuple[str, str]]:
    """
    :param job_name: str name of the jenkins job
    :param jenkins_url: url to the jenkins server
    :param db_handler: handle one the test results' database
    :return: List of tuples of runs and finish times that have taken place since the last data ingest
    """
    jenkins_handler = JenkinsHandler(jenkins_url)
    build_number, finish_time = db_handler.get_latest_build(job_name)
    if finish_time is None:
        logger.info("No previous builds found in the database")
        return jenkins_handler.get_all_builds_after_timestamp(job_name, 0)
    logger.info(f"Found most recent build {build_number} at {datetime.fromtimestamp(int(finish_time))}")
    return jenkins_handler.get_all_builds_after_timestamp(job_name, int(finish_time))


def retrieve_log_files(job_name: str, build_number: str) -> Dict[str, str]:
    """
    :param job_name: str name of the jenkins job
    :param build_number: str build number
    :return: Dictionary of str os names to their respective downloaded log files
    """
    logger.info(f"Retrieving log files for {job_name} build {build_number}")
    local_log_files = {}
    # this url works for pipeline jobs, pr jobs don't have a 'source' directory
    base_url = f"https://builds.mantidproject.org/job/{job_name}/{build_number}/artifact/source/build/test_logs/"
    for os_name, log_file_name in os_names_to_log_names.items():
        log_file_url = base_url + log_file_name
        local_log_file_path = f"./log_files/{job_name}_{build_number}_{log_file_name}"
        try:
            logger.info(f"Searching for {log_file_url}")
            os.mknod(local_log_file_path)
            urllib.request.urlretrieve(log_file_url, local_log_file_path)
        except urllib.error.HTTPError as e:
            if str(e) == "HTTP Error 404: Not Found":
                logger.info(f"{os_name} log not found for {job_name} build number {build_number}")
                continue
            else:
                raise e

        logger.info(f"Found log file for {os_name}: {local_log_file_path}")
        local_log_files[os_name] = local_log_file_path

    return local_log_files


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-db', '--database_name', type=str, help="e.g 'testResults.db'")
    parser.add_argument('-s', '--jenkins_server', type=str, help="url to the jenkins server")
    parser.add_argument('-j', '--jobs', type=str, nargs='+', help='List of jenkins job names')
    return parser.parse_args()


if __name__ == "__main__":
    main()
