# AI Setup Guide for Insurance AI System

## Overview

This guide provides comprehensive instructions for setting up and configuring AI features in the Insurance AI System. The system supports multiple AI providers including OpenAI, Anthropic Claude, and various local LLM options.

## Quick Start

### 1. Basic OpenAI Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your_openai_api_key_here"

# Configure AI provider (default is OpenAI)
export AI_PROVIDER="openai"
export AI_MODEL="gpt-3.5-turbo"
export AI_TEMPERATURE="0.7"
export AI_MAX_TOKENS="2000"

# Start the system
python api.py
```

### 2. Test AI Features

```bash
# Test the AI integration
python test_ai_simple.py

# Check AI health
curl http://localhost:8080/ai/health

# Get AI analytics
curl http://localhost:8080/ai/analytics
```

## Supported AI Providers

### 1. OpenAI (Recommended for Production)

**Models Available:**
- `gpt-4`: Most capable, best for complex analysis
- `gpt-4-turbo`: Faster version of GPT-4
- `gpt-3.5-turbo`: Cost-effective, good for standard tasks
- `gpt-3.5-turbo-16k`: Extended context version

**Configuration:**
```bash
export OPENAI_API_KEY="sk-your-api-key"
export AI_PROVIDER="openai"
export AI_MODEL="gpt-3.5-turbo"  # or gpt-4
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional custom endpoint
```

**Cost Considerations:**
- GPT-3.5-turbo: ~$0.002/1K tokens
- GPT-4: ~$0.03/1K tokens
- Use GPT-3.5 for standard analysis, GPT-4 for complex cases

### 2. Anthropic Claude

**Models Available:**
- `claude-3-opus-20240229`: Most capable Claude model
- `claude-3-sonnet-20240229`: Balanced performance and cost
- `claude-3-haiku-20240307`: Fastest and most cost-effective

**Configuration:**
```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export AI_PROVIDER="anthropic"
export AI_MODEL="claude-3-sonnet-20240229"
```

**Benefits:**
- Excellent reasoning capabilities
- Strong safety features
- Good for complex analysis and ethical considerations

### 3. Local LLM Options

#### Option A: Ollama (Easiest)

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama2:7b
ollama pull mistral:7b
ollama pull codellama:7b

# Configure the system
export AI_PROVIDER="local"
export AI_MODEL="llama2:7b"
export LOCAL_LLM_BASE_URL="http://localhost:11434"
export LOCAL_LLM_PROVIDER_TYPE="ollama"
```

#### Option B: LM Studio

**Setup:**
1. Download and install LM Studio
2. Download a model (e.g., Llama 2 7B, Mistral 7B)
3. Start the local server

**Configuration:**
```bash
export AI_PROVIDER="local"
export AI_MODEL="llama-2-7b-chat"
export LOCAL_LLM_BASE_URL="http://localhost:1234"
export LOCAL_LLM_PROVIDER_TYPE="lmstudio"
```

#### Option C: Text Generation WebUI

**Setup:**
```bash
# Clone and setup text-generation-webui
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
pip install -r requirements.txt

# Start with API enabled
python server.py --api
```

**Configuration:**
```bash
export AI_PROVIDER="local"
export AI_MODEL="your_model_name"
export LOCAL_LLM_BASE_URL="http://localhost:5000"
export LOCAL_LLM_PROVIDER_TYPE="textgen"
```

#### Option D: llama.cpp Server

**Setup:**
```bash
# Build llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make

# Download a GGUF model
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

# Start server
./server -m llama-2-7b-chat.Q4_K_M.gguf -c 2048
```

**Configuration:**
```bash
export AI_PROVIDER="local"
export AI_MODEL="llama-2-7b-chat"
export LOCAL_LLM_BASE_URL="http://localhost:8080"
export LOCAL_LLM_PROVIDER_TYPE="llamacpp"
```

## Advanced Configuration

### Environment Variables

```bash
# Core AI Settings
export AI_ENABLED="true"
export AI_PROVIDER="openai"  # openai, anthropic, local
export AI_MODEL="gpt-3.5-turbo"
export AI_TEMPERATURE="0.7"  # 0.0-1.0, lower = more deterministic
export AI_MAX_TOKENS="2000"
export AI_TIMEOUT="30"  # seconds
export AI_MAX_RETRIES="3"

# Provider-specific settings
export OPENAI_API_KEY="your_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export ANTHROPIC_API_KEY="your_key"
export LOCAL_LLM_BASE_URL="http://localhost:11434"
export LOCAL_LLM_MODEL="llama2:7b"
export LOCAL_LLM_PROVIDER_TYPE="ollama"

# Feature flags
export AI_ENABLE_CACHING="true"
export AI_ENABLE_FALLBACK="true"
export AI_ENABLE_METRICS="true"
```

### Multi-Provider Setup (Recommended)

Configure multiple providers for redundancy:

```bash
# Primary provider
export AI_PROVIDER="openai"
export OPENAI_API_KEY="your_openai_key"

# Fallback providers
export AI_ENABLE_FALLBACK="true"
export ANTHROPIC_API_KEY="your_anthropic_key"

# Local fallback
export LOCAL_LLM_BASE_URL="http://localhost:11434"
```

## API Usage Examples

### 1. Enhanced Underwriting Analysis

```bash
curl -X POST "http://localhost:8080/ai/underwriting/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "application_data": {
      "applicant_name": "John Doe",
      "age": 35,
      "occupation": "Software Engineer",
      "annual_income": 85000,
      "credit_score": 750,
      "coverage_amount": 500000,
      "policy_type": "term_life"
    },
    "use_ai_only": false
  }'
```

