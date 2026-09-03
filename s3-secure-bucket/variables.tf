variable "bucket_name" {
  description = "Name of the bucket to harden."
  type        = string
  default     = "linuxelite-secure-bucket-demo"
}

variable "log_bucket_name" {
  description = "An existing bucket that receives S3 server access logs. In a real setup this is your central log bucket, created and hardened separately."
  type        = string
  default     = "linuxelite-central-log-bucket"
}
