# Coursework-W13-LMNH
## Project introduction

## Technologies used
1. ECR - Docker images
2. ECS/Fargate to run cleaning/pipeline
3. RDS for short term data (24 hours)
4. S3 for long term storage - time-partitioned
5. Streamlit dashboard for visualisations - hosted on ECS service

## File structures
- .github
    - Utility folder used for github configs
- assets
    - Folder containing project-related diagrams, including the ERD and architecture
- db
    - Folder containing the schema script for the remote database
    - Also contains an initial seed script to test the database on static data if required
- src
    - api_to_rds_pipeline
        - Folder to store scripts used in the first pipeline
    - rds_to_s3_pipeline
        - Folder to store scripts used in the second pipeline
    - utils
        - Folder to store library functions used in multiple files
- terraform
    - ecr_repos_tf
        - Contains terraform scripts for the AWS ECR repos
    - fargate_tf
        - Contains terraform scripts for the AWS Fargate tasks
    - lambda_tf
        - Contains terraform scripts for the AWS Lambda functions used in Fargate tasks
    - s3_tf
        - Contains terraform scripts for the AWS S3 buckets used to store long term data
- test
    - Contains testing scripts for each module

## How to run
1. Install Python 3 on your system
2. Run `python3 -m venv .venv` to make a new virtual environment
3. Run `activate .venv/bin/activate` to enter the venv
4. Run `pip install -r requirements.txt` at the top level of the project
5. To test: `python3 -m pytest test/*.py`
6. To run the first pipeline: `python3 src/api_to_rds_pipeline/pipeline.py`
7. To run the second pipeline: `python3 src/rds_to_s3_pipeline/pipeline.py`
8. To run the dashboard (localhost): ``

Each pipeline also has a `deploy.sh` script to ease deployment of new versions to the cloud repository.
The user credentials it uses rely on secrets stored on the local machine.