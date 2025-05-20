# MCP Window Layout Driver

A tool for managing window layouts in MCP (Mission Control Panel) environment.

## Features

- Process management
  - List all processes
  - Get process by name
  - Get process status
  - Start/Stop process
  - Set process name

## Installation

### Using pip

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install the package:
```bash
pip install -e .
```

### Using uv (Recommended)

1. Install uv if you haven't:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package:
```bash
uv pip install -e .
```

## Development

### Using pip
Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Using uv
Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

### Development Tools

- **Code Formatting**: `black .`
- **Import Sorting**: `isort .`
- **Type Checking**: `mypy .`
- **Code Linting**: `ruff check .`

## Usage

Run the driver:
```bash
python -m src.layout_driver
```

## License

MIT License
