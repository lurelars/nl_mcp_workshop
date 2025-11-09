"""
Unit tests for the Database module
"""

import pytest
import json
from src.database import Database


class TestDatabase:
    """Test suite for Database class"""

    @pytest.mark.asyncio
    async def test_add_favorite_success(self, database):
        """Test successfully adding a favorite"""
        result = await database.add_favorite("person", 1, "My favorite character")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert "Added person ID 1 to favorites" in result_data["message"]
        assert result_data["favorite"]["type"] == "person"
        assert result_data["favorite"]["id"] == 1
        assert result_data["favorite"]["notes"] == "My favorite character"
        assert "added_at" in result_data["favorite"]

    @pytest.mark.asyncio
    async def test_add_favorite_invalid_type(self, database):
        """Test adding a favorite with invalid type"""
        result = await database.add_favorite("invalid_type", 1, "Test")
        result_data = json.loads(result)

        assert "error" in result_data
        assert "Invalid item type" in result_data["error"]

    @pytest.mark.asyncio
    async def test_add_favorite_duplicate(self, database):
        """Test adding duplicate favorite"""
        await database.add_favorite("person", 1, "First time")
        result = await database.add_favorite("person", 1, "Second time")
        result_data = json.loads(result)

        assert "error" in result_data
        assert "Already exists" in result_data["error"]

    @pytest.mark.asyncio
    async def test_list_favorites_empty(self, database):
        """Test listing favorites when database is empty"""
        result = await database.list_favorites()
        result_data = json.loads(result)

        assert result_data["count"] == 0
        assert result_data["favorites"] == []

    @pytest.mark.asyncio
    async def test_list_favorites_with_items(self, database):
        """Test listing favorites with multiple items"""
        await database.add_favorite("person", 1, "Luke")
        await database.add_favorite("planet", 1, "Tatooine")
        await database.add_favorite("starship", 9, "Death Star")

        result = await database.list_favorites()
        result_data = json.loads(result)

        assert result_data["count"] == 3
        assert len(result_data["favorites"]) == 3

    @pytest.mark.asyncio
    async def test_list_favorites_filtered(self, database):
        """Test listing favorites filtered by type"""
        await database.add_favorite("person", 1, "Luke")
        await database.add_favorite("person", 2, "Leia")
        await database.add_favorite("planet", 1, "Tatooine")

        result = await database.list_favorites("person")
        result_data = json.loads(result)

        assert result_data["count"] == 2
        assert all(fav["type"] == "person" for fav in result_data["favorites"])

    @pytest.mark.asyncio
    async def test_remove_favorite_success(self, database):
        """Test successfully removing a favorite"""
        await database.add_favorite("person", 1, "Luke")
        result = await database.remove_favorite("person", 1)
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert "Removed person ID 1" in result_data["message"]

        # Verify it's actually removed
        list_result = await database.list_favorites()
        list_data = json.loads(list_result)
        assert list_data["count"] == 0

    @pytest.mark.asyncio
    async def test_remove_favorite_not_found(self, database):
        """Test removing a non-existent favorite"""
        result = await database.remove_favorite("person", 999)
        result_data = json.loads(result)

        assert "error" in result_data
        assert "Not found" in result_data["error"]

    @pytest.mark.asyncio
    async def test_update_notes_success(self, database):
        """Test successfully updating notes"""
        await database.add_favorite("person", 1, "Original notes")
        result = await database.update_notes("person", 1, "Updated notes")
        result_data = json.loads(result)

        assert result_data["success"] is True

        # Verify notes were updated
        list_result = await database.list_favorites()
        list_data = json.loads(list_result)
        assert list_data["favorites"][0]["notes"] == "Updated notes"
        assert "updated_at" in list_data["favorites"][0]

    @pytest.mark.asyncio
    async def test_update_notes_not_found(self, database):
        """Test updating notes for non-existent favorite"""
        result = await database.update_notes("person", 999, "New notes")
        result_data = json.loads(result)

        assert "error" in result_data
        assert "Not found" in result_data["error"]

    @pytest.mark.asyncio
    async def test_search_favorites_found(self, database):
        """Test searching favorites with matches"""
        await database.add_favorite("person", 1, "Luke is a Jedi")
        await database.add_favorite("person", 2, "Leia is a princess")
        await database.add_favorite("planet", 1, "Desert planet")

        result = await database.search_favorites("Jedi")
        result_data = json.loads(result)

        assert result_data["count"] == 1
        assert result_data["matches"][0]["id"] == 1
        assert "Jedi" in result_data["matches"][0]["notes"]

    @pytest.mark.asyncio
    async def test_search_favorites_case_insensitive(self, database):
        """Test that search is case insensitive"""
        await database.add_favorite("person", 1, "Luke is a JEDI")

        result = await database.search_favorites("jedi")
        result_data = json.loads(result)

        assert result_data["count"] == 1

    @pytest.mark.asyncio
    async def test_search_favorites_no_matches(self, database):
        """Test searching with no matches"""
        await database.add_favorite("person", 1, "Luke")

        result = await database.search_favorites("Sith")
        result_data = json.loads(result)

        assert result_data["count"] == 0
        assert result_data["matches"] == []

    @pytest.mark.asyncio
    async def test_clear_all(self, database):
        """Test clearing all favorites"""
        await database.add_favorite("person", 1, "Luke")
        await database.add_favorite("planet", 1, "Tatooine")

        result = await database.clear_all()
        result_data = json.loads(result)

        assert result_data["success"] is True

        # Verify database is empty
        list_result = await database.list_favorites()
        list_data = json.loads(list_result)
        assert list_data["count"] == 0

    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(self, database):
        """Test a sequence of operations to ensure state consistency"""
        # Add multiple favorites
        await database.add_favorite("person", 1, "Luke")
        await database.add_favorite("person", 2, "Leia")
        await database.add_favorite("planet", 1, "Tatooine")

        # Update one
        await database.update_notes("person", 1, "Luke - Jedi Master")

        # Remove one
        await database.remove_favorite("person", 2)

        # Verify final state
        result = await database.list_favorites()
        result_data = json.loads(result)

        assert result_data["count"] == 2
        luke = next(f for f in result_data["favorites"] if f["id"] == 1 and f["type"] == "person")
        assert luke["notes"] == "Luke - Jedi Master"
