# Phase 3: Website Deployment with Custom Domains - Implementation Guide

**Date:** March 1, 2026
**Status:** Ready to Deploy
**Issue:** #6 (pipeline-factory)

---

## Overview

Phase 3 deploys the Los Tules website with custom domain support. The infrastructure is fully configured:

- ✅ Route 53 hosted zone created (lostuleskc.com)
- ✅ GoDaddy nameservers updated (or ready for automation)
- ✅ Pipeline configured with domain environment variables
- ✅ Website stack supports custom domains
- ✅ ACM certificate automation ready

---

## Current State

### Domain Configuration
- **Domain:** lostuleskc.com
- **Hosted Zone ID:** Z01235092D2OIX9KFYPQ8
- **Hosted Zone Name:** lostuleskc.com
- **Status:** Route 53 zone created, nameservers configured

### Pipeline Configuration
- **Pipeline:** los-tules-website-pipeline
- **Environment Variables:** DOMAIN_NAME, HOSTED_ZONE_ID, HOSTED_ZONE_NAME
- **Status:** Ready to deploy with domain configuration

### Website Stack
- **Stack:** LosTulesWebsiteStack
- **Features:** S3, CloudFront, ACM, Route 53
- **Domain Support:** Full support for custom domains
- **Status:** Ready to deploy

---

## Deployment Steps

### Step 1: Verify DNS Propagation

Before deploying, verify that GoDaddy nameservers have been updated and DNS is propagating:

```bash
# Check nameservers
dig lostuleskc.com NS +short

# Should return AWS nameservers:
# ns-1071.awsdns-05.org
# ns-1606.awsdns-08.co.uk
# ns-420.awsdns-52.com
# ns-670.awsdns-19.net

# Check DNS resolution
dig lostuleskc.com +short

# Should eventually return CloudFront IP
```

**Note:** DNS propagation can take 5-30 minutes. If not propagated yet, wait and retry.

### Step 2: Trigger Pipeline Deployment

The Los Tules website pipeline is configured to deploy with the custom domain. You can trigger it by:

**Option A: Push to GitHub (Automatic)**
```bash
cd websites/los-tules-website
git add .
git commit -m "Trigger Phase 3 deployment with custom domain"
git push origin main
```

**Option B: Manual Pipeline Trigger**
```bash
# Go to AWS CodePipeline console
# Find "los-tules-website-pipeline"
# Click "Release change" to manually trigger
```

### Step 3: Monitor Deployment

The pipeline will:
1. Pull code from GitHub
2. Build Next.js site
3. Install Python dependencies
4. Run CDK deploy with domain configuration
5. Create ACM certificate
6. Update CloudFront with custom domain
7. Create Route 53 A-record

**Monitor in AWS Console:**
- CodePipeline: los-tules-website-pipeline
- CodeBuild: los-tules-website-build
- CloudFormation: LosTulesWebsiteStack
- CloudWatch Logs: /aws/codebuild/los-tules-website-build

### Step 4: Verify Deployment

After deployment completes (5-10 minutes):

```bash
# Check CloudFormation outputs
aws cloudformation describe-stacks \
  --stack-name LosTulesWebsiteStack \
  --query 'Stacks[0].Outputs' \
  --output table

# Should show:
# - WebsiteURL: https://lostuleskc.com
# - CustomDomainURL: https://lostuleskc.com
# - CloudFrontDistributionID: E...
```

### Step 5: Test Website

**Test checklist:**
- [ ] Visit https://lostuleskc.com - site loads
- [ ] Check all images load correctly
- [ ] Test navigation (scroll, click buttons)
- [ ] Click "View Our Menu" - PDF opens
- [ ] Test on mobile (responsive design)
- [ ] Check browser console for errors
- [ ] Verify SSL certificate is valid (green lock)

**Test commands:**
```bash
# Check SSL certificate
openssl s_client -connect lostuleskc.com:443 -servername lostuleskc.com

# Check DNS resolution
nslookup lostuleskc.com

# Check CloudFront cache
curl -I https://lostuleskc.com
```

---

## What Happens During Deployment

### 1. ACM Certificate Creation
- CDK creates ACM certificate for lostuleskc.com
- Certificate validation via DNS (automatic)
- Route 53 creates CNAME record for validation
- Certificate issued (usually 1-2 minutes)

### 2. CloudFront Update
- CloudFront distribution updated with certificate
- Custom domain added to distribution
- SSL/TLS enabled for custom domain
- Cache invalidation triggered

### 3. Route 53 A-Record Creation
- A-record created for lostuleskc.com
- Points to CloudFront distribution
- Alias record (no additional charges)

