aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker build -t c18-git-botanists-streamlit-repo -f src/dashboard/dockerfile .

docker tag c18-git-botanists-streamlit-repo:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c18-git-botanists-streamlit-repo:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c18-git-botanists-streamlit-repo:latest