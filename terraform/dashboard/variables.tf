variable "ecr_repo_name" {
  default = "c18-git-botanists-streamlit-repo"
  description = "ecr repo name"
}
variable "image_tag" {
    default = "latest"
    description = "Docker tag"
}


variable "ecs-cluster-name"{
    default = "streamlit-cluster"
}

variable "DB_HOST" {
  description = "IP to access the RDS"
  type        = string
}
variable "DB_PORT" {
  description = "Port for MS SQLServer"
  type        = string
}
variable "DB_USER" {
  description = "Group-specific username for RDS"
  type        = string
}
variable "DB_PASSWORD" {
  description = "Group-specific password for RDS"
  type        = string
}
variable "DB_NAME" {
  description = "Database name for RDS"
  type        = string
}
variable "DB_SCHEMA" {
  description = "Group-specific schema for RDS"
  type        = string
}

variable "AWS_ACCESS_KEY_ID" {
  description = "access key for S3"
  type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  description = "access key for S3"
  type = string
}