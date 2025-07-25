variable "vpc_id" {
  description = "VPC where RDS and Lambda are deployed"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for NAT Gateway"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs to host Lambda"
  type        = list(string)
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
