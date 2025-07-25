provider "aws" {
  region = "eu-west-2"
}

# S3 Bucket
resource "aws_s3_bucket" "c18_botanists_bucket" {
  bucket = "c18-botanists-s3-bucket"
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.c18_botanists_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Glue Database
resource "aws_glue_catalog_database" "botanists_db" {
  name = "c18_botanists_db"
}

# IAM Role for Glue
resource "aws_iam_role" "glue_service_role" {
  name = "c18-botanists-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "glue.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Glue permissions
resource "aws_iam_role_policy" "glue_inline_permissions" {
  name = "c18-botanists-glue-s3-access"
  role = aws_iam_role.glue_service_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Glue Catalog Permissions
      {
        Effect = "Allow",
        Action = [
          "glue:CreateTable",
          "glue:UpdateTable",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:BatchGetPartition",
          "glue:BatchCreatePartition",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:UpdatePartition"
        ],
        Resource = "*"
      },

      # S3 Bucket Permissions
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::c18-botanists-s3-bucket",
          "arn:aws:s3:::c18-botanists-s3-bucket/*"
        ]
      },

      # CloudWatch Logs Permissions
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = [
          "arn:aws:logs:eu-west-2:129033205317:log-group:/aws-glue/*",
          "arn:aws:logs:eu-west-2:129033205317:log-group:/aws-glue/*:log-stream:*"
        ]
      }
    ]
  })
}




# Glue Crawler
resource "aws_glue_crawler" "botanists_crawler" {
  name          = "c18-botanists-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.botanists_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.c18_botanists_bucket.bucket}/"
  }

  schedule = "cron(0 23 * * ? *)"  # 11PM UTC = midnight BST, before 1AM (BST) pipeline

  configuration = jsonencode({
    Version = 1.0,
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  recrawl_policy {
    recrawl_behavior = "CRAWL_EVERYTHING"
  }
}