# Terraform State Management für GitHub Actions

## Problem
Terraform muss seinen State zwischen GitHub Actions Runs persistieren. Ohne Remote Backend würde jeder Run denken, es gibt keine existierenden Ressourcen.

## Lösung 1: OTC OBS Backend (Empfohlen für Produktion)

### 1. OBS Bucket erstellen

```bash
# Option A: Über OTC Console
# 1. Gehe zu Object Storage Service (OBS)
# 2. Create Bucket
# 3. Name: z.B. "terraform-state-serverless"
# 4. Region: eu-de
# 5. Storage Class: Standard

# Option B: Mit Terraform (einmalig lokal)
```

```hcl
# setup/create-backend.tf
resource "opentelekomcloud_obs_bucket" "terraform_state" {
  bucket = "terraform-state-serverless-${var.project_name}"
  acl    = "private"
  region = "eu-de"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    name    = "delete-old-versions"
    enabled = true
    
    noncurrent_version_expiration {
      days = 30
    }
  }
}
```

### 2. Backend konfigurieren

Die `backend.tf` ist bereits erstellt. Passe nur den Bucket-Namen an:

```hcl
terraform {
  backend "s3" {
    endpoints = {
      s3 = "https://obs.eu-de.otc.t-systems.com"
    }
    bucket = "DEIN-BUCKET-NAME"  # <-- Hier anpassen
    key    = "serverlessday/terraform.tfstate"
    region = "eu-de"
    # ...
  }
}
```

### 3. State migrieren (wenn schon lokal vorhanden)

```bash
# Backup erstellen
cp terraform.tfstate terraform.tfstate.backup.local

# Backend initialisieren (wird nach Migration fragen)
terraform init -migrate-state

# Antwort "yes" bei der Frage zur Migration
```

### 4. GitHub Actions funktioniert automatisch

Die Pipeline ist bereits konfiguriert für OBS Backend!

## Lösung 2: Terraform Cloud (Alternative)

### Vorteile:
- Kostenlos für kleine Teams
- State Locking
- UI für State-Verwaltung
- Runs History

### Setup:
1. Account bei app.terraform.io erstellen
2. Workspace erstellen
3. In `terraform/main.tf`:

```hcl
terraform {
  cloud {
    organization = "your-org"
    
    workspaces {
      name = "serverless-day"
    }
  }
}
```

4. Token in GitHub Secrets: `TF_API_TOKEN`

## Lösung 3: GitHub Artifacts (Nur für Dev/Test!)

⚠️ **WARNUNG**: Nicht für Produktion!
- Kein State Locking
- Kann zu Konflikten führen
- Artifacts laufen nach 30-90 Tagen ab

Nutze `deploy-with-artifact-state.yml` Workflow.

## State Locking

### Problem:
Mehrere Personen/Runs könnten gleichzeitig deployen.

### Lösung für OBS:
Nutze DynamoDB-kompatible Table für Locking:

```hcl
backend "s3" {
  # ... andere Config ...
  
  # State Locking mit DCS (Distributed Cache Service)
  dynamodb_table = "terraform-state-lock"
  
  # Oder ohne Locking (Vorsicht!)
  force_path_style = true
}
```

## Best Practices

### 1. State Backup
- OBS Versioning aktivieren ✅
- Regelmäßige Backups
- Alte Versionen automatisch löschen

### 2. Secrets Management
- Niemals Credentials im Code
- Nutze GitHub Secrets
- Rotiere Keys regelmäßig

### 3. State Isolation
- Ein State pro Environment (dev/staging/prod)
- Verschiedene Buckets oder Prefixes:
  ```
  terraform-state-dev/serverlessday/terraform.tfstate
  terraform-state-prod/serverlessday/terraform.tfstate
  ```

### 4. Disaster Recovery
```bash
# State wiederherstellen aus OBS
terraform init -reconfigure
terraform refresh

# Oder manuell
aws s3 cp s3://bucket/key terraform.tfstate --endpoint-url=https://obs.eu-de.otc.t-systems.com
```

## Troubleshooting

### "Error acquiring the state lock"
- Jemand anderes deployed gerade
- Oder: Vorheriger Run wurde abgebrochen
- Lösung: `terraform force-unlock <LOCK_ID>`

### "No such bucket"
- Bucket muss manuell erstellt werden
- Prüfe Bucket-Name und Region

### "Access Denied"
- Prüfe AK/SK in GitHub Secrets
- Prüfe OBS Bucket Permissions

## Lokale Entwicklung mit Remote State

```bash
# Environment Variables setzen
export AWS_ACCESS_KEY_ID=your-ak
export AWS_SECRET_ACCESS_KEY=your-sk

# Init mit Backend
terraform init

# Jetzt nutzt du denselben State wie GitHub Actions!
terraform plan
```

## State Inspektion

```bash
# State anzeigen
terraform show

# Spezifische Resource
terraform state show opentelekomcloud_fgs_function_v2.fastapi_function

# State Liste
terraform state list

# State von OBS herunterladen (Backup)
aws s3 cp s3://your-bucket/serverlessday/terraform.tfstate ./backup.tfstate \
  --endpoint-url=https://obs.eu-de.otc.t-systems.com
```