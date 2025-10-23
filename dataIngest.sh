#!/bin/bash

python create_database.py testResults.db --jobs main_nightly release-next_nightly
python workflow.py --database_name testResults.db --jenkins_server https://builds.mantidproject.org --jobs main_nightly release-next_nightly
python update_site.py --database_path testResults.db