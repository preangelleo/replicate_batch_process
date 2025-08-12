# Docker Setup Guide for replicate-batch-process

## 🐳 Docker Hub Repository
- **Docker Hub**: [preangelleo/replicate-batch-process](https://hub.docker.com/r/preangelleo/replicate-batch-process)
- **GitHub Container Registry**: ghcr.io/preangelleo/replicate-batch-process

## 📦 Using Pre-built Docker Images

### Pull the latest image:
```bash
docker pull preangelleo/replicate-batch-process:latest
```

### Run with your Replicate API token:
```bash
docker run -it --rm \
  -e REPLICATE_API_TOKEN="your-token-here" \
  -v $(pwd)/output:/app/output \
  preangelleo/replicate-batch-process:latest
```

### Using docker-compose:
```yaml
version: '3.8'
services:
  replicate-batch:
    image: preangelleo/replicate-batch-process:latest
    environment:
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
    volumes:
      - ./output:/app/output
      - ./input:/app/input
    command: python example_usage.py
```

## 🔧 GitHub Actions Setup (For Repository Maintainers)

### Required Secrets in GitHub Repository Settings

Navigate to: Settings → Secrets and variables → Actions

Add the following secrets:

1. **DOCKER_HUB_TOKEN** (Required)
   - Go to [Docker Hub Security Settings](https://hub.docker.com/settings/security)
   - Generate a new Access Token
   - Copy and add as GitHub secret

2. **PYPI_API_TOKEN** (Required for PyPI publishing)
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Generate API token (scope: project or entire account)
   - Copy and add as GitHub secret

3. **TEST_PYPI_API_TOKEN** (Optional, for test releases)
   - Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/)
   - Generate API token
   - Copy and add as GitHub secret

### Workflow Triggers

#### Docker Build & Push
- **Automatic**: On push to `main` branch
- **On Release**: When creating GitHub releases
- **Manual**: Via Actions tab → Docker Build and Push → Run workflow

#### PyPI Publishing
- **Automatic**: When creating a GitHub release
- **On Tag**: When pushing version tags (v*)
- **Manual**: Via Actions tab with version input

## 🏗️ Building Docker Image Locally

### Build for current architecture:
```bash
docker build -t replicate-batch-process:local .
```

### Build for multiple architectures:
```bash
# Setup buildx (one-time)
docker buildx create --name multiarch --use

# Build for amd64 and arm64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t replicate-batch-process:local \
  --load \
  .
```

### Test locally:
```bash
docker run -it --rm \
  -e REPLICATE_API_TOKEN="your-token-here" \
  replicate-batch-process:local \
  python -c "from replicate_batch_process import *; print('Success!')"
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| REPLICATE_API_TOKEN | Your Replicate API token | Yes |
| GEMINI_API_KEY | Google Gemini API key for prompt optimization | No |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

## 🚀 Deployment Examples

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: replicate-batch-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: replicate-batch
  template:
    metadata:
      labels:
        app: replicate-batch
    spec:
      containers:
      - name: processor
        image: preangelleo/replicate-batch-process:latest
        env:
        - name: REPLICATE_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: replicate-secrets
              key: api-token
        volumeMounts:
        - name: output
          mountPath: /app/output
      volumes:
      - name: output
        persistentVolumeClaim:
          claimName: output-pvc
```

### Docker Swarm
```bash
docker service create \
  --name replicate-batch \
  --secret replicate_token \
  --mount type=volume,source=output,target=/app/output \
  --replicas 3 \
  preangelleo/replicate-batch-process:latest
```

## 🔒 Security Best Practices

1. **Never hardcode API tokens** - Always use environment variables or secrets
2. **Use specific version tags** in production instead of `latest`
3. **Run as non-root user** (already configured in Dockerfile)
4. **Scan images regularly** with tools like Trivy (automated in CI)
5. **Keep base images updated** - Rebuild periodically

## 📊 Monitoring

The Docker image includes a health check that runs every 30 seconds:
```bash
docker inspect --format='{{json .State.Health}}' <container_id>
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs <container_id>

# Verify environment variables
docker exec <container_id> env | grep REPLICATE

# Test import
docker exec <container_id> python -c "import replicate_batch_process"
```

### Permission issues with output
```bash
# Fix ownership
docker exec <container_id> chown -R 1000:1000 /app/output

# Or mount with correct permissions
docker run -u $(id -u):$(id -g) ...
```

## 📚 Additional Resources

- [Docker Hub Repository](https://hub.docker.com/r/preangelleo/replicate-batch-process)
- [GitHub Repository](https://github.com/preangelleo/replicate_batch_process)
- [PyPI Package](https://pypi.org/project/replicate-batch-process/)
- [Replicate Documentation](https://replicate.com/docs)