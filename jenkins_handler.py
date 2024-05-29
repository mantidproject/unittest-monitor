import jenkins
import logging
from typing import List, Tuple

logger = logging.getLogger()


class JenkinsHandler:

    def __init__(self, url: str):
        self.server = jenkins.Jenkins(url)

    def get_all_builds_after_timestamp(self, job_name: str, time_stamp: int) -> List[Tuple[str, str]]:
        builds = []
        for build in self.server.get_job_info(job_name)['builds']:
            build_info = self.server.get_build_info(job_name,  build['number'])
            if not build_info['inProgress'] and build_info['timestamp'] > time_stamp and build_info['result'] != 'ABORTED':
                builds.append((build['number'], str(build_info['timestamp'])))
        builds_output = '\n'.join([f'{number} at {finish}' for number, finish in builds])
        logger.info(f"Found {len(builds)} more builds to ingest\n{builds_output}")
        return builds



