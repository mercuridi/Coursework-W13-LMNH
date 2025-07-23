provider "aws" {
    region = "eu-west-2"
}

resource "aws_ecr_repository" "c18-git-botanists-etl-repo" {
  name                 = "c18-git-botanists-etl-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c18-git-botanists-rds-to-s3-etl-repo" {
  name                 = "c18-git-botanists-rds-to-s3-etl-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c18-git-botanists-streamlit-repo" {
  name                 = "c18-git-botanists-streamlit-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}