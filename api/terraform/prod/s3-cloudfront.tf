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

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-${aws_s3_bucket.ui_bucket.id}"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
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
