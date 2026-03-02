#!/usr/bin/env python3
"""
Pipeline Factory - Creates CI/CD pipelines for multiple websites.

Reads config/websites.json and creates one CodePipeline stack per website.
"""
import os
import json
import aws_cdk as cdk
from pipeline_factory import WebsitePipelineStack


def load_config(config_path: str = "config/websites.json") -> dict:
    """Load website configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    """Create CDK app and pipeline stacks for all websites."""
    app = cdk.App()

    # Load configuration
    config = load_config()

    # Extract global config
    connection_arn = config["connectionArn"]
    github_owner = config["githubOwner"]
    default_region = config.get("defaultRegion", "us-east-1")
    default_account = config.get("defaultAccount", os.environ.get("CDK_DEFAULT_ACCOUNT"))
    notification_email = config.get("notificationEmail")

    # Create environment
    env = cdk.Environment(
        account=default_account,
        region=default_region,
    )

    # Create a pipeline stack for each website
    for website in config["websites"]:
        site_name = website["siteName"]
        github_repo = website["githubRepo"]
        domain_name = website.get("domainName", "")
        hosted_zone_id = website.get("hostedZoneId", "")
        hosted_zone_name = website.get("hostedZoneName", "")
        menu_pdf_enabled = website.get("menuPdfEnabled", False)
        menu_pdf_bucket_name = website.get("menuPdfBucketName", "")
        menu_pdf_filename = website.get("menuPdfFilename", "")

        # Create pipeline stack
        WebsitePipelineStack(
            app,
            f"{site_name}-pipeline",
            site_name=site_name,
            github_owner=github_owner,
            github_repo=github_repo,
            connection_arn=connection_arn,
            domain_name=domain_name,  # Pass as-is (empty string or value)
            hosted_zone_id=hosted_zone_id,  # Pass as-is (empty string or value)
            hosted_zone_name=hosted_zone_name,  # Pass as-is (empty string or value)
            menu_pdf_enabled=menu_pdf_enabled,
            menu_pdf_bucket_name=menu_pdf_bucket_name,
            menu_pdf_filename=menu_pdf_filename,
            notification_email=notification_email,
            env=env,
            description=f"CI/CD Pipeline for {site_name}",
        )

    app.synth()


if __name__ == "__main__":
    main()
