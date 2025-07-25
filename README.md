# Coursework-W13-LMNH
## Project introduction
Project (case study) for LMNH to help with tracking their extensive range of plants.
LMNH installed monitors on each of the plants in their conservatory, reporting soil moisture and soil temperature readings.
Further, the readings include the date and time of when the plant was last watered and their origin, or "home country".
We planned and implemented a 2-step ETL pipeline to help LMNH keep track of their plants:
- API to RDS, to collect the data from the API endpoints representing each monitor every minute
- RDS to S3, to send data from the day before to the long term storage S3 bucket
We also developed a dashboard for the botanists employed at LMNH, so that they could easily monitor each plant and even partition their analysis by the assigned botanist.

## Technologies used
1. ECR - Docker images
2. ECS/Fargate/Lambda to run pipelines
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
8. To run the dashboard (localhost): `streamlit run src/dashboard/streamlit_dashboard.py`

Each pipeline also has a `deploy.sh` script to ease deployment of new versions to the cloud repository.
The user credentials it uses rely on secrets stored on the local machine.

## Future improvements
- API to RDS load script needs optimisations - check database directly for existence instead of downloading the table on each change
- Dashboard could be improved on UX/UI