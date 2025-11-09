# Star Wars API MCP Workshop

A hands-on workshop project demonstrating how to build a Model Context Protocol (MCP) server using FastMCP and the Star Wars API (SWAPI).

## Overview

This MCP server provides:
- **Resources**: Access to Star Wars API data (people, planets, starships, films)
- **Tools**: Database operations to store and manage favorite Star Wars items
- **Prompts**: Helper workflows for exploring and comparing Star Wars data

## Project Structure

```
nl_mcp_workshop/
├── src/
│   ├── mcp_server.py       # Main MCP server implementation
│   ├── swapi_client.py     # Star Wars API client
│   └── database.py         # Local database operations
├── data/
│   └── local_db.json       # JSON database for favorites
├── config/
│   └── mcp_config.json     # MCP server configuration
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_database.py    # Database unit tests
│   ├── test_swapi_client.py # SWAPI client unit tests
│   └── test_integration.py # Integration tests
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment file
└── setup.py               # Package setup
```

## Setup Instructions

### Prerequisites
- Python 3.12 or higher
- pip or conda package manager

### Option 1: Using Virtual Environment (venv)

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv mcp_workshop
   source mcp_workshop/bin/activate  # On Windows: mcp_workshop\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

### Option 2: Using Conda/Miniconda

1. **Create environment from file:**
   ```bash
   conda env create -f environment.yml
   ```

2. **Activate the environment:**
   ```bash
   conda activate mcp_workshop
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

## Running the MCP Server

### Method 1: Direct Execution
```bash
cd src
python mcp_server.py
```

### Method 2: From Anywhere (after `pip install -e .`)
```bash
python src/mcp_server.py
```

## Configuring with Claude Desktop

To use this MCP server with Claude Desktop, add the following to your Claude Desktop configuration file:

**macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "starwars-workshop": {
      "command": "python",
      "args": [
        "/absolute/path/to/nl_mcp_workshop/src/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/nl_mcp_workshop"
      }
    }
  }
}
```

**Note:** Replace `/absolute/path/to/nl_mcp_workshop` with the actual path to your project directory.

## Features

### Resources (Read-only API access)

Access Star Wars data using URI patterns:

- `swapi://people/{person_id}` - Get character information (IDs 1-83)
- `swapi://planets/{planet_id}` - Get planet information (IDs 1-60)
- `swapi://starships/{starship_id}` - Get starship information
- `swapi://films/{film_id}` - Get film information (IDs 1-6)

### Tools (Database operations)

Manage your favorite Star Wars items:

- **add_favorite(item_type, item_id, notes)** - Save an item to favorites
- **list_favorites(item_type)** - List all favorites (optional filter)
- **remove_favorite(item_type, item_id)** - Remove from favorites
- **update_favorite_notes(item_type, item_id, notes)** - Update notes
- **search_favorites(query)** - Search favorites by keywords

### Prompts (Helper workflows)

Pre-configured workflows for common tasks:

- **explore_character(character_name)** - Comprehensive character exploration
- **compare_items(item_type, id1, id2)** - Side-by-side comparison

## Running Tests

### Run all tests:
```bash
pytest -v
```

### Run specific test files:
```bash
pytest tests/test_database.py -v
pytest tests/test_swapi_client.py -v
pytest tests/test_integration.py -v
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in your browser.

## Example Usage

Once connected to Claude, you can:

1. **Explore a character:**
   ```
   Tell me about Luke Skywalker using the Star Wars API
   ```

2. **Save favorites:**
   ```
   Add Luke Skywalker (person ID 1) to my favorites with a note about him being the main hero
   ```

3. **List favorites:**
   ```
   Show me all my favorite Star Wars characters
   ```

4. **Search your notes:**
   ```
   Search my favorites for entries about Jedi
   ```

5. **Compare items:**
   ```
   Compare planets Tatooine (ID 1) and Alderaan (ID 2)
   ```

## Workshop Learning Goals

This project demonstrates:
- Building MCP servers with FastMCP
- Implementing Resources for external API access
- Creating Tools for stateful operations
- Defining Prompts for complex workflows
- API error handling and data validation
- Local data persistence with JSON
- Comprehensive testing strategies (unit + integration)

## API Reference

### Star Wars API (SWAPI)
- Base URL: https://swapi.dev/api/
- Documentation: https://swapi.dev/documentation
- No authentication required
- Rate limiting: Please be respectful

## Troubleshooting

### Import Errors
If you encounter `ModuleNotFoundError`:
```bash
# Make sure you're in the project root
pip install -e .
```

### Database Issues
If the database gets corrupted:
```bash
# Reset the database
echo '{"favorites": []}' > data/local_db.json
```

### API Timeouts
If SWAPI is slow or unavailable:
- Check your internet connection
- The API might be experiencing high load
- Wait a few moments and try again

## Contributing

This is a workshop project! Feel free to:
- Add new endpoints (vehicles, species)
- Enhance the database with more features
- Create additional prompts for complex workflows
- Improve error handling and logging

## License

This project is for educational purposes as part of the MCP workshop.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Star Wars API (SWAPI)](https://swapi.dev)
- [Claude Desktop](https://claude.ai/download)
