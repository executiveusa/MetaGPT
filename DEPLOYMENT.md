# Meta Agent Deployment Guide

## Quick Start

### Prerequisites

1. **Coolify Instance**: A running Coolify self-hosted platform
2. **API Tokens**: Coolify API token with deployment permissions
3. **Domain**: A domain name pointing to your Coolify instance
4. **Git Repository**: The Meta Agent code pushed to a Git repository

### Deployment Steps

#### Option 1: Deploy via Coolify Dashboard

1. **Log in to Coolify Dashboard**
   - Navigate to your Coolify instance (e.g., `https://coolify.example.com`)

2. **Create New Project**
   - Click "New Project"
   - Name: `Archon X`
   - Description: `AI-native operating system with transparent agent collaboration`

3. **Add Application**
   - Click "New Resource" → "Application"
   - Select "Git Repository"
   - Enter repository URL: `https://github.com/your-org/meta-agent.git`
   - Branch: `main`

4. **Configure Build Settings**
   - Build Pack: `Dockerfile`
   - Dockerfile Location: `/Dockerfile.meta`
   - Exposed Ports: `8000, 3000`

5. **Set Environment Variables**
   - Copy variables from `.env.example`
   - Add your API keys and secrets
   - **Never commit real secrets to Git!**

6. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Access at your configured domain

#### Option 2: Deploy via CLI

```bash
# Set environment variables
export COOLIFY_API_URL="https://coolify.example.com/api/v1"
export COOLIFY_API_TOKEN="your-api-token"
export DOMAIN="meta-agent.example.com"
export GIT_REPO="https://github.com/your-org/meta-agent.git"

# Run deployment script
python scripts/deploy.py
```

#### Option 3: Deploy via Docker Compose

```bash
# Build and run locally
docker-compose -f docker-compose.meta.yml up -d

# Check status
docker-compose -f docker-compose.meta.yml ps

# View logs
docker-compose -f docker-compose.meta.yml logs -f meta-agent
```

### Post-Deployment Verification

1. **Health Check**
   ```bash
   curl https://your-domain.com/
   ```

2. **API Endpoints**
   ```bash
   # Get agents
   curl https://your-domain.com/api/agents
   
   # Get session summary
   curl https://your-domain.com/api/session
   ```

3. **WebSocket Connection**
   ```javascript
   const ws = new WebSocket('wss://your-domain.com/ws');
   ws.onmessage = (event) => console.log(event.data);
   ```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Coolify Platform                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│   │   Nginx     │────▶│  Meta Agent │────▶│   Redis     │  │
│   │  (Proxy)    │     │  (Backend)  │     │  (Cache)    │  │
│   └─────────────┘     └─────────────┘     └─────────────┘  │
│         │                    │                              │
│         │                    │                              │
│         ▼                    ▼                              │
│   ┌─────────────┐     ┌─────────────┐                      │
│   │ Connection  │     │  Canonical  │                      │
│   │   Window    │     │   Orders    │                      │
│   │ (Frontend)  │     │  (Storage)  │                      │
│   └─────────────┘     └─────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Yes* |
| `OPENAI_API_KEY` | OpenAI API key | Yes* |
| `GOOGLE_API_KEY` | Google AI API key | No |
| `SUPABASE_URL` | Supabase project URL | No |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | No |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | No |
| `COOLIFY_API_URL` | Coolify API endpoint | For deployment |
| `COOLIFY_API_TOKEN` | Coolify API token | For deployment |
| `DOMAIN` | Application domain | Yes |
| `NODE_ENV` | Node environment | Yes |

*At least one LLM API key is required

### Troubleshooting

#### Build Fails

1. Check Dockerfile syntax
2. Verify all dependencies in requirements.txt
3. Check build logs in Coolify dashboard

#### Application Won't Start

1. Check environment variables are set
2. Verify port configuration
3. Check application logs: `docker logs meta-agent`

#### WebSocket Connection Fails

1. Ensure Nginx is configured for WebSocket
2. Check CORS settings
3. Verify SSL certificate is valid

### Scaling

To scale the Meta Agent:

1. **Horizontal Scaling**: Add more application instances
2. **Redis**: Use Redis for session sharing
3. **Load Balancer**: Configure Coolify load balancing

### Security Checklist

- [ ] All secrets in environment variables (not in code)
- [ ] `.env` file is in `.gitignore`
- [ ] SSL certificate is configured
- [ ] API rate limiting enabled
- [ ] CORS configured for your domain only
- [ ] Authentication enabled for sensitive endpoints

---

*Generated by Meta Agent - Chief Orchestrator of Archon X*
