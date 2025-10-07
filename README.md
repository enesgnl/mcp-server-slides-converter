# mcp-server-slides-converter

SlideConverter is an MCP server that converts a PDF slide deck into a 4-up layout (four slide thumbnails per page) and returns the result as a Base64-encoded PDF.

## Requirements
- Python 3.10+
- No Poppler required (uses PyMuPDF/fitz for rendering)

## Installation

```bash
pip install -r requirements.txt
```

## Run locally

```bash
python slides_converter.py
```

## MCP Integration

This repository exposes an MCP server discoverable via the `mcp.json` manifest over stdio.

- Server command: `python slides_converter.py`
- Tool signature: `convert_pdf_4up(input_pdf_base64?: string, input_pdf_path?: string, dpi?: int = 72)`
- Output: `{ filename: string, pdf_base64: string, mime_type: "application/pdf" }`

### Run with uv

```bash
uv run -p 3.10 fastmcp mcp.json
```

If Python 3.10+ is not available, install 3.10/3.11 (e.g., with `pyenv`) and select it via the `-p` flag.

## Notes

- Inputs: provide either `input_pdf_base64` (Base64-encoded PDF bytes) or `input_pdf_path` (absolute/working-directory file path).
- `dpi` default is 72 for faster processing and smaller outputs. Increase for higher quality if needed.

### Saving the returned PDF (client-side example)

```python
import base64

result = tool_call_result  # { filename, pdf_base64, mime_type }
with open(result["filename"], "wb") as f:
    f.write(base64.b64decode(result["pdf_base64"]))
```

## Packaging

`pyproject.toml` is provided for packaging and dependency metadata.

## License

MIT
