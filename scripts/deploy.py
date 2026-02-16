#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Coolify Deployment Script for Meta Agent

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : deploy.py
@Mission : Deploy Meta Agent to Coolify cloud self-hosted platform
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Optional
import requests

# Configuration
COOLIFY_API_URL = os.environ.get("COOLIFY_API_URL", "https://coolify.example.com/api/v1")
COOLIFY_API_TOKEN = os.environ.get("COOLIFY_API_TOKEN", "")
COOLIFY_CLOUD_TOKEN = os.environ.get("COOLIFY_CLOUD_TOKEN", "")

# Application settings
APP_NAME = "meta-agent"
APP_DESCRIPTION = "Meta Agent - Chief Orchestrator of Archon X"
SERVER_PORT = 8000
FRONTEND_PORT = 3000


class CoolifyDeployer:
    """
    Deploy Meta Agent to Coolify.
    
    Uses the Coolify API to:
    1. Create application
    2. Configure environment
    3. Deploy from Git
    4. Set up SSL
    """
    
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
    
    def check_connection(self) -> bool:
        """Check if we can connect to Coolify."""
        try:
            response = requests.get(
                f"{self.api_url}/version",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def list_servers(self) -> list:
        """List available servers."""
        response = requests.get(
            f"{self.api_url}/servers",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    
    def list_projects(self) -> list:
        """List available projects."""
        response = requests.get(
            f"{self.api_url}/projects",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    
    def create_project(self, name: str, description: str = "") -> Optional[str]:
        """Create a new project."""
        data = {
            "name": name,
            "description": description or f"Project for {name}",
        }
        
        response = requests.post(
            f"{self.api_url}/projects",
            headers=self.headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            project = response.json()
            return project.get("data", {}).get("uuid")
        
        print(f"❌ Failed to create project: {response.text}")
        return None
    
    def create_application(
        self,
        project_uuid: str,
        server_uuid: str,
        git_repository: str,
        git_branch: str = "main",
        domain: str = "",
        environment_variables: dict = None,
    ) -> Optional[str]:
        """Create a new application."""
        data = {
            "project_uuid": project_uuid,
            "server_uuid": server_uuid,
            "git_repository": git_repository,
            "git_branch": git_branch,
            "domains": domain,
            "build_pack": "dockerfile",
            "dockerfile_location": "/Dockerfile.meta",
            "ports_exposes": f"{SERVER_PORT},{FRONTEND_PORT}",
            "environment_variables": environment_variables or {},
        }
        
        response = requests.post(
            f"{self.api_url}/applications",
            headers=self.headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            app = response.json()
            return app.get("data", {}).get("uuid")
        
        print(f"❌ Failed to create application: {response.text}")
        return None
    
    def deploy_application(self, app_uuid: str) -> bool:
        """Deploy an application."""
        response = requests.post(
            f"{self.api_url}/applications/{app_uuid}/start",
            headers=self.headers
        )
        
        if response.status_code == 200:
            print(f"✅ Deployment started for {app_uuid}")
            return True
        
        print(f"❌ Failed to deploy: {response.text}")
        return False
    
    def get_application_status(self, app_uuid: str) -> dict:
        """Get application status."""
        response = requests.get(
            f"{self.api_url}/applications/{app_uuid}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json().get("data", {})
        return {}
    
    def set_environment_variables(self, app_uuid: str, variables: dict) -> bool:
        """Set environment variables for an application."""
        env_list = [
            {"key": k, "value": v, "is_preview": False}
            for k, v in variables.items()
        ]
        
        response = requests.post(
            f"{self.api_url}/applications/{app_uuid}/envs",
            headers=self.headers,
            json={"envs": env_list}
        )
        
        return response.status_code == 200


def load_env_file(env_path: str = ".env") -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    
    if not os.path.exists(env_path):
        print(f"⚠️  No .env file found at {env_path}")
        return env_vars
    
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value
    
    return env_vars


def deploy_to_coolify():
    """Main deployment function."""
    print("🚀 Starting Meta Agent deployment to Coolify...")
    
    # Check for required tokens
    if not COOLIFY_API_TOKEN:
        print("❌ COOLIFY_API_TOKEN not set")
        print("   Set it with: export COOLIFY_API_TOKEN=your_token")
        return False
    
    # Initialize deployer
    deployer = CoolifyDeployer(COOLIFY_API_URL, COOLIFY_API_TOKEN)
    
    # Check connection
    print("📡 Checking connection to Coolify...")
    if not deployer.check_connection():
        print("❌ Cannot connect to Coolify. Check your API URL and token.")
        return False
    
    print("✅ Connected to Coolify")
    
    # List servers
    servers = deployer.list_servers()
    if not servers:
        print("❌ No servers available in Coolify")
        return False
    
    print(f"✅ Found {len(servers)} server(s)")
    server_uuid = servers[0].get("uuid")
    
    # List or create project
    projects = deployer.list_projects()
    project_uuid = None
    
    for project in projects:
        if project.get("name") == "Archon X":
            project_uuid = project.get("uuid")
            print(f"✅ Found existing project: Archon X")
            break
    
    if not project_uuid:
        print("📦 Creating new project: Archon X")
        project_uuid = deployer.create_project(
            name="Archon X",
            description="AI-native operating system with transparent agent collaboration"
        )
        
        if not project_uuid:
            print("❌ Failed to create project")
            return False
        
        print(f"✅ Project created: {project_uuid}")
    
    # Load environment variables
    print("🔐 Loading environment variables...")
    env_vars = load_env_file()
    
    # Filter out sensitive variables that shouldn't be sent
    safe_env_vars = {
        k: v for k, v in env_vars.items()
        if not any(sensitive in k.upper() for sensitive in ["TOKEN", "SECRET", "PASSWORD", "KEY"])
    }
    
    # Add required variables
    safe_env_vars.update({
        "PYTHONUNBUFFERED": "1",
        "NODE_ENV": "production",
    })
    
    print(f"✅ Loaded {len(safe_env_vars)} environment variables")
    
    # Create application
    print("📦 Creating application...")
    git_repo = os.environ.get("GIT_REPO", "https://github.com/your-org/meta-agent.git")
    domain = os.environ.get("DOMAIN", "meta-agent.example.com")
    
    app_uuid = deployer.create_application(
        project_uuid=project_uuid,
        server_uuid=server_uuid,
        git_repository=git_repo,
        git_branch="main",
        domain=domain,
        environment_variables=safe_env_vars,
    )
    
    if not app_uuid:
        print("❌ Failed to create application")
        return False
    
    print(f"✅ Application created: {app_uuid}")
    
    # Set sensitive environment variables separately
    print("🔐 Setting sensitive environment variables...")
    sensitive_vars = {
        k: v for k, v in env_vars.items()
        if any(sensitive in k.upper() for sensitive in ["TOKEN", "SECRET", "PASSWORD", "KEY"])
    }
    
    if sensitive_vars:
        deployer.set_environment_variables(app_uuid, sensitive_vars)
        print(f"✅ Set {len(sensitive_vars)} sensitive variables")
    
    # Deploy
    print("🚀 Deploying application...")
    if not deployer.deploy_application(app_uuid):
        print("❌ Failed to start deployment")
        return False
    
    print("✅ Deployment started!")
    
    # Wait for deployment
    print("⏳ Waiting for deployment to complete...")
    max_wait = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status = deployer.get_application_status(app_uuid)
        app_status = status.get("status", "unknown")
        
        print(f"   Status: {app_status}")
        
        if app_status == "running":
            print("✅ Application is running!")
            break
        elif app_status == "failed":
            print("❌ Deployment failed")
            return False
        
        time.sleep(10)
    
    print("\n" + "=" * 50)
    print("🎉 Deployment Complete!")
    print("=" * 50)
    print(f"Application UUID: {app_uuid}")
    print(f"Domain: https://{domain}")
    print(f"API: https://{domain}/api")
    print(f"WebSocket: wss://{domain}/ws")
    print("=" * 50)
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Meta Agent to Coolify")
    parser.add_argument("--api-url", help="Coolify API URL")
    parser.add_argument("--api-token", help="Coolify API token")
    parser.add_argument("--domain", help="Domain for the application")
    parser.add_argument("--git-repo", help="Git repository URL")
    
    args = parser.parse_args()
    
    # Override from command line
    if args.api_url:
        os.environ["COOLIFY_API_URL"] = args.api_url
    if args.api_token:
        os.environ["COOLIFY_API_TOKEN"] = args.api_token
    if args.domain:
        os.environ["DOMAIN"] = args.domain
    if args.git_repo:
        os.environ["GIT_REPO"] = args.git_repo
    
    success = deploy_to_coolify()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
