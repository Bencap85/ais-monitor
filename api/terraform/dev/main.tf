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

# SQS Queue (Kafka consumer group equivalent)
resource "aws_sqs_queue" "ais_message_group" {
  name = "ais_message_group"
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
