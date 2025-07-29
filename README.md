# Primer API Integration

This project provides a Python client for interacting with the Primer Enterprise Platform API. It includes tools for document analysis, search, and narrative extraction.

## Setup

### 1. Virtual Environment
The project uses a Python virtual environment. To activate it:

```bash
source venv/bin/activate
```

### 2. Dependencies
Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Authentication
Place your JWT token in a file named `token.txt` in the project root. The token should be a single line containing the JWT string.

## Files

- `primer_api_test.py` - Basic connection test script
- `primer_api_client.py` - Comprehensive API client class
- `openapi.json` - Primer API OpenAPI specification
- `token.txt` - JWT authentication token (not included in repo)
- `requirements.txt` - Python dependencies

### Panama Field Reports Project
- `upload_panama_reports.py` - Script to extract and upload Panama field reports
- `analyze_panama_reports.py` - Script to analyze uploaded reports using Primer features
- `panama_summary.py` - Summary of analysis results
- `panama_document_set_id.txt` - Document set identifier for uploaded reports
- `panama_sentiment_results.json` - Sentiment analysis results
- `Panama_Field_Reports/` - Directory containing 10 PDF field reports

### Streamlit Dashboard
- `streamlit_app.py` - Interactive web dashboard for analysis results
- `run_streamlit.sh` - Launcher script for the Streamlit app
- `test_streamlit.py` - Test script for data loading

## Usage

### Basic Connection Test
Test your connection to the Primer API:

```bash
python primer_api_test.py
```

### Panama Field Reports Analysis
Upload and analyze Panama field reports:

```bash
# Upload PDF reports to Primer
python upload_panama_reports.py

# Analyze uploaded reports
python analyze_panama_reports.py

# View analysis summary
python panama_summary.py

### Streamlit Dashboard
Launch the interactive web dashboard:

```bash
# Using the launcher script
./run_streamlit.sh

# Or directly with streamlit
streamlit run streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Using the API Client
```python
from primer_api_client import PrimerAPIClient

# Initialize client
client = PrimerAPIClient()

# List document sets
response = client.list_document_sets()
if response.success:
    print(f"Found {len(response.data)} document sets")

# Create a document set from raw text
texts = ["Sample document 1", "Sample document 2"]
response = client.create_document_set_from_text(texts)
if response.success:
    doc_set_id = response.data['document_set_id']
    print(f"Created document set: {doc_set_id}")

# Search for documents
search_request = {
    "search": {
        "query": {
            "concept": "artificial intelligence",
            "mode": "concept"
        },
        "results": {
            "max_results": 10
        }
    }
}
response = client.search_documents(search_request)
```

## API Features

The Primer API provides several key capabilities:

### Document Sets
- Create document sets from raw text, search results, or explicit document IDs
- List and manage existing document sets
- Delete document sets when no longer needed

### Search
- Semantic search using concept queries
- Boolean search with filters
- Aggregated search results

### Analysis Assets
- **Narrative Lookup**: Extract and cluster narratives from documents
- **Entity Table**: Identify and analyze entities mentioned in documents
- **Targeted Sentiment Analysis**: Analyze sentiment toward specific targets
- **Narrative Graphs**: Visualize narrative relationships and evolution

### Asset Management
- Create analysis assets
- Monitor processing status
- Retrieve results
- Clean up completed assets

## Example Workflows

### 1. Document Analysis
```python
# Create document set
response = client.create_document_set_from_text(["Document content here"])
doc_set_id = response.data['document_set_id']

# Create narrative lookup
response = client.create_narrative_lookup(doc_set_id)
narrative_asset_id = response.data['asset_id']

# Wait for completion and get results
client.wait_for_asset_completion("narrative-lookup", narrative_asset_id)
results = client.get_asset_results("narrative-lookup", narrative_asset_id)
```

### 2. Entity Analysis
```python
# Create entity table
response = client.create_entity_table(doc_set_id)
entity_asset_id = response.data['asset_id']

# Get entity results
results = client.get_asset_results("entity-table", entity_asset_id)
```

## Error Handling

The client includes comprehensive error handling:

- Network connectivity issues
- Authentication failures
- API rate limiting
- Invalid request parameters
- Asset processing failures

All methods return an `APIResponse` object with:
- `success`: Boolean indicating success/failure
- `status_code`: HTTP status code
- `data`: Response data (if successful)
- `error`: Error message (if failed)

## Rate Limits and Best Practices

- The API has rate limits; implement appropriate delays between requests
- Use the `wait_for_asset_completion` method for long-running operations
- Clean up assets when no longer needed
- Monitor API response status codes and handle errors gracefully

## Support

For API-specific questions, refer to the `openapi.json` specification or contact Primer support.

For client usage questions, check the example code in `primer_api_client.py`. 