# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-08

### Added
- [#8](https://github.com/tolkiger/pipeline-factory/issues/8) - Add dtl_global website to CI/CD pipeline configuration

## [0.1.0] - 2026-02-28

### Added
- Initial implementation of Pipeline Factory
- WebsitePipelineStack for creating CI/CD pipelines
- Config-driven pipeline generation from `config/websites.json`
- CodePipeline V2 with GitHub source (CodeStar Connections)
- CodeBuild project with Node.js 20 and Python 3.12
- SNS topic for pipeline failure notifications
- Notification rules for pipeline failures and cancellations
- Comprehensive IAM permissions for CodeBuild
- Environment variable injection for website configuration
- Comprehensive unit tests (14 test cases, 100% coverage)
- README with setup and usage instructions
- Sample configuration file

### Features
- Automatic pipeline creation for multiple websites
- GitHub integration via CodeStar Connections
- Trigger on push to main branch
- Email notifications for pipeline failures
- Support for with-domain and without-domain websites
- Full AWS permissions for infrastructure deployment
