# Code Review Assistant

An AI-powered code review assistant that analyzes Python code for complexity, best practices, and potential issues using the CodeBERT model.

## Features

- Code complexity analysis
- Best practices enforcement
- Code metrics calculation
- Issue detection
- Multiple file analysis support
- File upload capability
- REST API interface

## Prerequisites

- Python 3.8+ (for local installation)
- Redis (optional - for caching)
- Docker (for Docker installation)
- pip or conda for package management (for local installation)

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/SohamPrabhu/codereviewer.git
cd codereviewer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/MacOS
# or
.\venv\Scripts\activate   # On Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/SohamPrabhu/codereviewer.git
cd codereviewer
```

2. Build the Docker image:
```bash
docker build -t code-reviewer -f docker/Dockerfile .
```

3. Run the container:
```bash
docker run -d -p 8000:8000 code-reviewer
```

Or using docker-compose:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

This will:
- Build the image using the Dockerfile
- Start the FastAPI server inside the container
- Map port 8000 from the container to your host machine
- Start Redis (if using docker-compose)

## Project Structure

```
code-review-assistant/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py    # FastAPI endpoints
│   ├── ml/
│   │   ├── __init__.py
│   │   └── code_analyzer.py # CodeBERT analyzer
│   └── services/
├── tests/
├── docker/
│   ├── Dockerfile         # Docker configuration
│   └── docker-compose.yml # Docker Compose configuration
├── notebooks/
├── data/
├── requirements.txt
├── setup.py
└── README.md
```

## Usage

### Starting the Server

#### Local Run:
```bash
uvicorn src.api.endpoints:app --reload --host 0.0.0.0 --port 8000
```

#### Docker Run:
```bash
# Using Docker
docker run -d -p 8000:8000 code-reviewer

# Using Docker Compose
docker-compose -f docker/docker-compose.yml up -d
```

### API Endpoints

1. Analyze a Single File:
```bash
curl -X POST http://localhost:8000/analyze-file \
  -F "file=@/path/to/your/code.py"
```

2. Analyze Multiple Files:
```bash
curl -X POST http://localhost:8000/analyze-multiple \
  -F "files=@file1.py" \
  -F "files=@file2.py"
```

3. Analyze Code Snippet:
```bash
curl -X POST http://localhost:8000/analyze-code \
  -H "Content-Type: application/json" \
  -d '"def example():\n    print(\"hello\")\n"'
```

### Example Response

```json
{
  "Complexity_Score": 0.75,
  "Line Count": 50,
  "Suggestions": [
    "Functions are too complex consider breaking it down",
    "Class names should use the proper CapWords Convention"
  ],
  "code metrics": {
    "total lines": 50,
    "blank lines": 5,
    "comment lines": 3,
    "function_count": 2
  },
  "potential issues": [
    {
      "type": "long Function",
      "name": "example_function",
      "message": "Has Too Many Lines: (60 lines)"
    }
  ],
  "best practices": [
    {
      "type": "missing documentation",
      "message": "Functions are missing documentation"
    }
  ]
}
```

### Docker Commands

```bash
# Build the image
docker build -t code-reviewer -f docker/Dockerfile .

# Run the container
docker run -d -p 8000:8000 code-reviewer

# Stop the container
docker stop $(docker ps -q --filter ancestor=code-reviewer)

# View logs
docker logs $(docker ps -q --filter ancestor=code-reviewer)

# Interactive shell
docker exec -it $(docker ps -q --filter ancestor=code-reviewer) /bin/bash
```

### Docker Compose Commands

```bash
# Start services
docker-compose -f docker/docker-compose.yml up -d

# Stop services
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Rebuild and restart
docker-compose -f docker/docker-compose.yml up -d --build
```

## Analysis Features

The code analyzer checks for:
- Code complexity using CodeBERT
- Function length and complexity
- Naming conventions
- Documentation presence
- Code duplication
- Nesting depth
- Best practices compliance


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CodeBERT model by Microsoft
- FastAPI framework
- Transformers library by Hugging Face

