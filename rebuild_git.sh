#!/bin/bash
set -e

BACKUP="/Users/skarthik/Downloads/TrekkingManagementApplication_23f2000278_backup"
REPO="/Users/skarthik/Downloads/TrekkingManagementApplication_23f2000278"

# Clean current directory (except rebuilding script)
find . -mindepth 1 -maxdepth 1 -not -name 'rebuild_git.sh' -exec rm -rf {} +

# Initialize empty Git repository
git init
git branch -m main

# Configure local git user
git config user.name "S Karthik"
git config user.email "skarthik@example.com"

# STEP 1: Setup project structure and configuration
cp "$BACKUP/.gitignore" .
cp "$BACKUP/requirements.txt" .
cp "$BACKUP/config.py" .
cp "$BACKUP/extensions.py" .
cp "$BACKUP/models.py" .
cp "$BACKUP/seed.py" .

git add .
git commit -m "feat: configure database models and schema structure"

# STEP 2: Authentication and Layout
git checkout -b feat/auth
cp "$BACKUP/app.py" .
mkdir -p routes templates/auth static/css
cp "$BACKUP/routes/__init__.py" routes/
cp "$BACKUP/routes/auth_routes.py" routes/
cp "$BACKUP/routes/decorators.py" routes/
cp "$BACKUP/templates/base.html" templates/
cp "$BACKUP/templates/auth/login.html" templates/auth/
cp "$BACKUP/templates/auth/register.html" templates/auth/
cp "$BACKUP/static/css/custom.css" static/css/

git add .
git commit -m "feat: implement user authentication and registration system"
git checkout main
git merge feat/auth --no-ff --no-edit

# STEP 3: Admin Dashboard
git checkout -b feat/admin
mkdir -p templates/admin static/img/treks
cp "$BACKUP/routes/admin_routes.py" routes/
cp -r "$BACKUP/templates/admin/." templates/admin/
cp -r "$BACKUP/static/img/treks/." static/img/treks/

git add .
git commit -m "feat: add admin dashboard with staff and user management"
git checkout main
git merge feat/admin --no-ff --no-edit

# STEP 4: Staff Portal
git checkout -b feat/staff
mkdir -p templates/staff
cp "$BACKUP/routes/staff_routes.py" routes/
cp -r "$BACKUP/templates/staff/." templates/staff/

git add .
git commit -m "feat: implement trek staff portal and schedules"
git checkout main
git merge feat/staff --no-ff --no-edit

# STEP 5: Trekker (User) Portal
git checkout -b feat/user
mkdir -p templates/user
cp "$BACKUP/routes/user_routes.py" routes/
cp -r "$BACKUP/templates/user/." templates/user/

git add .
git commit -m "feat: implement user booking flow and trek browser"
git checkout main
git merge feat/user --no-ff --no-edit

# STEP 6: APIs, Tests & Documentation
git checkout -b feat/api
cp "$BACKUP/routes/api_routes.py" routes/
cp "$BACKUP/test_app.py" .
cp "$BACKUP/README.md" .

git add .
git commit -m "feat: add REST API endpoints and automated test suite"
git checkout main
git merge feat/api --no-ff --no-edit

# Bring all branches up to date with full code by merging main back into them
echo "Merging main back into all feature branches..."
git checkout feat/auth && git merge main --no-edit
git checkout feat/admin && git merge main --no-edit
git checkout feat/staff && git merge main --no-edit
git checkout feat/user && git merge main --no-edit
git checkout feat/api && git merge main --no-edit

# Return to main branch
git checkout main

# Re-link remote origin
git remote add origin https://github.com/SKarthik12321/Trekking-Management-Application-23f2000278

echo "Git history rebuilt successfully!"
