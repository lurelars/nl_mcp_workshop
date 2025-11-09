"""
Star Wars API (SWAPI) Client

Handles all interactions with the Star Wars API at https://swapi.dev/api/
"""

import requests
import json
from typing import Dict, Any, Optional


class SWAPIClient:
    """Client for interacting with the Star Wars API (SWAPI)"""

    BASE_URL = "https://swapi.dev/api"

    def __init__(self):
        """Initialize the SWAPI client"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MCP-Workshop-Client/1.0"
        })

    async def _fetch(self, endpoint: str, resource_id: int) -> str:
        """
        Generic fetch method for SWAPI resources.

        Args:
            endpoint: The API endpoint (e.g., 'people', 'planets')
            resource_id: The ID of the resource to fetch

        Returns:
            JSON string of the resource data

        Raises:
            Exception: If the API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}/{resource_id}/"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            return json.dumps(data, indent=2)

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return json.dumps({
                    "error": "Not found",
                    "message": f"{endpoint.capitalize()} with ID {resource_id} does not exist"
                })
            else:
                return json.dumps({
                    "error": "HTTP error",
                    "message": str(e),
                    "status_code": response.status_code
                })

        except requests.exceptions.RequestException as e:
            return json.dumps({
                "error": "Request failed",
                "message": f"Failed to fetch data from SWAPI: {str(e)}"
            })

        except Exception as e:
            return json.dumps({
                "error": "Unexpected error",
                "message": str(e)
            })

    async def get_person(self, person_id: int) -> str:
        """
        Get information about a Star Wars character.

        Args:
            person_id: The ID of the character (1-83)

        Returns:
            JSON string containing character information including:
            - name, height, mass, hair_color, skin_color, eye_color
            - birth_year, gender
            - homeworld, films, species, vehicles, starships
        """
        return await self._fetch("people", person_id)

    async def get_planet(self, planet_id: int) -> str:
        """
        Get information about a Star Wars planet.

        Args:
            planet_id: The ID of the planet (1-60)

        Returns:
            JSON string containing planet information including:
            - name, rotation_period, orbital_period
            - diameter, climate, gravity, terrain
            - surface_water, population
            - residents, films
        """
        return await self._fetch("planets", planet_id)

    async def get_starship(self, starship_id: int) -> str:
        """
        Get information about a Star Wars starship.

        Args:
            starship_id: The ID of the starship

        Returns:
            JSON string containing starship information including:
            - name, model, manufacturer, cost_in_credits
            - length, max_atmosphering_speed, crew, passengers
            - cargo_capacity, consumables, hyperdrive_rating
            - MGLT, starship_class
            - pilots, films
        """
        return await self._fetch("starships", starship_id)

    async def get_film(self, film_id: int) -> str:
        """
        Get information about a Star Wars film.

        Args:
            film_id: The ID of the film (1-6)

        Returns:
            JSON string containing film information including:
            - title, episode_id, opening_crawl
            - director, producer, release_date
            - characters, planets, starships, vehicles, species
        """
        return await self._fetch("films", film_id)

    async def search(self, endpoint: str, query: str) -> str:
        """
        Search for resources in SWAPI.

        Args:
            endpoint: The API endpoint to search (e.g., 'people', 'planets')
            query: The search query string

        Returns:
            JSON string containing search results
        """
        url = f"{self.BASE_URL}/{endpoint}/"

        try:
            response = self.session.get(url, params={"search": query}, timeout=10)
            response.raise_for_status()

            data = response.json()
            return json.dumps(data, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({
                "error": "Search failed",
                "message": f"Failed to search SWAPI: {str(e)}"
            })

        except Exception as e:
            return json.dumps({
                "error": "Unexpected error",
                "message": str(e)
            })
