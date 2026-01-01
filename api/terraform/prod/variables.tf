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

variable "service_paths" {
  type = map(list(string))
  default = {
    broadcaster = ["/broadcaster/*"]
    repository  = ["/repo/*", "/api/*"]
    ingestor    = ["/ingestor/*"]
  }
}

