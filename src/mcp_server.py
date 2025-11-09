"""
MCP Server for Star Wars API Workshop

This server provides:
- Resources: Access to Star Wars API data (people, planets, starships, etc.)
- Tools: Database operations to store and manipulate local data
"""

from fastmcp import FastMCP
from swapi_client import SWAPIClient
from database import Database

# Initialize FastMCP server
mcp = FastMCP(
    "Star Wars API Workshop Server",
    dependencies=["requests"]
)

# Initialize clients
swapi_client = SWAPIClient()
db = Database()


# Resources - Star Wars API Data Access
@mcp.resource("swapi://people/{person_id}")
async def get_person(person_id: int) -> str:
    """
    Get information about a Star Wars character by ID.

    Args:
        person_id: The ID of the character (1-83)

    Returns:
        JSON string containing character information
    """
    return await swapi_client.get_person(person_id)


@mcp.resource("swapi://planets/{planet_id}")
async def get_planet(planet_id: int) -> str:
    """
    Get information about a Star Wars planet by ID.

    Args:
        planet_id: The ID of the planet (1-60)

    Returns:
        JSON string containing planet information
    """
    return await swapi_client.get_planet(planet_id)


@mcp.resource("swapi://starships/{starship_id}")
async def get_starship(starship_id: int) -> str:
    """
    Get information about a Star Wars starship by ID.

    Args:
        starship_id: The ID of the starship

    Returns:
        JSON string containing starship information
    """
    return await swapi_client.get_starship(starship_id)


@mcp.resource("swapi://films/{film_id}")
async def get_film(film_id: int) -> str:
    """
    Get information about a Star Wars film by ID.

    Args:
        film_id: The ID of the film (1-6)

    Returns:
        JSON string containing film information
    """
    return await swapi_client.get_film(film_id)


# Tools - Database Operations
@mcp.tool()
async def add_favorite(item_type: str, item_id: int, notes: str = "") -> str:
    """
    Add a Star Wars item to your favorites database.

    Use this tool to save your favorite characters, planets, starships, or films
    from the Star Wars universe to your local database for quick reference.

    Args:
        item_type: Type of item ('person', 'planet', 'starship', 'film')
        item_id: The ID of the item from SWAPI
        notes: Optional personal notes about why this is a favorite

    Returns:
        Confirmation message with the added item details
    """
    return await db.add_favorite(item_type, item_id, notes)


@mcp.tool()
async def list_favorites(item_type: str = None) -> str:
    """
    List all your favorite Star Wars items from the database.

    Use this tool to view all items you've saved as favorites, optionally
    filtered by type (person, planet, starship, or film).

    Args:
        item_type: Optional filter by type ('person', 'planet', 'starship', 'film')

    Returns:
        JSON string containing all favorites or filtered favorites
    """
    return await db.list_favorites(item_type)


@mcp.tool()
async def remove_favorite(item_type: str, item_id: int) -> str:
    """
    Remove a Star Wars item from your favorites database.

    Use this tool to delete an item from your favorites list.

    Args:
        item_type: Type of item ('person', 'planet', 'starship', 'film')
        item_id: The ID of the item to remove

    Returns:
        Confirmation message
    """
    return await db.remove_favorite(item_type, item_id)


@mcp.tool()
async def update_favorite_notes(item_type: str, item_id: int, notes: str) -> str:
    """
    Update the notes for a favorite Star Wars item in your database.

    Use this tool to modify or add notes to an existing favorite item.

    Args:
        item_type: Type of item ('person', 'planet', 'starship', 'film')
        item_id: The ID of the item
        notes: New notes to replace existing notes

    Returns:
        Confirmation message
    """
    return await db.update_notes(item_type, item_id, notes)


@mcp.tool()
async def search_favorites(query: str) -> str:
    """
    Search your favorites database by notes content.

    Use this tool to find favorites based on keywords in your notes.

    Args:
        query: Search term to look for in notes

    Returns:
        JSON string containing matching favorites
    """
    return await db.search_favorites(query)


# Prompts - Helper prompts for common tasks
@mcp.prompt()
async def explore_character(character_name: str) -> str:
    """
    Get a comprehensive overview of a Star Wars character.

    This prompt helps you explore a character by searching for them
    and displaying their full information including homeworld and films.
    """
    return f"""Please help me explore the Star Wars character "{character_name}".

1. Search for the character in the Star Wars API
2. Display their key information (name, height, mass, birth year, etc.)
3. If they have a homeworld, fetch and display information about it
4. List the films they appeared in
5. Ask if I'd like to add them to my favorites
"""


@mcp.prompt()
async def compare_items(item_type: str, id1: int, id2: int) -> str:
    """
    Compare two Star Wars items side by side.

    This prompt helps you compare two items of the same type.
    """
    return f"""Please compare these two Star Wars {item_type}s:

1. Fetch data for {item_type} ID {id1}
2. Fetch data for {item_type} ID {id2}
3. Display them side by side highlighting key differences
4. Provide a summary of the comparison
"""


if __name__ == "__main__":
    import sys

    # Check for SSE mode flag
    if False:#len(sys.argv) > 1 and sys.argv[1] == "--sse":
        # Run in SSE mode (HTTP server)
        port = 8000#int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"Starting MCP server in SSE mode on http://localhost:{port}")
        print("Press Ctrl+C to stop")
        mcp.run(transport="sse", port=port)
    else:
        # Run in stdio mode (default - launched by client)
        mcp.run()
