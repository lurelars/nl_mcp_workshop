"""
Pytest configuration and shared fixtures
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.database import Database
from src.swapi_client import SWAPIClient


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
        json.dump({"favorites": []}, f)

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def database(temp_db):
    """Create a Database instance with temporary storage"""
    return Database(db_path=temp_db)


@pytest.fixture
def swapi_client():
    """Create a SWAPI client instance"""
    return SWAPIClient()


@pytest.fixture
def sample_person_data():
    """Sample person data from SWAPI"""
    return {
        "name": "Luke Skywalker",
        "height": "172",
        "mass": "77",
        "hair_color": "blond",
        "skin_color": "fair",
        "eye_color": "blue",
        "birth_year": "19BBY",
        "gender": "male",
        "homeworld": "https://swapi.dev/api/planets/1/",
        "films": [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/2/",
            "https://swapi.dev/api/films/3/",
            "https://swapi.dev/api/films/6/"
        ],
        "species": [],
        "vehicles": [
            "https://swapi.dev/api/vehicles/14/",
            "https://swapi.dev/api/vehicles/30/"
        ],
        "starships": [
            "https://swapi.dev/api/starships/12/",
            "https://swapi.dev/api/starships/22/"
        ],
        "created": "2014-12-09T13:50:51.644000Z",
        "edited": "2014-12-20T21:17:56.891000Z",
        "url": "https://swapi.dev/api/people/1/"
    }


@pytest.fixture
def sample_planet_data():
    """Sample planet data from SWAPI"""
    return {
        "name": "Tatooine",
        "rotation_period": "23",
        "orbital_period": "304",
        "diameter": "10465",
        "climate": "arid",
        "gravity": "1 standard",
        "terrain": "desert",
        "surface_water": "1",
        "population": "200000",
        "residents": [
            "https://swapi.dev/api/people/1/",
            "https://swapi.dev/api/people/2/"
        ],
        "films": [
            "https://swapi.dev/api/films/1/",
            "https://swapi.dev/api/films/3/"
        ],
        "created": "2014-12-09T13:50:49.641000Z",
        "edited": "2014-12-20T20:58:18.411000Z",
        "url": "https://swapi.dev/api/planets/1/"
    }