### 4. DNS Propagation
- Route 53 returns CloudFront IP for lostuleskc.com
- DNS caches update (5-30 minutes)
- Website accessible at custom domain

---

## Troubleshooting

### Issue: "Certificate validation failed"

**Cause:** Route 53 hosted zone not properly configured or DNS not propagating

**Solution:**
```bash
# Verify hosted zone exists
aws route53 list-hosted-zones --query "HostedZones[?Name=='lostuleskc.com.']"

# Verify nameservers in GoDaddy
# Go to GoDaddy > My Products > Domains > lostuleskc.com > Manage DNS
# Check that nameservers match AWS output

# Wait for DNS propagation
dig lostuleskc.com NS +short
```

### Issue: "Website not accessible at custom domain"

**Cause:** DNS not propagated or CloudFront not updated

**Solution:**
```bash
# Check DNS resolution
dig lostuleskc.com +short

# Check CloudFront distribution
aws cloudfront get-distribution --id E... --query 'Distribution.DistributionConfig.Aliases'

# Check Route 53 record
aws route53 list-resource-record-sets \
  --hosted-zone-id Z01235092D2OIX9KFYPQ8 \
  --query "ResourceRecordSets[?Name=='lostuleskc.com.']"

# Wait for DNS propagation (can take up to 48 hours)
```

### Issue: "SSL certificate error"

**Cause:** Certificate not issued or CloudFront not using certificate

**Solution:**
```bash
# Check certificate status
aws acm list-certificates --query "CertificateSummaryList[?DomainName=='lostuleskc.com']"

# Check certificate details
aws acm describe-certificate --certificate-arn arn:aws:acm:...

# Redeploy if needed
cd websites/los-tules-website/infra
cdk deploy --require-approval never
```

### Issue: "Pipeline deployment failed"

**Cause:** Various - check CodeBuild logs

**Solution:**
```bash
# Check CodeBuild logs
aws logs tail /aws/codebuild/los-tules-website-build --follow

# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name LosTulesWebsiteStack \
  --query 'StackEvents[0:10]'

# Redeploy manually
cd websites/los-tules-website/infra
cdk deploy --require-approval never
```

---

## Rollback Plan

If something goes wrong, you can rollback to CloudFront-only deployment:

```bash
# Remove domain configuration
export DOMAIN_NAME=""
export HOSTED_ZONE_ID=""
export HOSTED_ZONE_NAME=""

# Redeploy
cd websites/los-tules-website/infra
cdk deploy --require-approval never

# Website will be accessible at CloudFront URL only
```

---

## After Successful Deployment

### 1. Update Documentation
- [ ] Update README.md with custom domain URL
- [ ] Document deployment process
- [ ] Add troubleshooting guide

### 2. Monitor Website
- [ ] Set up CloudWatch alarms for errors
- [ ] Monitor CloudFront cache hit ratio
- [ ] Check Route 53 query metrics

### 3. Next Steps
- [ ] Test CI/CD pipeline with code changes
- [ ] Add more domains to domain-management
- [ ] Deploy additional websites
- [ ] Set up monitoring and alerting

---

## Key Files

### Configuration
- `website-infrastructure/pipeline-factory/config/websites.json` - Domain configuration
- `websites/los-tules-website/infra/app.py` - Website stack with domain support

### Infrastructure
- `website-infrastructure/shared-website-constructs/shared_website_constructs/website_stack.py` - WebsiteStack with domain support
- `website-infrastructure/pipeline-factory/pipeline_factory/pipeline_stack.py` - Pipeline with domain environment variables

### Domain Management
- `website-infrastructure/domain-management/domain_management/hosted_zone_stack.py` - Route 53 hosted zone creation
- `website-infrastructure/domain-management/lambda/godaddy_updater.py` - GoDaddy automation

---

## Success Criteria

- [x] Route 53 hosted zone created
- [x] GoDaddy nameservers updated
- [x] Pipeline configured with domain variables
- [x] Website stack supports custom domains
- [ ] Pipeline deployment triggered
- [ ] ACM certificate created
- [ ] CloudFront updated with custom domain
- [ ] Route 53 A-record created
- [ ] Website accessible at https://lostuleskc.com
- [ ] SSL certificate valid
- [ ] All website features working
- [ ] No errors in browser console

---

## Summary

Phase 3 is ready to deploy. The Los Tules website will be deployed with custom domain support at https://lostuleskc.com. All infrastructure is configured and tested. The deployment is automated via the CI/CD pipeline.

**Next Action:** Trigger the pipeline deployment and monitor the process.
