#!/bin/bash

python create_database.py testResults.db --jobs main_nightly_deployment release-next_nightly_deployment
python workflow.py --database_name testResults.db --jenkins_server https://builds.mantidproject.org --jobs main_nightly_deployment release-next_nightly_deployment