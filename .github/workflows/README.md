# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated deployment of the documentation site.

## Workflows

### Preview Deployment (`preview.yml`)

- **Trigger**: Pull requests to `main` branch
- **Purpose**: Creates a preview deployment for each PR
- **Deployment**: Firebase Hosting preview channel (unique URL per PR)
- **Features**:
  - Automatically comments on PRs with preview URL
  - Only runs when relevant files change (content, assets, configs)
  - Uses PR number as channel ID: `pr-{PR_NUMBER}`

### Production Deployment (`deploy.yml`)

- **Trigger**: Pushes to `main` branch
- **Purpose**: Deploys the site to production
- **Deployment**: Firebase Hosting production site
- **Features**:
  - Only runs when relevant files change
  - Deploys to the live site

## Setup Instructions

### 1. Firebase Service Account

You need to create a Firebase service account and add it as a GitHub secret:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Download the JSON file
6. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
7. Add a new secret named `FIREBASE_SERVICE_ACCOUNT` with the entire contents of the JSON file

### 2. Firebase Project ID

1. In Firebase Console, go to **Project Settings** → **General**
2. Copy the **Project ID**
3. In GitHub repository, add a new secret named `FIREBASE_PROJECT_ID` with the project ID value

### 3. Verify Setup

After adding the secrets:
- Create a test PR to trigger the preview workflow
- Merge to main to trigger the production workflow

## Workflow Details

Both workflows:
- Use Hugo Extended v0.135.0
- Use Node.js 18
- Install npm dependencies
- Build the site with `hugo --gc --minify`
- Deploy to Firebase Hosting

The preview workflow automatically comments on PRs with a link to the preview deployment.
