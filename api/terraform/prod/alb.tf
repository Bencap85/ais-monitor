# --- Security group for the ALB (allow inbound HTTP from anywhere) ---
resource "aws_security_group" "alb_sg" {
  name        = "${var.alb_name}-sg"
  description = "ALB security group"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.alb_name}-sg"
    Env  = var.env
  }
}

# --- Security group for EC2 instances (allow traffic from ALB to service ports) ---
resource "aws_security_group" "instance_sg" {
  name        = "${var.alb_name}-instance-sg"
  description = "Allow traffic from ALB to instances"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow ALB to reach broadcaster port"
    from_port       = var.service_ports["broadcaster"]
    to_port         = var.service_ports["broadcaster"]
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    description     = "Allow ALB to reach repository port"
    from_port       = var.service_ports["repository"]
    to_port         = var.service_ports["repository"]
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    description     = "Allow ALB to reach ingestor port"
    from_port       = var.service_ports["ingestor"]
    to_port         = var.service_ports["ingestor"]
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.alb_name}-instance-sg"
    Env  = var.env
  }
}

# --- Application Load Balancer ---
resource "aws_lb" "alb" {
  name                       = var.alb_name
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.alb_sg.id]
  subnets                    = var.subnet_ids
  enable_deletion_protection = false

  tags = {
    Name = var.alb_name
    Env  = var.env
  }
}

# --- Target groups (one per service) ---
resource "aws_lb_target_group" "broadcaster_tg" {
  name        = "${var.alb_name}-broadcaster-tg"
  port        = var.service_ports["broadcaster"]
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${var.alb_name}-broadcaster-tg"
    Env  = var.env
  }
}

resource "aws_lb_target_group" "repository_tg" {
  name        = "${var.alb_name}-repository-tg"
  port        = var.service_ports["repository"]
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${var.alb_name}-repository-tg"
    Env  = var.env
  }
}

resource "aws_lb_target_group" "ingestor_tg" {
  name        = "${var.alb_name}-ingestor-tg"
  port        = var.service_ports["ingestor"]
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${var.alb_name}-ingestor-tg"
    Env  = var.env
  }
}

# --- HTTP listener with default forwarding to repository TG ---
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.repository_tg.arn
  }
}

# --- Listener rules: path-based routing to each service TG ---
resource "aws_lb_listener_rule" "repository_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.repository_tg.arn
  }

  condition {
    path_pattern { values = var.service_paths["repository"] }
  }
}

resource "aws_lb_listener_rule" "broadcaster_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.broadcaster_tg.arn
  }

  condition {
    path_pattern { values = var.service_paths["broadcaster"] }
  }
}

resource "aws_lb_listener_rule" "ingestor_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 30

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ingestor_tg.arn
  }

  condition {
    path_pattern { values = var.service_paths["ingestor"] }
  }
}

# --- Register existing EC2 instances with each target group ---
resource "aws_lb_target_group_attachment" "broadcaster_instances" {
  for_each = { for id in var.instance_ids : id => id }

  target_group_arn = aws_lb_target_group.broadcaster_tg.arn
  target_id        = each.value
  port             = var.service_ports["broadcaster"]
}

resource "aws_lb_target_group_attachment" "repository_instances" {
  for_each = { for id in var.instance_ids : id => id }

  target_group_arn = aws_lb_target_group.repository_tg.arn
  target_id        = each.value
  port             = var.service_ports["repository"]
}

resource "aws_lb_target_group_attachment" "ingestor_instances" {
  for_each = { for id in var.instance_ids : id => id }

  target_group_arn = aws_lb_target_group.ingestor_tg.arn
  target_id        = each.value
  port             = var.service_ports["ingestor"]
}

# --- Outputs ---
output "alb_arn" {
  value = aws_lb.alb.arn
}

output "alb_dns_name" {
  value       = aws_lb.alb.dns_name
  description = "Public DNS name for the ALB"
}

output "broadcaster_tg_arn" {
  value       = aws_lb_target_group.broadcaster_tg.arn
  description = "Broadcaster target group ARN"
}

output "repository_tg_arn" {
  value       = aws_lb_target_group.repository_tg.arn
  description = "Repository target group ARN"
}

output "ingestor_tg_arn" {
  value       = aws_lb_target_group.ingestor_tg.arn
  description = "Ingestor target group ARN"
}

