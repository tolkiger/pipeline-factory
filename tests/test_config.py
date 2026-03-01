"""Tests for configuration loading."""

import json
import tempfile
import os
import pytest


def test_config_schema():
    """Test that config/websites.json has the correct schema."""
    config_path = "config/websites.json"
    
    assert os.path.exists(config_path), "config/websites.json must exist"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Verify required top-level fields
    assert "connectionArn" in config
    assert "githubOwner" in config
    assert "defaultRegion" in config
    assert "defaultAccount" in config
    assert "notificationEmail" in config
    assert "websites" in config
    
    # Verify websites is a list
    assert isinstance(config["websites"], list)
    
    # Verify each website has required fields
    for website in config["websites"]:
        assert "siteName" in website
        assert "githubRepo" in website
        assert "domainName" in website
        assert "hostedZoneId" in website
        assert "hostedZoneName" in website


def test_config_values_are_strings():
    """Test that all config values are strings."""
    config_path = "config/websites.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Check top-level string fields
    assert isinstance(config["connectionArn"], str)
    assert isinstance(config["githubOwner"], str)
    assert isinstance(config["defaultRegion"], str)
    assert isinstance(config["defaultAccount"], str)
    assert isinstance(config["notificationEmail"], str)
    
    # Check website fields
    for website in config["websites"]:
        assert isinstance(website["siteName"], str)
        assert isinstance(website["githubRepo"], str)
        assert isinstance(website["domainName"], str)
        assert isinstance(website["hostedZoneId"], str)
        assert isinstance(website["hostedZoneName"], str)


def test_empty_domain_is_valid():
    """Test that empty string for domain fields is valid."""
    config_path = "config/websites.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Find a website with empty domain (should be los-tules-website)
    empty_domain_sites = [
        w for w in config["websites"]
        if w["domainName"] == ""
    ]
    
    assert len(empty_domain_sites) > 0, "Should have at least one site without domain"
    
    # Verify empty domain site also has empty zone fields
    for site in empty_domain_sites:
        assert site["hostedZoneId"] == ""
        assert site["hostedZoneName"] == ""
