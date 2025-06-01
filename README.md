# Insurance AI System

A fully modular, production-grade Agentic AI system for the insurance industry, capable of handling:

1. Dynamic Underwriting  
2. Claims Automation  
3. Actuarial Analysis & Reporting  
4. Full Multi-Tenant and Branding Configuration

## System Architecture

The system is built with a modular architecture, where each module consists of specialized agents that work together to accomplish complex insurance tasks:

- **Underwriting Module**: Handles risk evaluation for new applications
- **Claims Module**: Manages claims processing and resolution
- **Actuarial Module**: Performs data analysis and reporting
- **Configuration System**: Provides institution-specific settings and branding

Each agent is designed to be production-ready with proper error handling, audit logging, and configuration validation.

## Features

- **Production-Grade Implementation**: No placeholders, stubs, or TODOs
- **Multi-Tenant Support**: Configurable for different institutions
- **Comprehensive Audit Logging**: All decisions and actions are logged
- **Robust Error Handling**: Graceful error recovery and reporting
- **Branding Integration**: Institution-specific branding throughout
- **API Access**: RESTful API for all system functions
- **Dockerized Deployment**: One-click deployment via Docker

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (for containerized deployment)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the System

#### Command Line Interface

Run a specific module:
```
python insurance_ai_system/main.py --module underwriting --institution institution_a
```

Run all modules:
```
python insurance_ai_system/main.py --module all --institution institution_a
```

#### API Server

Start the API server:
```
python insurance_ai_system/api.py --host 0.0.0.0 --port 8000
```

### Docker Deployment

Build the Docker image:
```
docker build -t insurance-ai-system .
```

Run the container:
```
docker run -p 8000:8000 insurance-ai-system
```

## Configuration

Institution-specific configuration is stored in JSON files in the `config` directory. Each institution has its own configuration file with settings for underwriting rules, claims thresholds, actuarial parameters, and branding.

## API Documentation

The system provides a RESTful API for all functionality:

- `POST /underwriting/evaluate`: Evaluate an insurance application
- `POST /claims/process`: Process an insurance claim
- `POST /actuarial/analyze`: Analyze actuarial data

All API endpoints require an `X-Institution-ID` header to specify the institution context.

## Project Structure

```
insurance_ai_system/
├── agents/                 # Agent implementations
│   ├── actuarial/          # Actuarial analysis agents
│   ├── base/               # Base agent classes
│   ├── claims/             # Claims processing agents
│   ├── underwriting/       # Underwriting agents
│   └── config_agent.py     # Configuration agent
├── config/                 # Institution configuration files
├── data/                   # Sample data files
├── docs/                   # Documentation
├── logs/                   # Audit and system logs
├── modules/                # Module flow implementations
│   ├── actuarial/
│   ├── claims/
│   └── underwriting/
├── utils/                  # Utility modules
│   ├── branding_utils.py   # Branding utilities
│   ├── config_utils.py     # Configuration utilities
│   ├── error_utils.py      # Error handling utilities
│   └── logging_utils.py    # Audit logging utilities
├── api.py                  # API server
├── main.py                 # Command-line interface
└── requirements.txt        # Python dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
