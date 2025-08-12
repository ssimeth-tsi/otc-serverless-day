# GitHub Actions Setup

## Required Secrets

Um die automatische Deployment-Pipeline zu nutzen, müssen folgende Secrets in GitHub konfiguriert werden:

### 1. Navigiere zu Repository Settings
- Gehe zu deinem Repository auf GitHub
- Klicke auf `Settings` → `Secrets and variables` → `Actions`

### 2. Füge folgende Secrets hinzu

Klicke auf `New repository secret` für jedes Secret:

| Secret Name | Beschreibung | Beispiel |
|-------------|--------------|----------|
| `OTC_DOMAIN_NAME` | OTC Domain Name | `OTC00000000001000xxxxxx` |
| `OTC_TENANT_NAME` | OTC Tenant Name | `eu-de` |
| `OTC_REGION` | OTC Region | `eu-de` |
| `OTC_ACCESS_KEY` | OTC Access Key (AK) | `XXXXXXXXXX` |
| `OTC_SECRET_KEY` | OTC Secret Key (SK) | `YYYYYYYYYY` |

### 3. Wo finde ich diese Werte?

#### Domain Name, Tenant Name, Region
- Login in die OTC Console
- Oben rechts auf deinen Username klicken
- "My Credentials" auswählen
- Unter "Projects" findest du die Informationen

#### Access Key und Secret Key
- In "My Credentials"
- Unter "Access Keys" → "Create Access Key"
- **WICHTIG**: Den Secret Key sofort sicher speichern, er wird nur einmal angezeigt!

## Workflow-Übersicht

### `deploy.yml`
- **Trigger**: Push auf `main` oder `master` Branch
- **Aktionen**:
  1. Baut die Dependencies für Linux mit Docker
  2. Erstellt das Deployment-Package (code.zip)
  3. Führt Terraform Plan aus
  4. Deployed die Function mit Terraform Apply
  5. Testet die API mit einem Health Check

### `pr-check.yml`
- **Trigger**: Pull Requests
- **Aktionen**:
  1. Validiert Python-Syntax
  2. Prüft Terraform-Formatierung
  3. Validiert Terraform-Konfiguration
  4. Testet den Build-Prozess (ohne Deploy)

## Manuelles Deployment

Du kannst das Deployment auch manuell triggern:
1. Gehe zu `Actions` Tab im Repository
2. Wähle "Deploy to OTC FunctionGraph"
3. Klicke auf "Run workflow"
4. Wähle den Branch und klicke "Run workflow"

## Lokales Testen

Bevor du pushst, teste lokal:

```bash
# Python Syntax prüfen
python -m py_compile src/index.py

# Terraform formatieren
cd terraform
terraform fmt -recursive

# Terraform validieren
terraform validate

# Dependencies packen
./packDependencies.sh

# ZIP erstellen
python3 createZip.py
```

## Troubleshooting

### Fehler: "Invalid credentials"
- Überprüfe die GitHub Secrets
- Stelle sicher, dass AK/SK korrekt sind und nicht abgelaufen

### Fehler: "code.zip too large"
- Prüfe die Dependencies in createZip.py
- Entferne unnötige Packages

### Fehler: "Terraform plan failed"
- Prüfe die Terraform-Konfiguration lokal
- Stelle sicher, dass alle Variablen gesetzt sind

## Monitoring

Nach einem erfolgreichen Deployment:
1. Prüfe den "Actions" Tab für Logs
2. Die API-URL wird im Workflow-Summary angezeigt
3. Teste die API mit:
   ```bash
   curl https://your-api-url/users
   ```