"""
Integration tests for the MCP Server

These tests verify that all components work together correctly.
"""

import pytest
import json
import responses
import tempfile
from pathlib import Path
from src.swapi_client import SWAPIClient
from src.database import Database


class TestIntegration:
    """Integration test suite"""

    @pytest.fixture
    def integration_db(self):
        """Create a temporary database for integration testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump({"favorites": []}, f)

        yield Database(db_path=temp_path)

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def integration_client(self):
        """Create SWAPI client for integration testing"""
        return SWAPIClient()

    @pytest.mark.asyncio
    @responses.activate
    async def test_fetch_and_save_workflow(self, integration_client, integration_db, sample_person_data):
        """Test the full workflow: fetch from API and save to database"""
        # Mock the API response
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            json=sample_person_data,
            status=200
        )

        # Step 1: Fetch person from SWAPI
        person_result = await integration_client.get_person(1)
        person_data = json.loads(person_result)

        assert person_data["name"] == "Luke Skywalker"

        # Step 2: Save to favorites
        save_result = await integration_db.add_favorite(
            "person",
            1,
            f"My favorite character: {person_data['name']}"
        )
        save_data = json.loads(save_result)

        assert save_data["success"] is True

        # Step 3: Verify it's saved
        list_result = await integration_db.list_favorites()
        list_data = json.loads(list_result)

        assert list_data["count"] == 1
        assert list_data["favorites"][0]["type"] == "person"
        assert list_data["favorites"][0]["id"] == 1

    @pytest.mark.asyncio
    @responses.activate
    async def test_multiple_resources_workflow(self, integration_client, integration_db,
                                               sample_person_data, sample_planet_data):
        """Test fetching multiple resource types and managing favorites"""
        # Mock multiple API responses
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            json=sample_person_data,
            status=200
        )
        responses.add(
            responses.GET,
            "https://swapi.dev/api/planets/1/",
            json=sample_planet_data,
            status=200
        )

        # Fetch person
        person_result = await integration_client.get_person(1)
        person_data = json.loads(person_result)

        # Fetch planet
        planet_result = await integration_client.get_planet(1)
        planet_data = json.loads(planet_result)

        # Save both to favorites
        await integration_db.add_favorite("person", 1, f"Hero: {person_data['name']}")
        await integration_db.add_favorite("planet", 1, f"Homeworld: {planet_data['name']}")

        # Verify both are saved
        list_result = await integration_db.list_favorites()
        list_data = json.loads(list_result)

        assert list_data["count"] == 2
        types = [fav["type"] for fav in list_data["favorites"]]
        assert "person" in types
        assert "planet" in types

    @pytest.mark.asyncio
    @responses.activate
    async def test_search_and_save_workflow(self, integration_client, integration_db):
        """Test searching for a character and saving to favorites"""
        search_results = {
            "count": 1,
            "results": [
                {
                    "name": "Darth Vader",
                    "height": "202",
                    "url": "https://swapi.dev/api/people/4/"
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/",
            json=search_results,
            status=200
        )

        # Search for character
        search_result = await integration_client.search("people", "Vader")
        search_data = json.loads(search_result)

        assert search_data["count"] == 1
        character = search_data["results"][0]

        # Save to favorites
        await integration_db.add_favorite("person", 4, f"The villain: {character['name']}")

        # Search favorites by notes
        favorites_search = await integration_db.search_favorites("villain")
        favorites_data = json.loads(favorites_search)

        assert favorites_data["count"] == 1
        assert favorites_data["matches"][0]["id"] == 4

    @pytest.mark.asyncio
    async def test_database_persistence(self, integration_db):
        """Test that database operations persist across multiple operations"""
        # Add multiple favorites
        await integration_db.add_favorite("person", 1, "Luke Skywalker")
        await integration_db.add_favorite("person", 2, "C-3PO")
        await integration_db.add_favorite("planet", 1, "Tatooine")

        # Update one
        await integration_db.update_notes("person", 1, "Luke - Jedi Knight")

        # Remove one
        await integration_db.remove_favorite("person", 2)

        # List remaining favorites
        result = await integration_db.list_favorites()
        data = json.loads(result)

        assert data["count"] == 2

        # Verify the updated notes
        luke = next(f for f in data["favorites"] if f["id"] == 1 and f["type"] == "person")
        assert luke["notes"] == "Luke - Jedi Knight"
        assert "updated_at" in luke

    @pytest.mark.asyncio
    @responses.activate
    async def test_api_error_handling_in_workflow(self, integration_client, integration_db):
        """Test that API errors don't break the workflow"""
        # Mock a 404 response
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/999/",
            json={"detail": "Not found"},
            status=404
        )

        # Try to fetch non-existent person
        result = await integration_client.get_person(999)
        data = json.loads(result)

        # Should return error gracefully
        assert "error" in data
        assert data["error"] == "Not found"

        # Database should still work
        save_result = await integration_db.add_favorite("person", 1, "Valid entry")
        save_data = json.loads(save_result)

        assert save_data["success"] is True

    @pytest.mark.asyncio
    async def test_complex_filtering_workflow(self, integration_db):
        """Test complex filtering and querying scenarios"""
        # Add various favorites with different notes
        await integration_db.add_favorite("person", 1, "Luke - Jedi Master")
        await integration_db.add_favorite("person", 4, "Vader - Sith Lord")
        await integration_db.add_favorite("person", 3, "R2-D2 - Loyal droid")
        await integration_db.add_favorite("planet", 1, "Tatooine - Desert world")
        await integration_db.add_favorite("starship", 9, "Death Star - Ultimate weapon")

        # Filter by type
        people_result = await integration_db.list_favorites("person")
        people_data = json.loads(people_result)
        assert people_data["count"] == 3

        # Search for Jedi
        jedi_result = await integration_db.search_favorites("Jedi")
        jedi_data = json.loads(jedi_result)
        assert jedi_data["count"] == 1

        # Search for Sith
        sith_result = await integration_db.search_favorites("Sith")
        sith_data = json.loads(sith_result)
        assert sith_data["count"] == 1

        # Get all favorites
        all_result = await integration_db.list_favorites()
        all_data = json.loads(all_result)
        assert all_data["count"] == 5

    @pytest.mark.asyncio
    @responses.activate
    async def test_full_user_journey(self, integration_client, integration_db, sample_person_data):
        """Test a complete user journey through the system"""
        # Mock API responses
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            json=sample_person_data,
            status=200
        )

        # 1. User fetches a character
        person_result = await integration_client.get_person(1)
        person_data = json.loads(person_result)
        assert person_data["name"] == "Luke Skywalker"

        # 2. User likes the character and adds to favorites
        add_result = await integration_db.add_favorite(
            "person",
            1,
            "The main hero of the original trilogy"
        )
        assert json.loads(add_result)["success"] is True

        # 3. User lists their favorites
        list_result = await integration_db.list_favorites()
        list_data = json.loads(list_result)
        assert list_data["count"] == 1

        # 4. User updates notes with more information
        update_result = await integration_db.update_notes(
            "person",
            1,
            "Luke Skywalker - Son of Anakin, became a Jedi Master"
        )
        assert json.loads(update_result)["success"] is True

        # 5. User searches their notes
        search_result = await integration_db.search_favorites("Jedi Master")
        search_data = json.loads(search_result)
        assert search_data["count"] == 1

        # 6. User verifies the updated information
        final_list = await integration_db.list_favorites()
        final_data = json.loads(final_list)
        assert "Jedi Master" in final_data["favorites"][0]["notes"]
