# A single S3 bucket that boots up hardened. Every protection is its own
# resource in the current AWS provider, which is a feature, not a chore:
# each control is explicit and shows up on its own line in a checkov scan.

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "s3" {
  description         = "Encryption key for the secure bucket"
  enable_key_rotation = true

  # A key with no policy falls back to a default that is easy to lock yourself
  # out of. Define it: the account root administers the key, IAM policies
  # delegate use from there. That is the AWS-recommended baseline.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "EnableRootAccountAdmin"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      }
    ]
  })
}

resource "aws_s3_bucket" "secure" {
  bucket = var.bucket_name

  # Cross-region replication is a DR / data-residency decision, not a baseline
  # security control. Turn it on when the use case calls for it.
  #checkov:skip=CKV_AWS_144:CRR is a use-case DR decision, out of scope for a baseline hardening demo
  # Event notifications are an integration concern, not a posture control.
  #checkov:skip=CKV2_AWS_62:Event notifications are use-case integration, not a security baseline
}

resource "aws_s3_bucket_public_access_block" "secure" {
  bucket                  = aws_s3_bucket.secure.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "secure" {
  bucket = aws_s3_bucket.secure.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure" {
  bucket = aws_s3_bucket.secure.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_versioning" "secure" {
  bucket = aws_s3_bucket.secure.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "secure" {
  bucket = aws_s3_bucket.secure.id
  rule {
    id     = "abort-incomplete-multipart"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_logging" "secure" {
  bucket        = aws_s3_bucket.secure.id
  target_bucket = var.log_bucket_name
  target_prefix = "s3-access/${var.bucket_name}/"
}

# Deny anything that isn't HTTPS. An explicit Deny beats any Allow, so this
# cuts every plaintext request no matter where it comes from.
resource "aws_s3_bucket_policy" "secure" {
  bucket = aws_s3_bucket.secure.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.secure.arn,
          "${aws_s3_bucket.secure.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}
