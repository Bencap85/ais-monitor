# S3 bucket for static site
resource "aws_s3_bucket" "ui_bucket" {
  bucket        = "ui-static-build-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket                  = aws_s3_bucket.ui_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "OAI for ${aws_s3_bucket.ui_bucket.id}"
}

# S3 bucket policy to allow CloudFront OAI
data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions = ["s3:GetObject"]
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.oai.iam_arn]
    }
    resources = ["${aws_s3_bucket.ui_bucket.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "policy" {
  bucket = aws_s3_bucket.ui_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "cdn" {
  origin {
    domain_name = aws_s3_bucket.ui_bucket.bucket_regional_domain_name
    origin_id   = "s3-${aws_s3_bucket.ui_bucket.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  origin {
    domain_name = var.alb_dns_name
    origin_id   = var.alb_origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = var.alb_origin_protocol
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_All"

  # Default behavior -> S3 UI
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-${aws_s3_bucket.ui_bucket.id}"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
    compress    = true
    min_ttl     = 0
    default_ttl = 60
    max_ttl     = 86400
  }

  # API behavior: repository
  ordered_cache_behavior {
    path_pattern           = "/repository/*"
    target_origin_id       = var.alb_origin_id
    viewer_protocol_policy = "redirect-to-https"

    # Use the full allowed methods set because API needs POST/PUT/DELETE
    allowed_methods = ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true

    forwarded_values {
      query_string = true
      cookies { forward = "none" }
      headers = ["Host", "Origin", "Authorization", "X-Requested-With"]
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # API behavior: broadcaster (socket namespace)
  ordered_cache_behavior {
    path_pattern           = "/broadcaster/*"
    target_origin_id       = var.alb_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    forwarded_values {
      query_string = true
      cookies { forward = "none" }
      headers = ["Host", "Origin", "Authorization", "X-Requested-With"]
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # Socket.IO handshake/polling (wildcard)
  ordered_cache_behavior {
    path_pattern           = "/socket.io*"
    target_origin_id       = var.alb_origin_id
    viewer_protocol_policy = "redirect-to-https"

    # Socket.IO needs POST for polling, so use the full set
    allowed_methods = ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]
    cached_methods  = ["GET", "HEAD"]
    compress        = true

    forwarded_values {
      query_string = true
      cookies { forward = "none" }
      headers = ["Host", "Origin", "Authorization", "X-Requested-With"]
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # Additional API path (ingestor)
  ordered_cache_behavior {
    path_pattern           = "/ingestor/*"
    target_origin_id       = var.alb_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    forwarded_values {
      query_string = true
      cookies { forward = "none" }
      headers = ["Host", "Origin", "Authorization", "X-Requested-With"]
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

output "cloudfront_domain" {
  description = "CloudFront domain to use as API/UI base (https://<domain>)"
  value       = aws_cloudfront_distribution.cdn.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution id (for invalidations)"
  value       = aws_cloudfront_distribution.cdn.id
}
