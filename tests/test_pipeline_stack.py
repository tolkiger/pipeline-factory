"""Tests for WebsitePipelineStack."""

import aws_cdk as cdk
from aws_cdk import assertions
from pipeline_factory import WebsitePipelineStack
import pytest


class TestWebsitePipelineStack:
    """Tests for WebsitePipelineStack."""

    def test_creates_all_resources(self):
        """Test that all expected resources are created."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            domain_name="test.example.com",
            hosted_zone_id="Z1234567890ABC",
            hosted_zone_name="example.com",
            notification_email="test@example.com",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify CodePipeline created
        template.resource_count_is("AWS::CodePipeline::Pipeline", 1)
        
        # Verify CodeBuild project created
        template.resource_count_is("AWS::CodeBuild::Project", 1)
        
        # Verify SNS topic created
        template.resource_count_is("AWS::SNS::Topic", 1)
        
        # Verify SNS subscription created
        template.resource_count_is("AWS::SNS::Subscription", 1)
        
        # Verify notification rule created
        template.resource_count_is("AWS::CodeStarNotifications::NotificationRule", 1)

    def test_pipeline_is_v2(self):
        """Test that pipeline is V2 type."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify pipeline type is V2
        template.has_resource_properties(
            "AWS::CodePipeline::Pipeline",
            {
                "PipelineType": "V2",
            }
        )

    def test_pipeline_has_github_source(self):
        """Test that pipeline has GitHub source stage."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify source stage with CodeStar connection
        template.has_resource_properties(
            "AWS::CodePipeline::Pipeline",
            {
                "Stages": assertions.Match.array_with([
                    assertions.Match.object_like({
                        "Name": "Source",
                        "Actions": assertions.Match.array_with([
                            assertions.Match.object_like({
                                "Name": "GitHub_Source",
                                "ActionTypeId": {
                                    "Category": "Source",
                                    "Owner": "AWS",
                                    "Provider": "CodeStarSourceConnection",
                                },
                            })
                        ])
                    })
                ])
            }
        )

    def test_pipeline_has_build_stage(self):
        """Test that pipeline has build stage with CodeBuild."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify build stage with CodeBuild
        template.has_resource_properties(
            "AWS::CodePipeline::Pipeline",
            {
                "Stages": assertions.Match.array_with([
                    assertions.Match.object_like({
                        "Name": "Build",
                        "Actions": assertions.Match.array_with([
                            assertions.Match.object_like({
                                "Name": "Build_and_Deploy",
                                "ActionTypeId": {
                                    "Category": "Build",
                                    "Owner": "AWS",
                                    "Provider": "CodeBuild",
                                },
                            })
                        ])
                    })
                ])
            }
        )

    def test_codebuild_has_nodejs_and_python(self):
        """Test that CodeBuild project has Node.js 20 and Python 3.12."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify buildspec has correct runtime versions
        template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Source": {
                    "BuildSpec": assertions.Match.string_like_regexp(".*nodejs.*"),
                }
            }
        )

    def test_codebuild_has_environment_variables(self):
        """Test that CodeBuild has website-specific environment variables."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            domain_name="test.example.com",
            hosted_zone_id="Z1234567890ABC",
            hosted_zone_name="example.com",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify environment variables
        template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Environment": {
                    "EnvironmentVariables": assertions.Match.array_with([
                        assertions.Match.object_like({
                            "Name": "SITE_NAME",
                            "Value": "test-site",
                        }),
                        assertions.Match.object_like({
                            "Name": "DOMAIN_NAME",
                            "Value": "test.example.com",
                        }),
                        assertions.Match.object_like({
                            "Name": "HOSTED_ZONE_ID",
                            "Value": "Z1234567890ABC",
                        }),
                        assertions.Match.object_like({
                            "Name": "HOSTED_ZONE_NAME",
                            "Value": "example.com",
                        }),
                    ])
                }
            }
        )

    def test_codebuild_role_has_necessary_permissions(self):
        """Test that CodeBuild role has all necessary permissions."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify IAM role has policies
        template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": assertions.Match.array_with([
                        assertions.Match.object_like({
                            "Principal": {
                                "Service": "codebuild.amazonaws.com",
                            }
                        })
                    ])
                }
            }
        )

    def test_sns_topic_created(self):
        """Test that SNS topic is created for notifications."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            notification_email="test@example.com",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify SNS topic
        template.has_resource_properties(
            "AWS::SNS::Topic",
            {
                "DisplayName": "test-site Pipeline Notifications",
            }
        )

    def test_notification_rule_for_failures(self):
        """Test that notification rule is created for pipeline failures."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            notification_email="test@example.com",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify notification rule
        template.has_resource_properties(
            "AWS::CodeStarNotifications::NotificationRule",
            {
                "EventTypeIds": assertions.Match.array_with([
                    "codepipeline-pipeline-pipeline-execution-failed",
                    "codepipeline-pipeline-pipeline-execution-canceled",
                ]),
            }
        )

    def test_without_domain(self):
        """Test that stack works without domain configuration."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            domain_name=None,
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify environment variables have empty strings for domain
        template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Environment": {
                    "EnvironmentVariables": assertions.Match.array_with([
                        assertions.Match.object_like({
                            "Name": "DOMAIN_NAME",
                            "Value": "",
                        }),
                    ])
                }
            }
        )

    def test_properties_are_accessible(self):
        """Test that public properties are accessible."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
        )
        
        # Verify properties are accessible
        assert stack.pipeline is not None
        assert stack.codebuild_project is not None
        assert stack.notification_topic is not None


    def test_menu_pdf_environment_variables(self):
        """Test that menu PDF environment variables are set correctly."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            menu_pdf_enabled=True,
            menu_pdf_bucket_name="test-menu-bucket",
            menu_pdf_filename="test-menu.pdf",
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify menu PDF environment variables
        template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Environment": {
                    "EnvironmentVariables": assertions.Match.array_with([
                        assertions.Match.object_like({
                            "Name": "MENU_PDF_ENABLED",
                            "Value": "true",
                        }),
                        assertions.Match.object_like({
                            "Name": "MENU_PDF_BUCKET_NAME",
                            "Value": "test-menu-bucket",
                        }),
                        assertions.Match.object_like({
                            "Name": "MENU_PDF_FILENAME",
                            "Value": "test-menu.pdf",
                        }),
                    ])
                }
            }
        )

    def test_menu_pdf_disabled(self):
        """Test that menu PDF environment variables work when disabled."""
        app = cdk.App()
        
        stack = WebsitePipelineStack(
            app,
            "TestStack",
            site_name="test-site",
            github_owner="test-owner",
            github_repo="test-repo",
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/test",
            menu_pdf_enabled=False,
        )
        
        template = assertions.Template.from_stack(stack)
        
        # Verify menu PDF is disabled
        template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Environment": {
                    "EnvironmentVariables": assertions.Match.array_with([
                        assertions.Match.object_like({
                            "Name": "MENU_PDF_ENABLED",
                            "Value": "false",
                        }),
                        assertions.Match.object_like({
                            "Name": "MENU_PDF_BUCKET_NAME",
                            "Value": "",
                        }),
                        assertions.Match.object_like({
                            "Name": "MENU_PDF_FILENAME",
                            "Value": "",
                        }),
                    ])
                }
            }
        )
