"""Lambda function to update GoDaddy nameservers via API."""

import json
import boto3
import requests
import os
from typing import Any, Dict

ssm = boto3.client("ssm")


def get_godaddy_credentials() -> tuple[str, str]:
    """Retrieve GoDaddy API credentials from SSM Parameter Store."""
    try:
        response = ssm.get_parameter(
            Name="/dtl-global/godaddy/api-key",
            WithDecryption=True
        )
        credentials = json.loads(response["Parameter"]["Value"])
        return credentials["key"], credentials["secret"]
    except Exception as e:
        print(f"Error retrieving GoDaddy credentials: {e}")
        raise


def update_godaddy_nameservers(
    domain: str,
    nameservers: list[str],
    api_key: str,
    api_secret: str
) -> bool:
    """Update nameservers for a domain in GoDaddy."""
    
    url = f"https://api.godaddy.com/v1/domains/{domain}/records/NS"
    
    headers = {
        "Authorization": f"sso-key {api_key}:{api_secret}",
        "Content-Type": "application/json",
    }
    
    # Build NS records
    ns_records = [
        {
            "data": ns,
            "name": "@",
            "ttl": 3600,
            "type": "NS"
        }
        for ns in nameservers
    ]
    
    try:
        response = requests.patch(url, json=ns_records, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Successfully updated nameservers for {domain}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error updating GoDaddy nameservers for {domain}: {e}")
        return False


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Lambda invocation from CDK Custom Resource."""
    
    print(f"Event: {json.dumps(event)}")
    
    # Parse payload
    payload = json.loads(event.get("Payload", "{}"))
    domain = payload.get("Domain")
    nameservers = payload.get("Nameservers", [])
    
    if not domain or not nameservers:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Missing Domain or Nameservers"
            }),
        }
    
    try:
        api_key, api_secret = get_godaddy_credentials()
        
        # Update nameservers
        success = update_godaddy_nameservers(domain, nameservers, api_key, api_secret)
        
        if success:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"Successfully updated nameservers for {domain}",
                    "domain": domain,
                    "nameservers": nameservers,
                }),
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "Failed to update GoDaddy nameservers"
                }),
            }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            }),
        }
