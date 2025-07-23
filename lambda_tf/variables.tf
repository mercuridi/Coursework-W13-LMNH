variable "vpc_id" {
  description = "VPC where RDS and Lambda are deployed"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for Lambda"
  type        = list(string)
}
