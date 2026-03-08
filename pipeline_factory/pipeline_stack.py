"""WebsitePipelineStack - Creates CI/CD pipeline for a website."""

from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_codestarnotifications as notifications,
)
from constructs import Construct
from typing import Optional


class WebsitePipelineStack(Stack):
    """
    CDK Stack for creating a CI/CD pipeline for a website.
    
    Creates:
    - CodePipeline V2 with GitHub source and CodeBuild deploy
    - CodeBuild project with Node.js 20 and Python 3.12
    - SNS topic for pipeline failure notifications
    - IAM roles with necessary permissions
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        site_name: str,
        github_owner: str,
        github_repo: str,
        connection_arn: str,
        domain_name: Optional[str] = None,
        hosted_zone_id: Optional[str] = None,
        hosted_zone_name: Optional[str] = None,
        menu_pdf_enabled: bool = False,
        menu_pdf_bucket_name: Optional[str] = None,
        menu_pdf_filename: Optional[str] = None,
        notification_email: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize WebsitePipelineStack.
        
        Args:
            site_name: Unique identifier for the website
            github_owner: GitHub organization or username
            github_repo: GitHub repository name
            connection_arn: AWS CodeStar Connection ARN for GitHub
            domain_name: Custom domain (optional, empty string for none)
            hosted_zone_id: Route 53 hosted zone ID (optional)
            hosted_zone_name: Route 53 hosted zone name (optional)
            menu_pdf_enabled: Whether to create menu PDF bucket (optional)
            menu_pdf_bucket_name: Custom menu bucket name (optional)
            menu_pdf_filename: Menu PDF filename (optional)
            notification_email: Email for pipeline failure notifications (optional)
        """
        super().__init__(scope, construct_id, **kwargs)

        self._site_name = site_name
        self._github_owner = github_owner
        self._github_repo = github_repo
        self._connection_arn = connection_arn
        self._domain_name = domain_name or ""
        self._hosted_zone_id = hosted_zone_id or ""
        self._hosted_zone_name = hosted_zone_name or ""
        self._menu_pdf_enabled = menu_pdf_enabled
        self._menu_pdf_bucket_name = menu_pdf_bucket_name or ""
        self._menu_pdf_filename = menu_pdf_filename or ""
        self._notification_email = notification_email

        # Create resources
        self._notification_topic = self._create_notification_topic()
        self._codebuild_project = self._create_codebuild_project()
        self._pipeline = self._create_pipeline()
        
        # Create notification rule
        if notification_email:
            self._create_notification_rule()

    @property
    def pipeline(self) -> codepipeline.Pipeline:
        """The CodePipeline pipeline."""
        return self._pipeline

    @property
    def codebuild_project(self) -> codebuild.Project:
        """The CodeBuild project."""
        return self._codebuild_project

    @property
    def notification_topic(self) -> sns.Topic:
        """The SNS notification topic."""
        return self._notification_topic

    def _create_notification_topic(self) -> sns.Topic:
        """Create SNS topic for pipeline notifications."""
        topic = sns.Topic(
            self,
            "pipeline-notifications",
            display_name=f"Pipeline Notifications - {self._site_name}",
            topic_name=f"{self._site_name}-pipeline-notifications",
        )

        # Subscribe email if provided
        if self._notification_email:
            topic.add_subscription(
                subscriptions.EmailSubscription(self._notification_email)
            )

        # Add policy to allow CodeStar Notifications to publish
        topic.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AWSCodeStarNotifications",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("codestar-notifications.amazonaws.com")],
                actions=["SNS:Publish"],
                resources=[topic.topic_arn],
            )
        )

        return topic

    def _create_codebuild_project(self) -> codebuild.Project:
        """Create CodeBuild project for building and deploying the website."""
        # Create CodeBuild role with necessary permissions
        role = iam.Role(
            self,
            "codebuild-role",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="CodeBuild role for website deployment pipeline",
        )

        # Grant CloudFormation permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:*",
                ],
                resources=["*"],
            )
        )

        # Grant S3 permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:*",
                ],
                resources=["*"],
            )
        )

        # Grant CloudFront permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudfront:*",
                ],
                resources=["*"],
            )
        )

        # Grant Route53 permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "route53:*",
                ],
                resources=["*"],
            )
        )

        # Grant ACM permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "acm:*",
                ],
                resources=["*"],
            )
        )

        # Grant IAM permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "iam:PassRole",
                    "iam:CreateRole",
                    "iam:AttachRolePolicy",
                    "iam:PutRolePolicy",
                    "iam:DeleteRole",
                    "iam:DetachRolePolicy",
                    "iam:DeleteRolePolicy",
                    "iam:GetRole",
                    "iam:TagRole",
                    "iam:UntagRole",
                    "iam:GetRolePolicy",
                    "iam:CreatePolicy",
                    "iam:DeletePolicy",
                    "iam:GetPolicy",
                    "iam:GetPolicyVersion",
                    "iam:ListPolicyVersions",
                ],
                resources=["*"],
            )
        )

        # Grant Lambda permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "lambda:*",
                ],
                resources=["*"],
            )
        )

        # Grant SSM permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                ],
                resources=["*"],
            )
        )

        # Grant STS permissions for CDK bootstrap role assumption
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "sts:AssumeRole",
                ],
                resources=["arn:aws:iam::*:role/cdk-*"],
            )
        )

        # Use buildspec from repository (infra/buildspec.yml)
        # This allows each website to customize its build process
        buildspec = codebuild.BuildSpec.from_source_filename("infra/buildspec.yml")

        # Create CodeBuild project
        project = codebuild.Project(
            self,
            "build-project",
            project_name=f"{self._site_name}-build",
            description=f"Build and deploy {self._site_name}",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=False,
            ),
            environment_variables={
                "SITE_NAME": codebuild.BuildEnvironmentVariable(
                    value=self._site_name
                ),
                "DOMAIN_NAME": codebuild.BuildEnvironmentVariable(
                    value=self._domain_name or ""
                ),
                "HOSTED_ZONE_ID": codebuild.BuildEnvironmentVariable(
                    value=self._hosted_zone_id or ""
                ),
                "HOSTED_ZONE_NAME": codebuild.BuildEnvironmentVariable(
                    value=self._hosted_zone_name or ""
                ),
                "MENU_PDF_ENABLED": codebuild.BuildEnvironmentVariable(
                    value="true" if self._menu_pdf_enabled else "false"
                ),
                "MENU_PDF_BUCKET_NAME": codebuild.BuildEnvironmentVariable(
                    value=self._menu_pdf_bucket_name
                ),
                "MENU_PDF_FILENAME": codebuild.BuildEnvironmentVariable(
                    value=self._menu_pdf_filename
                ),
            },
            build_spec=buildspec,
            role=role,
        )

        return project

    def _create_pipeline(self) -> codepipeline.Pipeline:
        """Create CodePipeline V2 with GitHub source and CodeBuild deploy."""
        # Create source output artifact
        source_output = codepipeline.Artifact("SourceOutput")

        # Create source action
        source_action = cpactions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            owner=self._github_owner,
            repo=self._github_repo,
            branch="main",
            connection_arn=self._connection_arn,
            output=source_output,
            trigger_on_push=True,
        )

        # Create build action
        build_action = cpactions.CodeBuildAction(
            action_name="Build_and_Deploy",
            project=self._codebuild_project,
            input=source_output,
        )

        # Create pipeline with site name (no "website-pipeline-" prefix)
        pipeline = codepipeline.Pipeline(
            self,
            "pipeline",
            pipeline_name=self._site_name,
            pipeline_type=codepipeline.PipelineType.V2,
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action],
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action],
                ),
            ],
        )

        return pipeline

    def _create_notification_rule(self) -> notifications.CfnNotificationRule:
        """Create notification rule for pipeline failures."""
        return notifications.CfnNotificationRule(
            self,
            "notification-rule",
            name=f"{self._site_name}-pipeline-failures",
            detail_type="FULL",
            event_type_ids=[
                "codepipeline-pipeline-pipeline-execution-failed",
                "codepipeline-pipeline-pipeline-execution-canceled",
            ],
            resource=self._pipeline.pipeline_arn,
            targets=[
                notifications.CfnNotificationRule.TargetProperty(
                    target_type="SNS",
                    target_address=self._notification_topic.topic_arn,
                )
            ],
        )
