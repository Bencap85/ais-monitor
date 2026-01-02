variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "instance_ids" {
  type    = list(string)
  default = [] # list of EC2 instance IDs to register with the target group
}

variable "target_port" {
  type    = number
  default = 8080
}

variable "alb_name" {
  type    = string
  default = "ais-api-alb"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "service_ports" {
  type = map(number)
  default = {
    broadcaster = 5000
    repository  = 8080
    ingestor    = 8081
  }
}

service_paths = {
  broadcaster = ["/broadcaster/*"]
  repository  = ["/repository/*"]
  ingestor    = ["/ingestor/*"]
}

variable "ingestor_service_base_path" {
    type = string
    default = "/ingestor/api/v1"
}

variable "repository_service_base_path" {
    type = string
    default = "/repository/api/v1"
}

variable "broadcaster_service_base_path" {
    type = string
    default = "/broadcaster/api/v1"
}

