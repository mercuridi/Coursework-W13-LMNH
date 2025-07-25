provider "aws" {
  region = "eu-west-2"
}

# Reference existing ECS Cluster
data "aws_ecs_cluster" "existing_cluster" {
  cluster_name = "c18-ecs-cluster"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/c18-botanists-s3-pipeline"
  retention_in_days = 7
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "c18-botanists-ecs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "data_pipeline_task" {
  family                   = "c18-botanists-s3-pipeline-task"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name      = "c18-botanists-s3-pipeline"
    image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c18-git-botanists-rds-to-s3-etl-repo:latest"
    essential = true
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs_log_group.name
        awslogs-region        = "eu-west-2"
        awslogs-stream-prefix = "ecs"
      }
    }
  }])
}

# IAM Role for EventBridge Scheduler
resource "aws_iam_role" "eventbridge_invoke_ecs_role" {
  name = "c18-botanists-eventbridge-ecs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "eventbridge_invoke_policy" {
  name = "c18-botanists-eventbridge-ecs-policy"
  role = aws_iam_role.eventbridge_invoke_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

# EventBridge Scheduler
resource "aws_scheduler_schedule" "daily_pipeline_trigger" {
  name       = "daily-data-pipeline"
  group_name = "default"
  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 * * ? *)" # 1am BST = 00:00 UTC

  target {
    arn      = data.aws_ecs_cluster.existing_cluster.arn
    role_arn = aws_iam_role.eventbridge_invoke_ecs_role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.data_pipeline_task.arn
      launch_type         = "FARGATE"
      network_configuration {
        subnets          = ["subnet-0aed07ac008a10da9", "subnet-0f10662561eade8c3", "subnet-0679d4b1f9e7839ef"] # Public
        assign_public_ip = true
      }
      platform_version = "LATEST"
    }
  }
}
