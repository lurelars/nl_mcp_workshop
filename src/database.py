"""
Local Database Module

Manages a local JSON file to store and manipulate user's favorite Star Wars items.
This mimics database operations for the workshop.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class Database:
    """Local JSON database for storing favorite Star Wars items"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database.

        Args:
            db_path: Optional path to the database file. Defaults to data/local_db.json
        """
        if db_path is None:
            # Default to data/local_db.json relative to project root
            project_root = Path(__file__).parent.parent
            self.db_path = project_root / "data" / "local_db.json"
        else:
            self.db_path = Path(db_path)

        # Ensure the database file exists
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the database file if it doesn't exist"""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_db({"favorites": []})

    def _read_db(self) -> Dict[str, Any]:
        """Read the database file"""
        try:
            with open(self.db_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {"favorites": []}
                return json.loads(content)
        except json.JSONDecodeError:
            # If JSON is corrupted, reset the database
            return {"favorites": []}
        except Exception as e:
            raise Exception(f"Failed to read database: {str(e)}")

    def _write_db(self, data: Dict[str, Any]):
        """Write to the database file"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to write to database: {str(e)}")

    async def add_favorite(self, item_type: str, item_id: int, notes: str = "") -> str:
        """
        Add an item to favorites.

        Args:
            item_type: Type of item ('person', 'planet', 'starship', 'film')
            item_id: The ID of the item
            notes: Optional notes about the item

        Returns:
            Success message as JSON string
        """
        # Validate item type
        valid_types = ['person', 'planet', 'starship', 'film']
        if item_type not in valid_types:
            return json.dumps({
                "error": "Invalid item type",
                "message": f"Item type must be one of: {', '.join(valid_types)}"
            })

        db = self._read_db()

        # Check if already exists
        for fav in db["favorites"]:
            if fav["type"] == item_type and fav["id"] == item_id:
                return json.dumps({
                    "error": "Already exists",
                    "message": f"{item_type.capitalize()} with ID {item_id} is already in favorites"
                })

        # Add new favorite
        favorite = {
            "type": item_type,
            "id": item_id,
            "notes": notes,
            "added_at": datetime.now().isoformat()
        }

        db["favorites"].append(favorite)
        self._write_db(db)

        return json.dumps({
            "success": True,
            "message": f"Added {item_type} ID {item_id} to favorites",
            "favorite": favorite
        }, indent=2)

    async def list_favorites(self, item_type: Optional[str] = None) -> str:
        """
        List all favorites, optionally filtered by type.

        Args:
            item_type: Optional filter by type

        Returns:
            JSON string containing favorites
        """
        db = self._read_db()
        favorites = db["favorites"]

        if item_type:
            favorites = [f for f in favorites if f["type"] == item_type]

        return json.dumps({
            "count": len(favorites),
            "favorites": favorites
        }, indent=2)

    async def remove_favorite(self, item_type: str, item_id: int) -> str:
        """
        Remove an item from favorites.

        Args:
            item_type: Type of item
            item_id: The ID of the item

        Returns:
            Success message as JSON string
        """
        db = self._read_db()
        original_count = len(db["favorites"])

        # Filter out the item to remove
        db["favorites"] = [
            f for f in db["favorites"]
            if not (f["type"] == item_type and f["id"] == item_id)
        ]

        if len(db["favorites"]) == original_count:
            return json.dumps({
                "error": "Not found",
                "message": f"{item_type.capitalize()} with ID {item_id} not found in favorites"
            })

        self._write_db(db)

        return json.dumps({
            "success": True,
            "message": f"Removed {item_type} ID {item_id} from favorites"
        }, indent=2)

    async def update_notes(self, item_type: str, item_id: int, notes: str) -> str:
        """
        Update notes for a favorite item.

        Args:
            item_type: Type of item
            item_id: The ID of the item
            notes: New notes

        Returns:
            Success message as JSON string
        """
        db = self._read_db()

        # Find and update the item
        found = False
        for fav in db["favorites"]:
            if fav["type"] == item_type and fav["id"] == item_id:
                fav["notes"] = notes
                fav["updated_at"] = datetime.now().isoformat()
                found = True
                break

        if not found:
            return json.dumps({
                "error": "Not found",
                "message": f"{item_type.capitalize()} with ID {item_id} not found in favorites"
            })

        self._write_db(db)

        return json.dumps({
            "success": True,
            "message": f"Updated notes for {item_type} ID {item_id}"
        }, indent=2)

    async def search_favorites(self, query: str) -> str:
        """
        Search favorites by notes content.

        Args:
            query: Search term

        Returns:
            JSON string containing matching favorites
        """
        db = self._read_db()
        query_lower = query.lower()

        # Search in notes
        matches = [
            f for f in db["favorites"]
            if query_lower in f.get("notes", "").lower()
        ]

        return json.dumps({
            "query": query,
            "count": len(matches),
            "matches": matches
        }, indent=2)

    async def clear_all(self) -> str:
        """
        Clear all favorites from the database.
        USE WITH CAUTION - This cannot be undone!

        Returns:
            Success message as JSON string
        """
        self._write_db({"favorites": []})

        return json.dumps({
            "success": True,
            "message": "All favorites have been cleared"
        }, indent=2)
