provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    sns = "http://localhost:4566"
    sqs = "http://localhost:4566"
  }
}

# SNS Topic (Kafka topic equivalent)
resource "aws_sns_topic" "ais_message" {
  name = "ais_message"
}

# Repository queue
resource "aws_sqs_queue" "ais_repository_queue" {
  name = "ais_repository_queue"

  # Example sensible defaults; tune as needed
  visibility_timeout_seconds = 60
  message_retention_seconds  = 1209600  # 14 days
  receive_wait_time_seconds  = 20       # long polling
}

# Broadcaster queue
resource "aws_sqs_queue" "ais_broadcaster_queue" {
  name = "ais_broadcaster_queue"

  visibility_timeout_seconds = 60
  message_retention_seconds  = 1209600
  receive_wait_time_seconds  = 20
}

# SQS policy helper (one per queue) to allow SNS to send messages
locals {
  repo_queue_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.ais_repository_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.ais_message.arn
          }
        }
      }
    ]
  })

  broadcaster_queue_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.ais_broadcaster_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.ais_message.arn
          }
        }
      }
    ]
  })
}

# Attach policies
resource "aws_sqs_queue_policy" "repo_policy" {
  queue_url = aws_sqs_queue.ais_repository_queue.id
  policy    = local.repo_queue_policy
}

resource "aws_sqs_queue_policy" "broadcaster_policy" {
  queue_url = aws_sqs_queue.ais_broadcaster_queue.id
  policy    = local.broadcaster_queue_policy
}

# Subscriptions: wire both queues to the topic
resource "aws_sns_topic_subscription" "ais_repo_sub" {
  topic_arn = aws_sns_topic.ais_message.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.ais_repository_queue.arn
}

resource "aws_sns_topic_subscription" "ais_broadcaster_sub" {
  topic_arn = aws_sns_topic.ais_message.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.ais_broadcaster_queue.arn
}

# Outputs for convenience
output "topic_arn" {
  value = aws_sns_topic.ais_message.arn
}

output "repository_queue_url" {
  value = aws_sqs_queue.ais_repository_queue.id
}

output "repository_queue_arn" {
  value = aws_sqs_queue.ais_repository_queue.arn
}

output "broadcaster_queue_url" {
  value = aws_sqs_queue.ais_broadcaster_queue.id
}

output "broadcaster_queue_arn" {
  value = aws_sqs_queue.ais_broadcaster_queue.arn
}
