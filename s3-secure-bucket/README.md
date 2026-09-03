# s3-secure-bucket

A single S3 bucket that boots up hardened, and a way to prove it is hardened
without an AWS account.

Companion to the post *Como Proteger um Bucket S3: SSE-KMS, IAM e o Erro
Clássico por Trás dos Vazamentos*. The post shows the core Terraform; this is
the complete, scan-clean version, plus the scanner that checks it.

## What it sets up

- KMS key with rotation and an explicit key policy (the account root
  administers the key, IAM policies delegate use from there).
- SSE-KMS default encryption with S3 Bucket Keys enabled (cuts the KMS request
  cost of encrypting every object).
- Block Public Access, all four flags, on the bucket.
- Object Ownership set to `BucketOwnerEnforced`, which disables ACLs.
- Versioning.
- A lifecycle rule that aborts incomplete multipart uploads.
- Server access logging to a central log bucket.
- A bucket policy that denies any request where `aws:SecureTransport` is false,
  so plaintext HTTP is refused.

## Prove it, no AWS needed

The point of this repo: you do not need an AWS account, credentials, or a
`terraform apply` to check the bucket is hardened. checkov reads the `.tf`
files statically and runs its S3 policy pack against them.

```bash
pip install checkov
./scan.sh
```

Real output:

```
Passed checks: 20, Failed checks: 0, Skipped checks: 2
```

The two skipped checks are intentional and documented inline in `main.tf` with
a reason, which is how you accept a check consciously instead of ignoring it:

- `CKV_AWS_144` (cross-region replication): a DR and data-residency decision,
  not a baseline security control.
- `CKV2_AWS_62` (event notifications): an integration concern, not a posture
  control.

Everything security-relevant passes: KMS encryption, versioning, access
logging, lifecycle, the public-access block, ACLs disabled, a defined KMS key
policy, and a bucket policy that does not lock out the account.

## Actually standing it up

checkov validates the config, it does not create anything. To provision the
bucket for real you need either an AWS account (`terraform init && terraform
apply`, and the KMS key does cost money) or a local emulator like LocalStack.
The scan above is the part that needs neither, which is why it is the part
worth running in CI on every change.

## Why this exists

The classic S3 leak is not a broken cipher, it is a public bucket nobody
reviewed. Hardening is configuration discipline, and configuration you can
lint. This is the bucket already linted.
