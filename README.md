# OTC Serverless FastAPI

Serverless FastAPI application deployed on Open Telekom Cloud (OTC) FunctionGraph.

## Architecture

```
API Gateway → FunctionGraph → FastAPI → SQLite
     ↓              ↓
   HTTPS       Python 3.9
```

- **API Gateway**: Public HTTPS endpoints
- **FunctionGraph**: Serverless compute (256MB, 30s timeout)
- **FastAPI**: REST API with `/` and `/users` endpoints
- **SQLite**: Embedded database in `/tmp`

## Deployment

### Production (main branch)
Push to `main` triggers automatic deployment via GitHub Actions.

### PR Preview Environments
Each PR gets an isolated preview environment:

1. **Automatic Deployment**: PR opened → Preview deployed with suffix `-pr-<number>`
2. **Performance Testing**: 100 requests against each endpoint
3. **Results Comment**: Performance metrics posted to PR
4. **Auto-Cleanup**: PR closed → Environment destroyed

## Setup

### Prerequisites
- OTC Account with FunctionGraph & API Gateway
- OBS Bucket 
- GitHub Secrets:
  - `OTC_ACCESS_KEY`
  - `OTC_SECRET_KEY`
  - `OTC_DOMAIN_NAME`
  - `OTC_TENANT_NAME`
  - `OTC_REGION`
  - `OTC_BUCKET`


### Creating a PR for Testing
```bash
# Create feature branch
git checkout -b my-feature

# Make changes
# ... edit files ...

# Commit and push
git add .
git commit -m "feat: my new feature"
git push -u origin my-feature

# Create PR via GitHub CLI
gh pr create --title "My Feature" --body "Description"

# Or create PR via GitHub web interface
# Visit: https://github.com/your-repo/compare
```

### Local Development
```bash
 terraform init \
          -backend-config="endpoint=https://obs.$OTC_REGION.otc.t-systems.com" \
          -backend-config="bucket=$OTC_BUCKET" \
          -backend-config="region=$OTC_REGION" \
          -backend-config="access_key=$OTC_ACCESS_KEY" \
          -backend-config="secret_key=$OTC_SECRET_KEY" \
          -backend-config="key=terraform-state/otc-serverless" \
          -backend-config="skip_credentials_validation=true" \
          -backend-config="skip_region_validation=true" \
          -backend-config="skip_metadata_api_check=true"

./deploy.sh
```
