#!/bin/bash
# Script to create a new website with CI/CD pipeline

set -e

# Check for required arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <site-name> <github-repo> [domain-name]"
    echo "Example: $0 my-restaurant-website my-restaurant-website myrestaurant.com"
    exit 1
fi

SITE_NAME="$1"
GITHUB_REPO="$2"
DOMAIN_NAME="${3:-}"  # Optional domain name

echo "Creating new website: $SITE_NAME"
echo "GitHub repository: $GITHUB_REPO"
echo "Domain name: ${DOMAIN_NAME:-'none (will use CloudFront default)'}"

# Read current configuration
CONFIG_FILE="config/websites.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file $CONFIG_FILE not found"
    exit 1
fi

# Check if website already exists in config
if grep -q "\"siteName\": \"$SITE_NAME\"" "$CONFIG_FILE"; then
    echo "Error: Website '$SITE_NAME' already exists in configuration"
    exit 1
fi

# Create the new website entry
NEW_ENTRY=$(cat <<EOF
    {
      "siteName": "$SITE_NAME",
      "githubRepo": "$GITHUB_REPO",
      "domainName": "$DOMAIN_NAME",
      "hostedZoneId": "",
      "hostedZoneName": "",
      "menuPdfEnabled": false,
      "menuPdfBucketName": "",
      "menuPdfFilename": ""
    }
EOF
)

# Add the new website to the configuration
# Remove the last closing bracket, add new entry, then add closing bracket back
sed -i '' '/  ]/d' "$CONFIG_FILE"
echo "  ]," >> "$CONFIG_FILE"
echo "$NEW_ENTRY" >> "$CONFIG_FILE"
echo "  ]" >> "$CONFIG_FILE"

echo "✅ Added $SITE_NAME to pipeline configuration"

# Create website template structure
echo "Creating website template structure..."
cat > "website-template.md" <<EOF
# Website Template for $SITE_NAME

## Repository Structure
Create a GitHub repository named "$GITHUB_REPO" with this structure:

\`\`\`
$GITHUB_REPO/
├── site/                    # Next.js website
│   ├── app/
│   │   └── page.js         # Home page
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── next.config.js      # Next.js configuration
├── infra/                   # CDK infrastructure
│   ├── app.py              # CDK application
│   ├── buildspec.yml       # CodeBuild configuration
│   ├── requirements.txt    # Python dependencies
│   ├── cdk.json           # CDK configuration
│   └── shared_website_constructs/  # Copy from los-tules-website
└── .gitignore
\`\`\`

## 1. Create the Next.js Site
\`\`\`bash
npx create-next-app@latest $GITHUB_REPO --typescript --tailwind --app
cd $GITHUB_REPO
\`\`\`

## 2. Set Up Infrastructure
Copy the \`infra/\` directory from the Los Tules website and update \`app.py\`:

\`\`\`python
#!/usr/bin/env python3
"""
CDK Entry Point -- Uses shared website construct
"""
import os
import aws_cdk as cdk
from shared_website_constructs import WebsiteStack

app = cdk.App()

# Read environment variables
site_name = os.environ.get("SITE_NAME", "$SITE_NAME")
domain_name = os.environ.get("DOMAIN_NAME", "$DOMAIN_NAME") or None
hosted_zone_id = os.environ.get("HOSTED_ZONE_ID", "") or None
hosted_zone_name = os.environ.get("HOSTED_ZONE_NAME", "") or None

# Build paths
infra_dir = os.path.dirname(os.path.abspath(__file__))
content_path = os.path.join(infra_dir, "..", "site", "out")

# Create the website stack
website_stack = WebsiteStack(
    app,
    "${SITE_NAME^}Stack",  # Capitalized site name
    site_name=site_name,
    domain_name=domain_name,
    hosted_zone_id=hosted_zone_id,
    hosted_zone_name=hosted_zone_name,
    content_path=content_path,
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    ),
    description="$SITE_NAME - Static Website on AWS",
)

app.synth()
\`\`\`

## 3. Deploy the Pipeline
After creating the repository and pushing code:

\`\`\`bash
# Deploy the pipeline for the new website
cd website-infrastructure/pipeline-factory
cdk deploy --all --require-approval never
\`\`\`

## 4. Add Domain (Optional)
If you have a domain name ($DOMAIN_NAME):

1. Update the domain in the configuration
2. Deploy the pipeline again
3. Update GoDaddy nameservers to point to AWS Route 53

## Next Steps
1. Create GitHub repository: $GITHUB_REPO
2. Copy the template structure
3. Customize the Next.js site
4. Push to GitHub
5. Deploy pipeline
6. Website will be available at: https://[cloudfront-id].cloudfront.net
EOF

echo "✅ Created website template in website-template.md"
echo ""
echo "Next steps:"
echo "1. Review the template in website-template.md"
echo "2. Create GitHub repository: $GITHUB_REPO"
echo "3. Set up the website structure"
echo "4. Deploy the pipeline: cd website-infrastructure/pipeline-factory && cdk deploy --all --require-approval never"
echo "5. Push code to GitHub to trigger the first deployment"