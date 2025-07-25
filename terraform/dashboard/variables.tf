variable "ecr_repo_name" {
  default = "c18-git-botanists-streamlit-repo"
  description = "ecr repo name"
}
variable "image_tag" {
    default = "latest"
    description = "Docker tag"
}

variable "env_vars" {
    type = map(string)
    description = "env variable"
  
}

variable "ecs-cluster-name"{
    default = "streamlit-cluster"
}