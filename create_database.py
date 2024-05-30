import sqlite3
import argparse
import os
from typing import List
from string import Template

JOBS_TABLE_CREATE_COMMAND = """
CREATE TABLE JOB (
    job_id INTEGER NOT NULL,
    job_name CHAR(128) NOT NULL,
    PRIMARY KEY(job_id)
);
"""
RUN_TABLE_CREATE_COMMAND = """
CREATE TABLE RUN (
    job_id INTEGER NOT NULL,
    build_number INTEGER NOT NULL,
    os CHAR(32) NOT NULL,
    finish_time INTEGER NOT NULL,
    PRIMARY KEY(job_id, build_number, os),
    FOREIGN KEY(job_id) REFERENCES JOB(job_id)
);
"""
TEST_RESULT_TABLE_CREATE_COMMAND = """
CREATE TABLE TEST_RESULT (
    name CHAR(128) NOT NULL,
    job_id INTEGER NOT NULL,
    build_number INTEGER NOT NULL,
    os CHAR(32) NOT NULL,
    result CHAR(32) NOT NULL,
    FOREIGN KEY(job_id, build_number, os) REFERENCES RUN(job_id, build_number, os),
    PRIMARY KEY(name, job_id, build_number, os)
);
"""
INSERT_JOB_COMMAND = Template("""
INSERT INTO JOB (job_name)
VALUES ('$job_name');
""")


def main():
    args = parse_args()
    db_name = args.db_name
    if os.path.exists(db_name):
        print(f"Database {db_name} already exists, exiting database creation script")
        return 0
    init_database(db_name, args.jobs)


def init_database(db_name: str, job_names: List[str]):
    # creates database if it doesn't exist
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute(JOBS_TABLE_CREATE_COMMAND)
        cur.execute(RUN_TABLE_CREATE_COMMAND)
        cur.execute(TEST_RESULT_TABLE_CREATE_COMMAND)
        for job in job_names:
            cur.execute(INSERT_JOB_COMMAND.substitute(job_name=job))
        conn.commit()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_name', type=str, help="e.g 'testResults.db'")
    parser.add_argument('-j', '--jobs', type=str, nargs='+', help='List of jenkins job names')
    return parser.parse_args()


if __name__ == "__main__":
    main()
