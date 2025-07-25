aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker build -t c18-git-botanists-rds-to-s3-etl-repo -f src/api_to_rds_pipeline/dockerfile .

docker tag c18-git-botanists-rds-to-s3-etl-repo:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c18-git-botanists-rds-to-s3-etl-repo:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c18-git-botanists-rds-to-s3-etl-repo:latest

# run "bash src/rds_to_s3_pipeline/deploy.sh" from root