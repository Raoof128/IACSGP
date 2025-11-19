# Outputs for the secure infrastructure

output "s3_bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.secure_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN of the created S3 bucket"
  value       = aws_s3_bucket.secure_bucket.arn
}

output "security_group_id" {
  description = "ID of the secure security group"
  value       = aws_security_group.secure_app.id
}

output "ebs_volume_id" {
  description = "ID of the encrypted EBS volume"
  value       = aws_ebs_volume.secure_volume.id
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.secure_db.endpoint
  sensitive   = true
}

output "rds_instance_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.secure_db.id
}
