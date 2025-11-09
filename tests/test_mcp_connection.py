"""
MCP Connection Tests

Tests to verify that the MCP server can be properly invoked and responds correctly.
This simulates how Claude Code would interact with the server.
"""

import pytest
import json
import subprocess
import time
import signal
from pathlib import Path


class TestMCPConnection:
    """Test MCP server connection and communication"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def server_path(self, project_root):
        """Get path to MCP server"""
        return project_root / "src" / "mcp_server.py"

    def test_server_file_exists(self, server_path):
        """Test that the MCP server file exists"""
        assert server_path.exists(), f"MCP server not found at {server_path}"

    def test_server_imports(self, project_root):
        """Test that server can import required modules"""
        import sys
        sys.path.insert(0, str(project_root / "src"))

        try:
            from swapi_client import SWAPIClient
            from database import Database
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import required modules: {e}")

    def test_server_can_start(self, server_path, project_root):
        """Test that the server can be started (basic smoke test)"""
        # This test checks if the server file is executable and has no syntax errors
        result = subprocess.run(
            ["python", "-m", "py_compile", str(server_path)],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )

        assert result.returncode == 0, f"Server has syntax errors: {result.stderr}"

    @pytest.mark.asyncio
    async def test_client_initialization(self, project_root):
        """Test that SWAPI client can be initialized"""
        import sys
        sys.path.insert(0, str(project_root / "src"))

        from swapi_client import SWAPIClient

        client = SWAPIClient()
        assert client is not None
        assert client.BASE_URL == "https://swapi.dev/api"

    @pytest.mark.asyncio
    async def test_database_initialization(self, project_root):
        """Test that database can be initialized"""
        import sys
        sys.path.insert(0, str(project_root / "src"))
        import tempfile

        from database import Database

        # Create temporary database
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump({"favorites": []}, f)

        db = Database(db_path=temp_path)
        assert db is not None

        # Verify database is readable
        result = await db.list_favorites()
        data = json.loads(result)
        assert data["count"] == 0

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_mcp_config_exists(self, project_root):
        """Test that MCP configuration file exists"""
        config_path = project_root / "config" / "mcp_config.json"
        assert config_path.exists(), "MCP config file not found"

        # Verify it's valid JSON
        with open(config_path) as f:
            config = json.load(f)
            assert "mcpServers" in config or "settings" in config

    def test_database_file_exists(self, project_root):
        """Test that database file exists and is valid"""
        db_path = project_root / "data" / "local_db.json"
        assert db_path.exists(), "Database file not found"

        # Verify it's valid JSON
        with open(db_path) as f:
            data = json.load(f)
            assert "favorites" in data
            assert isinstance(data["favorites"], list)

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, project_root):
        """Test a complete end-to-end workflow"""
        import sys
        sys.path.insert(0, str(project_root / "src"))
        import tempfile

        from swapi_client import SWAPIClient
        from database import Database

        # Create temporary database
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump({"favorites": []}, f)

        try:
            client = SWAPIClient()
            db = Database(db_path=temp_path)

            # Fetch from API
            person_result = await client.get_person(1)
            person_data = json.loads(person_result)
            assert "name" in person_data

            # Save to database
            save_result = await db.add_favorite("person", 1, "Test character")
            save_data = json.loads(save_result)
            assert save_data.get("success") is True

            # List favorites
            list_result = await db.list_favorites()
            list_data = json.loads(list_result)
            assert list_data["count"] == 1

            # Search favorites
            search_result = await db.search_favorites("Test")
            search_data = json.loads(search_result)
            assert search_data["count"] == 1

            # Remove favorite
            remove_result = await db.remove_favorite("person", 1)
            remove_data = json.loads(remove_result)
            assert remove_data.get("success") is True

            # Verify removed
            final_list = await db.list_favorites()
            final_data = json.loads(final_list)
            assert final_data["count"] == 0

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_python_environment(self):
        """Test that required packages are available"""
        try:
            import fastmcp
            import requests
            assert True
        except ImportError as e:
            pytest.fail(f"Required package not installed: {e}")


class TestMCPServerStructure:
    """Test the structure of the MCP server"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    def test_src_directory_exists(self, project_root):
        """Test that src directory exists"""
        assert (project_root / "src").exists()

    def test_required_files_exist(self, project_root):
        """Test that all required files exist"""
        required_files = [
            "src/mcp_server.py",
            "src/swapi_client.py",
            "src/database.py",
            "src/__init__.py",
            "data/local_db.json",
            "config/mcp_config.json",
            "requirements.txt",
            "setup.py"
        ]

        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file not found: {file_path}"

    def test_test_directory_structure(self, project_root):
        """Test that test directory is properly structured"""
        test_files = [
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/test_database.py",
            "tests/test_swapi_client.py",
            "tests/test_integration.py"
        ]

        for file_path in test_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Test file not found: {file_path}"
