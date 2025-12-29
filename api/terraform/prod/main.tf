data "aws_caller_identity" "current" {}

provider "aws" {
  region = "us-east-2"
}

# SNS Topic (Kafka topic equivalent)
resource "aws_sns_topic" "ais_message" {
  name = "ais_message"
}

# SQS Queue (Kafka consumer group equivalent)
resource "aws_sqs_queue" "ais_message_group" {
  name = "ais_message_group"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "sqs:SendMessage"
        Resource = "arn:aws:sqs:us-east-2:${data.aws_caller_identity.current.account_id}:ais_message_group"
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.ais_message.arn
          }
        }
      }
    ]
  })
}

# Subscription: wire queue to topic
resource "aws_sns_topic_subscription" "ais_message_sub" {
  topic_arn = aws_sns_topic.ais_message.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.ais_message_group.arn
}

# Outputs for convenience
output "topic_arn" {
  value = aws_sns_topic.ais_message.arn
}

output "queue_url" {
  value = aws_sqs_queue.ais_message_group.id
}
