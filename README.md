# Pipeline Factory

Multi-website CI/CD pipeline generator using AWS CodePipeline, CodeBuild, and CodeStar Connections.

## Overview

The Pipeline Factory reads a configuration file (`config/websites.json`) and automatically creates AWS CodePipeline V2 pipelines for each website. Each pipeline:

- Monitors a GitHub repository for changes
- Builds the Next.js website
- Deploys infrastructure using AWS CDK
- Sends notifications on failures

## Features

- **Config-Driven**: Define all websites in a single JSON file
- **AWS-Native CI/CD**: Uses CodePipeline V2, CodeBuild, CodeStar Connections
- **Automatic Deployments**: Triggers on push to main branch
- **Failure Notifications**: SNS topics with email subscriptions
- **Multi-Runtime Support**: Node.js 20 and Python 3.12
- **Comprehensive Permissions**: CodeBuild has all necessary AWS permissions

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or with dev dependencies
pip install -r requirements-dev.txt
```

## Configuration

### 1. Create CodeStar Connection

First, create a CodeStar Connection to GitHub:

```bash
aws codestar-connections create-connection \
  --provider-type GitHub \
  --connection-name "github-connection"
```

Then go to AWS Console > CodePipeline > Settings > Connections > click "Update pending connection" to authorize GitHub access. Save the Connection ARN.

### 2. Configure Websites

Edit `config/websites.json`:

```json
{
  "connectionArn": "arn:aws:codestar-connections:us-east-1:ACCOUNT:connection/ID",
  "githubOwner": "your-github-org",
  "defaultRegion": "us-east-1",
  "defaultAccount": "123456789012",
  "notificationEmail": "alerts@example.com",
  "websites": [
    {
      "siteName": "my-website",
      "githubRepo": "my-website",
      "domainName": "www.example.com",
      "hostedZoneId": "Z1234567890ABC",
      "hostedZoneName": "example.com"
    },
    {
      "siteName": "another-website",
      "githubRepo": "another-website",
      "domainName": "",
      "hostedZoneId": "",
      "hostedZoneName": ""
    }
  ]
}
```

**Configuration Fields:**

- `connectionArn`: AWS CodeStar Connection ARN for GitHub
- `githubOwner`: GitHub organization or username
- `defaultRegion`: AWS region for pipelines (default: us-east-1)
- `defaultAccount`: AWS account ID
- `notificationEmail`: Email for pipeline failure notifications

**Website Fields:**

- `siteName`: Unique identifier for the website
- `githubRepo`: GitHub repository name
- `domainName`: Custom domain (empty string for no domain)
- `hostedZoneId`: Route 53 hosted zone ID (empty string if no domain)
- `hostedZoneName`: Route 53 hosted zone name (empty string if no domain)

## Usage

### Deploy All Pipelines

```bash
# Bootstrap CDK (first time only)
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1

# Deploy all pipeline stacks
cdk deploy --all --require-approval never
```

### Deploy Specific Pipeline

```bash
cdk deploy my-website-pipeline
```

### List All Stacks

```bash
cdk list
```

## Pipeline Architecture

Each website gets its own pipeline stack:

```
┌─────────────────┐
│  GitHub Repo    │
└────────┬────────┘
         │ Push to main
         ▼
┌─────────────────────────┐
│  CodePipeline V2        │
│  ┌─────────────────┐    │
│  │ Source Stage    │    │
│  │ (CodeStar)      │    │
│  └────────┬────────┘    │
│           │             │
│  ┌────────▼────────┐    │
│  │ Build Stage     │    │
│  │ (CodeBuild)     │    │
│  └─────────────────┘    │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  CodeBuild Project      │
│  1. npm ci && npm build │
│  2. pip install         │
│  3. cdk deploy          │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  Website Deployed       │
│  (CloudFront + S3)      │
└─────────────────────────┘
```

## CodeBuild Process

Each pipeline's CodeBuild project:

1. **Install Phase**: Sets up Node.js 20 and Python 3.12
2. **Pre-Build Phase**: Installs Node.js dependencies (`npm ci`)
3. **Build Phase**:
   - Builds Next.js site (`npm run build`)
   - Installs Python dependencies
   - Deploys with CDK (`cdk deploy --all --require-approval never`)

## Environment Variables

CodeBuild receives these environment variables:

- `SITE_NAME`: Website identifier
- `DOMAIN_NAME`: Custom domain (empty string if none)
- `HOSTED_ZONE_ID`: Route 53 zone ID (empty string if none)
- `HOSTED_ZONE_NAME`: Route 53 zone name (empty string if none)

## IAM Permissions

CodeBuild role has permissions for:

- CloudFormation (full access)
- S3 (full access)
- CloudFront (full access)
- Route 53 (full access)
- ACM (full access)
- IAM (role management)
- Lambda (full access)
- SSM (parameter access)
- STS (CDK bootstrap role assumption)

## Notifications

Each pipeline has:

- **SNS Topic**: For failure notifications
- **Email Subscription**: Configured via `notificationEmail`
- **Notification Rule**: Triggers on pipeline failures and cancellations

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pipeline_factory --cov-report=html

# Run specific test file
pytest tests/test_pipeline_stack.py -v
```

### Test Coverage

The test suite includes:

- ✅ Pipeline V2 creation
- ✅ GitHub source stage (CodeStar)
- ✅ CodeBuild stage
- ✅ Node.js 20 and Python 3.12 runtime
- ✅ Environment variables
- ✅ IAM permissions
- ✅ SNS notifications
- ✅ Notification rules
- ✅ With/without domain scenarios
- ✅ Config schema validation

## Adding a New Website

1. Add entry to `config/websites.json`:
   ```json
   {
     "siteName": "new-website",
     "githubRepo": "new-website",
     "domainName": "new.example.com",
     "hostedZoneId": "Z1234567890ABC",
     "hostedZoneName": "example.com"
   }
   ```

2. Deploy the new pipeline:
   ```bash
   cdk deploy new-website-pipeline
   ```

3. Push code to the GitHub repository. The pipeline auto-triggers!

## Troubleshooting

### Pipeline Fails to Start

- Verify CodeStar Connection is in "Available" status
- Check GitHub repository exists and is accessible
- Verify connection ARN is correct

### Build Fails

- Check CodeBuild logs in AWS Console
- Verify `site/` directory has `package.json` and Next.js setup
- Verify `infra/` directory has `requirements.txt` and CDK app
- Check environment variables are set correctly

### Deployment Fails

- Verify CDK is bootstrapped in the account/region
- Check CodeBuild role has necessary permissions
- Review CloudFormation stack events for errors

## Requirements

- Python >= 3.12
- AWS CDK >= 2.0.0
- AWS Account with CDK bootstrapped
- GitHub repository with CodeStar Connection

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
