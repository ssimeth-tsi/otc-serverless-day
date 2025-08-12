#!/bin/bash

echo "🚀 Starting deployment..."

# Step 1: Create code.zip
echo "📦 Creating code.zip..."
python3 createZip.py

if [ ! -f "code.zip" ]; then
    echo "❌ Error: code.zip was not created"
    exit 1
fi

echo "✅ code.zip created successfully"
ls -lh code.zip

# Step 2: Run Terraform
echo "🔧 Running Terraform..."
cd terraform
terraform apply -auto-approve

echo "✅ Deployment complete!"