### 2. Claims Fraud Detection

```bash
curl -X POST "http://localhost:8080/ai/claims/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_data": {
      "claim_id": "CLM-001",
      "policy_id": "POL-001",
      "claimed_amount": 2500,
      "claim_description": "Vehicle collision damage",
      "incident_location": "Main Street",
      "police_report": true
    },
    "use_ai_only": false
  }'
```

### 3. Actuarial Analysis

```bash
curl -X POST "http://localhost:8080/ai/actuarial/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_data": {
      "normalized_data": {
        "claims_data": [...],
        "policy_data": [...]
      },
      "analysis_results": {
        "claim_frequency": 0.15,
        "loss_ratio": 0.65
      }
    },
    "use_ai_only": false
  }'
```

### 4. AI Analytics and Monitoring

```bash
# Get AI performance analytics
curl "http://localhost:8080/ai/analytics?hours_back=24"

# Compare provider performance
curl "http://localhost:8080/ai/providers/comparison"

# Benchmark all providers
curl -X POST "http://localhost:8080/ai/benchmark"

# Export metrics
curl "http://localhost:8080/ai/analytics/export?format=json" > ai_metrics.json
```

## Performance Optimization

### 1. Model Selection Guidelines

**For Underwriting:**
- Simple cases: GPT-3.5-turbo or Claude Haiku
- Complex cases: GPT-4 or Claude Opus
- High volume: Local Llama2 7B

**For Claims:**
- Fraud detection: GPT-4 (better pattern recognition)
- Standard processing: GPT-3.5-turbo
- Privacy-sensitive: Local models

**For Actuarial:**
- Complex modeling: GPT-4 or Claude Opus
- Trend analysis: GPT-3.5-turbo
- Regulatory compliance: Claude (better safety)

### 2. Cost Optimization

```bash
# Use cheaper models for initial screening
export AI_MODEL="gpt-3.5-turbo"

# Enable caching to reduce API calls
export AI_ENABLE_CACHING="true"

# Use local models for high-volume processing
export AI_PROVIDER="local"
export LOCAL_LLM_MODEL="llama2:7b"
```

### 3. Performance Tuning

```bash
# Adjust temperature for consistency
export AI_TEMPERATURE="0.3"  # More deterministic

# Optimize token usage
export AI_MAX_TOKENS="1500"  # Reduce for faster responses

# Enable parallel processing
export AI_ENABLE_FALLBACK="true"
```

## Security and Privacy

### 1. Data Protection

```bash
# Use local models for sensitive data
export AI_PROVIDER="local"

# Enable data minimization
export AI_ENABLE_PRIVACY_MODE="true"

# Configure secure endpoints
export OPENAI_BASE_URL="https://your-secure-proxy.com/v1"
```

### 2. API Key Management

```bash
# Use environment variables (never hardcode)
export OPENAI_API_KEY="$(cat /secure/path/openai.key)"

# Rotate keys regularly
export ANTHROPIC_API_KEY="$(vault kv get -field=api_key secret/anthropic)"
```

### 3. Compliance Settings

```bash
# Enable audit logging
export AI_ENABLE_AUDIT_LOG="true"

# Set data retention limits
export AI_METRICS_RETENTION_DAYS="30"

# Enable GDPR compliance mode
export AI_GDPR_COMPLIANCE="true"
```

## Monitoring and Troubleshooting

### 1. Health Checks

```bash
# Check overall AI health
curl http://localhost:8080/ai/health

# Check specific provider
curl http://localhost:8080/ai/providers/comparison
```

### 2. Performance Monitoring

```bash
# View real-time analytics
curl http://localhost:8080/ai/analytics

# Export detailed metrics
curl http://localhost:8080/ai/analytics/export > metrics.json
```

### 3. Common Issues

**Issue: API Key Invalid**
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

**Issue: Local Model Not Responding**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

**Issue: High Response Times**
```bash
# Check current performance
curl http://localhost:8080/ai/analytics

# Switch to faster model
export AI_MODEL="gpt-3.5-turbo"
```

## Production Deployment

### 1. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Set environment variables
ENV AI_PROVIDER=openai
ENV AI_MODEL=gpt-3.5-turbo

# Start application
CMD ["python", "api.py"]
```

### 2. Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insurance-ai-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: insurance-ai-system
  template:
    metadata:
      labels:
        app: insurance-ai-system
    spec:
      containers:
      - name: api
        image: insurance-ai-system:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-api-key
        - name: AI_PROVIDER
          value: "openai"
        - name: AI_MODEL
          value: "gpt-3.5-turbo"
```

### 3. Load Balancing

```bash
# Use multiple providers for load distribution
export AI_ENABLE_FALLBACK="true"
export AI_PROVIDER="openai"
export ANTHROPIC_API_KEY="backup_key"
```

## Best Practices

### 1. Development

- Start with OpenAI GPT-3.5-turbo for development
- Use local models for testing and experimentation
- Enable comprehensive logging and monitoring
- Test with realistic insurance data

### 2. Staging

- Test all configured providers
- Validate performance under load
- Verify security and compliance settings
- Test failover scenarios

### 3. Production

- Use multiple providers for redundancy
- Monitor costs and performance continuously
- Implement proper security measures
- Regular backup of AI configurations and metrics

## Support and Resources

### Documentation
- [AI Features Documentation](./AI_FEATURES.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Configuration Reference](./CONFIGURATION.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Ask questions and share experiences

### Commercial Support
- Enterprise support available for production deployments
- Custom model training and fine-tuning services
- Compliance and security consulting