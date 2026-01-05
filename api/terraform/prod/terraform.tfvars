alb_name   = "ais-api-alb"
env        = "dev"
vpc_id     = "vpc-001e3fa5430068b05"
subnet_ids = ["subnet-091a8716cb204b874", "subnet-0ef070a1bf53fb667", "subnet-0364e5849b09614f9"]

instance_ids = ["i-0555741714ac8d2de"]
service_ports = {
  broadcaster = 5000
  repository  = 8080
  ingestor    = 8081
}
service_paths = {
  broadcaster = ["/broadcaster/*"]
  repository  = ["/repo/*", "/api/*"]
  ingestor    = ["/ingestor/*"]
  ws          = ["/socket.io*"]
}

alb_dns_name        = "ais-api-alb-1011091891.us-east-2.elb.amazonaws.com"
alb_origin_protocol = "http-only"
