
# School Info Service (Node 5)

## Overview
This is a standalone Microservice (MSA Node) responsible for:
1.  **Crawling** school data from `schoolinfo.go.kr`.
2.  **Generating** high-fidelity PDF documents (Teaching Plans) using Typst.
3.  **Serving** these documents via a REST API.

## Architecture
- **Framework**: FastAPI
- **Engine**: Typst (Must be installed in system path)
- **Data**: Local filesystem (`downloads/`)
- **Crawler Mode**: **Simulation Only** (Real site `schoolinfo.go.kr` blocks headless requests. Data is mocked for architectural verification.)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Typst**
   Ensure `typst` CLI is available in your PATH.

3. **Install Fonts**
   Ensure `NanumGothic` (Korean font) is installed in standard system font directories.

## Running the Service
```bash
python main.py
```
The server will start at `http://localhost:8005`.

## Real Browser Agent (Experimental)
To bypass site blocks, use the Playwright-based agent:
```bash
playwright install
python src/agent_crawler.py
```
*Note: This works best in a local environment with a headed browser.*

## API Endpoints
- `GET /health`: Health check.
- `POST /schools/{code}/teaching-plans`: Triggers crawler + PDF gen.
- `GET /downloads/{code}/{year}/{filename}`: Download generated PDFs.
