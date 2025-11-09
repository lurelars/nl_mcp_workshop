"""
Unit tests for the SWAPI Client module
"""

import pytest
import json
import responses
from src.swapi_client import SWAPIClient


class TestSWAPIClient:
    """Test suite for SWAPIClient class"""

    @pytest.mark.asyncio
    @responses.activate
    async def test_get_person_success(self, swapi_client, sample_person_data):
        """Test successfully fetching a person"""
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            json=sample_person_data,
            status=200
        )

        result = await swapi_client.get_person(1)
        result_data = json.loads(result)

        assert result_data["name"] == "Luke Skywalker"
        assert result_data["height"] == "172"
        assert result_data["gender"] == "male"

    @pytest.mark.asyncio
    @responses.activate
    async def test_get_person_not_found(self, swapi_client):
        """Test fetching a non-existent person"""
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/999/",
            json={"detail": "Not found"},
            status=404
        )

        result = await swapi_client.get_person(999)
        result_data = json.loads(result)

        assert "error" in result_data
        assert result_data["error"] == "Not found"
        assert "does not exist" in result_data["message"]

    @pytest.mark.asyncio
    @responses.activate
    async def test_get_planet_success(self, swapi_client, sample_planet_data):
        """Test successfully fetching a planet"""
        responses.add(
            responses.GET,
            "https://swapi.dev/api/planets/1/",
            json=sample_planet_data,
            status=200
        )

        result = await swapi_client.get_planet(1)
        result_data = json.loads(result)

        assert result_data["name"] == "Tatooine"
        assert result_data["climate"] == "arid"
        assert result_data["terrain"] == "desert"

    @pytest.mark.asyncio
    @responses.activate
    async def test_get_starship_success(self, swapi_client):
        """Test successfully fetching a starship"""
        starship_data = {
            "name": "Millennium Falcon",
            "model": "YT-1300 light freighter",
            "manufacturer": "Corellian Engineering Corporation",
            "length": "34.37",
            "crew": "4",
            "passengers": "6"
        }

        responses.add(
            responses.GET,
            "https://swapi.dev/api/starships/10/",
            json=starship_data,
            status=200
        )

        result = await swapi_client.get_starship(10)
        result_data = json.loads(result)

        assert result_data["name"] == "Millennium Falcon"
        assert result_data["model"] == "YT-1300 light freighter"

    @pytest.mark.asyncio
    @responses.activate
    async def test_get_film_success(self, swapi_client):
        """Test successfully fetching a film"""
        film_data = {
            "title": "A New Hope",
            "episode_id": 4,
            "director": "George Lucas",
            "producer": "Gary Kurtz, Rick McCallum",
            "release_date": "1977-05-25"
        }

        responses.add(
            responses.GET,
            "https://swapi.dev/api/films/1/",
            json=film_data,
            status=200
        )

        result = await swapi_client.get_film(1)
        result_data = json.loads(result)

        assert result_data["title"] == "A New Hope"
        assert result_data["episode_id"] == 4
        assert result_data["director"] == "George Lucas"

    @pytest.mark.asyncio
    @responses.activate
    async def test_http_error_500(self, swapi_client):
        """Test handling of server errors"""
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            json={"error": "Internal Server Error"},
            status=500
        )

        result = await swapi_client.get_person(1)
        result_data = json.loads(result)

        assert "error" in result_data
        assert result_data["error"] == "HTTP error"
        assert result_data["status_code"] == 500

    @pytest.mark.asyncio
    @responses.activate
    async def test_search_success(self, swapi_client):
        """Test searching for resources"""
        search_results = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "name": "Luke Skywalker",
                    "height": "172",
                    "mass": "77"
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/",
            json=search_results,
            status=200
        )

        result = await swapi_client.search("people", "Luke")
        result_data = json.loads(result)

        assert result_data["count"] == 1
        assert result_data["results"][0]["name"] == "Luke Skywalker"

    @pytest.mark.asyncio
    @responses.activate
    async def test_search_no_results(self, swapi_client):
        """Test searching with no matches"""
        search_results = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": []
        }

        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/",
            json=search_results,
            status=200
        )

        result = await swapi_client.search("people", "NonexistentCharacter")
        result_data = json.loads(result)

        assert result_data["count"] == 0
        assert result_data["results"] == []

    @pytest.mark.asyncio
    @responses.activate
    async def test_connection_error(self, swapi_client):
        """Test handling of connection errors"""
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            body=Exception("Connection refused")
        )

        result = await swapi_client.get_person(1)
        result_data = json.loads(result)

        assert "error" in result_data

    @pytest.mark.asyncio
    @responses.activate
    async def test_multiple_endpoints(self, swapi_client, sample_person_data, sample_planet_data):
        """Test fetching from multiple endpoints"""
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

        person_result = await swapi_client.get_person(1)
        planet_result = await swapi_client.get_planet(1)

        person_data = json.loads(person_result)
        planet_data = json.loads(planet_result)

        assert person_data["name"] == "Luke Skywalker"
        assert planet_data["name"] == "Tatooine"

    @pytest.mark.asyncio
    @responses.activate
    async def test_json_parsing_error(self, swapi_client):
        """Test handling of invalid JSON response"""
        responses.add(
            responses.GET,
            "https://swapi.dev/api/people/1/",
            body="Invalid JSON {{{",
            status=200,
            content_type="application/json"
        )

        result = await swapi_client.get_person(1)
        result_data = json.loads(result)

        assert "error" in result_data
