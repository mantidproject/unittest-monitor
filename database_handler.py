import logging
import sqlite3
from typing import Tuple

from run_result import RunResult

logger = logging.getLogger("DatabaseHandler")


class DatabaseHandler:

    def __init__(self, address: str):
        self.connection = sqlite3.Connection(address)

    def get_latest_build(self, job_name: str) -> Tuple[str | None, str | None]:
        """
        Returns the most recent build number and its finish time stored in the database
        for the given job name
        """
        query = f"""
        SELECT build_number, finish_time FROM RUN 
        INNER JOIN JOB ON RUN.job_id = JOB.job_id WHERE JOB.job_name = '{job_name}' 
        ORDER BY datetime(finish_time) DESC Limit 1
        """
        cur = self.connection.cursor()
        result = cur.execute(query)
        row = result.fetchone()
        if row is None:
            return None, None
        return row

    def ingest_results(self, run_result: RunResult):
        job_id = self._get_job_id(run_result.job_name)
        self._add_run(run_result, job_id)
        cur = self.connection.cursor()
        for test_name, test_result in run_result.test_results.items():
            result_text = test_result.get_result_text()
            query = f"""
            INSERT INTO TEST_RESULT (name, job_id, build_number, os, result)
            VALUES ('{test_name}', {job_id}, '{run_result.build_number}', '{run_result.os}', '{result_text}')
            """
            cur.execute(query)

        self.connection.commit()

    def _add_run(self, run_result: RunResult, job_id: int):
        query = f"""
        INSERT INTO RUN (job_id, build_number, os, finish_time)
        VALUES ({job_id}, '{run_result.build_number}', '{run_result.os}', '{run_result.finish_time}')
        """
        cur = self.connection.cursor()
        cur.execute(query)
        self.connection.commit()

    def _get_job_id(self, job_name: str) -> int:
        cur = self.connection.cursor()
        result = cur.execute(f"SELECT job_id FROM JOB WHERE job_name = '{job_name}'")
        return int(result.fetchone()[0])
