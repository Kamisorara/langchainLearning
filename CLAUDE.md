# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain learning project that demonstrates multimodal AI integration using LangGraph and vision models. The project processes images through an LLM node for content analysis and description, accessible both through direct Python execution and a FastAPI web interface.

## Architecture

The project implements a multimodal AI system with multiple interfaces:

### Core Components
- **main.py**: Defines LangGraph workflows with two implementations:
  - `ImageProcessingState` graph for new image processing functionality
  - `MessagesState` legacy graph for backward compatibility
  - Includes `process_image_with_graph()` utility function
- **llm_node.py**: Contains the core LLM logic that processes images using Qwen's vision model (qwen3-vl-plus)
  - `process_image_base64()`: Main function using Alibaba's DashScope API
  - `llm_node()` and `llm_node_legacy()`: State-based and legacy node functions
- **app.py**: FastAPI web application providing REST API with async processing
- **response_models.py**: Pydantic models for API responses and task management

### Workflow Patterns
1. **Direct Python execution**: `main.py → llm_node.py → AI response`
2. **Web API workflow**: `FastAPI → async task → graph processing → AI response`
3. **Fallback mechanism**: Graph processing with direct LLM call fallback

### Data Flow
- Images are loaded and encoded as base64
- LangGraph processes the image through the LLM node
- Qwen3-VL-Plus model analyzes the image and returns JSON responses
- The system supports both streaming and batch processing modes

## Environment Setup

The project uses Python 3.12+ and is managed with `uv` package manager.

### Required Environment Variables

Copy `.env.example` to `.env` and configure:
- `DASHSCOPE_API_KEY`: Your Alibaba DashScope API key
- `DASHSCOPE_API_URL`: API endpoint (defaults to `https://dashscope.aliyuncs.com/compatible-mode/v1`)

## Common Commands

### Installation
```bash
uv sync
```

### Running the Application
```bash
# Run FastAPI web server (primary application with API interface)
python app.py

# Run main LangGraph workflow directly
python main.py

# Run LLM node directly for testing
python llm_node.py
```

### API Development
```bash
# API runs on http://localhost:8080 by default
# Access interactive docs at http://localhost:8080/docs
# Health check endpoint: GET /health
```

## Key Dependencies

- `langchain>=1.1.2`: Core LangChain framework for LLM orchestration
- `langchain-openai>=1.1.0`: OpenAI-compatible API integration
- `langgraph>=1.0.4`: Graph-based workflow orchestration
- `fastapi>=0.124.0`: Modern async web framework for REST API
- `uvicorn[standard]>=0.30.0`: ASGI server for FastAPI
- `python-multipart>=0.0.9`: File upload handling
- `dotenv>=0.9.9`: Environment variable management

## Development Notes

### Image Processing
- Images can be processed from `./images/` directory (direct execution) or via upload (API)
- Supports multiple formats: JPEG, PNG, GIF, BMP, WebP
- Default test image: `./images/image1.jpg`
- All images are converted to base64 for processing

### API Features
- Async image upload and processing with task management
- Background processing with status tracking
- Multiple endpoints: upload, status check, sync processing, health check
- CORS middleware enabled (configure for production)
- Comprehensive error handling with fallback mechanisms

### Testing and Debugging
- Use `python llm_node.py` to test the LLM processing directly
- The API provides both async and sync processing endpoints
- Task IDs allow tracking processing status
- Response models include processing method (GRAPH, FALLBACK, DIRECT, FAILED)

## File Structure

```
.
├── app.py                 # FastAPI web application and API endpoints
├── main.py               # LangGraph workflow definition and utilities
├── llm_node.py           # Core LLM processing logic and vision model integration
├── response_models.py    # Pydantic models for API responses
├── images/               # Directory for input images (direct execution)
│   └── image1.jpg        # Default test image
├── reference/            # Documentation
│   └── README_API.md     # Detailed API documentation
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Environment variable template
└── pyproject.toml        # Project configuration and dependencies
```

## API Endpoints Summary

- `POST /upload-image`: Upload image for async processing
- `GET /status/{task_id}`: Check processing status and get results
- `POST /process-image-sync`: Synchronous image processing
- `GET /health`: Health check endpoint
- `GET /results`: Get all processing results
- `DELETE /results/{task_id}`: Delete specific result