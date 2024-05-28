import sqlite3
from typing import Tuple

from run_result import RunResult


class DatabaseHandler:

    def __init__(self, address: str):
        self.connection = sqlite3.Connection(address)

    def get_latest_build(self, job_name: str) -> Tuple[str, str]:
        """
        Returns the most recent build number and its finish time stored in the database
        for the given job name
        """
        query = f"""
        SELECT RUN_NUMBER, FINISH_TIME FROM run 
        INNER JOIN job ON run.JOB_ID = job.JOB_ID WHERE job.JOB_NAME = '{job_name}' 
        ORDER BY datetime(FINISH_TIME) DESC Limit 1
        """
        cur = self.connection.cursor()
        result = cur.execute(query)
        return result.fetchone()

    def ingest_results(self, run_result: RunResult):
        run_id = self._add_run(run_result)
        cur = self.connection.cursor()
        for test_name, test_result in run_result.test_results.items():
            result_text = test_result.get_result_text()
            query = f"""
            INSERT INTO test_result (RESULT_ID, RUN_ID, NAME, RESULT)
            VALUES (NULL, {run_id}, '{test_name}', '{result_text}')
            """
            cur.execute(query)

        self.connection.commit()

    def _add_run(self, run_result: RunResult) -> int:
        job_id = self._get_job_id(run_result.job_name)
        query = f"""
        INSERT INTO run (RUN_ID, RUN_NUMBER, JOB_ID, OS, FINISH_TIME)
        VALUES (NULL, '{run_result.run_number}', {job_id}, '{run_result.os}', '{run_result.finish_time}')
        """
        cur = self.connection.cursor()
        cur.execute(query)
        self.connection.commit()
        run_id = cur.execute(f"SELECT RUN_ID FROM run WHERE RUN_NUMBER = '{run_result.run_number}'").fetchone()[0]
        return int(run_id)

    def _get_job_id(self, job_name: str) -> int:
        cur = self.connection.cursor()
        result = cur.execute(f"SELECT JOB_ID FROM job WHERE JOB_NAME = '{job_name}'")
        return int(result.fetchone()[0])





