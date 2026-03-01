# Phase 3: Prerequisites - GoDaddy Nameserver Update Required

**Status:** ⏳ Waiting for Manual Action

---

## Current DNS Status

**Domain:** lostuleskc.com
**Current Nameservers:** GoDaddy (ns51.domaincontrol.com, ns52.domaincontrol.com)
**Required Nameservers:** AWS Route 53

```bash
$ dig lostuleskc.com NS +short
ns52.domaincontrol.com.
ns51.domaincontrol.com.
```

---

## What Needs to Be Done

The GoDaddy nameservers need to be updated to point to AWS Route 53. This is a **one-time manual step** that takes about 5 minutes.

### AWS Nameservers to Use

From the domain-management stack deployment:

```
ns-1071.awsdns-05.org
ns-1606.awsdns-08.co.uk
ns-420.awsdns-52.com
ns-670.awsdns-19.net
```

---

## Step-by-Step Instructions

### 1. Log in to GoDaddy

Go to https://www.godaddy.com and log in with your account credentials.

### 2. Navigate to Domain Settings

1. Click **"My Products"** (top right)
2. Find **"Domains"** section
3. Click on **"lostuleskc.com"**

### 3. Access Nameserver Settings

1. Click **"Manage DNS"** button
2. Look for **"Nameservers"** section
3. Click **"Change"** button next to nameservers

### 4. Update Nameservers

1. Select **"Custom"** option
2. Delete existing nameservers (if any)
3. Enter the 4 AWS nameservers:
   - `ns-1071.awsdns-05.org`
   - `ns-1606.awsdns-08.co.uk`
   - `ns-420.awsdns-52.com`
   - `ns-670.awsdns-19.net`
4. Click **"Save"**

### 5. Verify Update

GoDaddy will show a confirmation message. The update typically takes effect within 5-30 minutes.

---

## Verification

After updating nameservers, verify the change:

```bash
# Check nameservers (may take 5-30 minutes to propagate)
dig lostuleskc.com NS +short

# Should show AWS nameservers:
# ns-1071.awsdns-05.org
# ns-1606.awsdns-08.co.uk
# ns-420.awsdns-52.com
# ns-670.awsdns-19.net

# Check DNS resolution
dig lostuleskc.com +short

# Should eventually return CloudFront IP
```

---

## Alternative: Automated Update via GoDaddy Lambda

If you prefer automated updates for future domains, the domain-management stack includes a Lambda function that can automatically update GoDaddy nameservers.

**To enable for Los Tules:**

1. Ensure GoDaddy API credentials are stored in SSM:
   ```bash
   aws ssm put-parameter \
     --name /dtl-global/godaddy/api-key \
     --value '{"key":"YOUR_KEY","secret":"YOUR_SECRET"}' \
     --type SecureString \
     --overwrite
   ```

2. Update `website-infrastructure/domain-management/config/domains.json`:
   ```json
   {
     "domains": [
       {
         "name": "lostuleskc.com",
         "description": "Los Tules Mexican Restaurant",
         "autoUpdate": true
       }
     ]
   }
   ```

3. Redeploy domain-management stack:
   ```bash
   cd website-infrastructure/domain-management
   cdk deploy
   ```

The Lambda function will automatically update GoDaddy nameservers during deployment.

---

## Timeline

1. **Now:** Update GoDaddy nameservers (5 minutes)
2. **5-30 minutes:** DNS propagation
3. **After propagation:** Deploy Los Tules website with custom domain
4. **5-10 minutes:** Website deployment and ACM certificate creation
5. **Total:** ~30-50 minutes from now

---

## Next Steps

1. **Update GoDaddy nameservers** using the instructions above
2. **Wait for DNS propagation** (check with `dig lostuleskc.com NS +short`)
3. **Trigger pipeline deployment** when DNS is ready
4. **Monitor deployment** in AWS CodePipeline console
5. **Verify website** at https://lostuleskc.com

---

## Questions?

If you have questions about the nameserver update:

1. Check GoDaddy's help: https://www.godaddy.com/help/change-nameservers-for-your-domain-664
2. Review the domain-management README: `website-infrastructure/domain-management/README.md`
3. Check the deployment guide: `PHASE_3_DEPLOYMENT_GUIDE.md`

---

## Summary

**Action Required:** Update GoDaddy nameservers to AWS Route 53 nameservers

**Time Required:** 5 minutes + 5-30 minutes for DNS propagation

**After Completion:** Phase 3 deployment can proceed automatically via CI/CD pipeline
