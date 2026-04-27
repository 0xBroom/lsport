"""
Integration tests for portctl CLI commands
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, Mock

# Import the app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from portctl import app

runner = CliRunner()


class TestListCommand:
    """Test the list command"""

    @patch('portctl.get_open_ports')
    def test_list_no_ports(self, mock_get_ports):
        """Test list command when no ports are open"""
        mock_get_ports.return_value = []
        
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "No open ports found" in result.stdout

    @patch('portctl.get_open_ports')
    def test_list_with_ports(self, mock_get_ports):
        """Test list command with open ports"""
        mock_get_ports.return_value = [
            {
                'port': 8080,
                'pid': 1234,
                'name': 'test-app',
                'user': 'testuser',
                'status': 'LISTEN',
                'proto': 'TCP',
                'addr': '127.0.0.1',
            }
        ]
        
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "8080" in result.stdout
        assert "test-app" in result.stdout
        assert "LISTEN" in result.stdout

    @patch('portctl.get_open_ports')
    def test_list_with_state_filter(self, mock_get_ports):
        """Test list command with state filter"""
        mock_get_ports.return_value = []
        
        result = runner.invoke(app, ["list", "-s", "listen"])
        
        assert result.exit_code == 0
        mock_get_ports.assert_called_once_with(filter_state='listen')

    def test_list_with_invalid_state(self):
        """Test list command with invalid state"""
        result = runner.invoke(app, ["list", "-s", "invalid"])
        
        assert result.exit_code == 1
        assert "Unknown state" in result.stdout


class TestKillCommand:
    """Test the kill command"""

    @patch('portctl.kill_port')
    @patch('portctl.get_open_ports')
    def test_kill_no_process_on_port(self, mock_get_ports, mock_kill_port):
        """Test kill command when no process is on the port"""
        mock_get_ports.return_value = []
        
        result = runner.invoke(app, ["kill", "8080"])
        
        assert result.exit_code == 1
        assert "No process found" in result.stdout

    @patch('portctl.kill_port')
    @patch('portctl.get_open_ports')
    def test_kill_with_yes_flag(self, mock_get_ports, mock_kill_port):
        """Test kill command with --yes flag"""
        mock_get_ports.return_value = [
            {
                'port': 8080,
                'pid': 1234,
                'name': 'test-app',
                'user': 'testuser',
                'status': 'LISTEN',
                'proto': 'TCP',
                'addr': '127.0.0.1',
            }
        ]
        mock_kill_port.return_value = True
        
        result = runner.invoke(app, ["kill", "8080", "--yes"])
        
        assert result.exit_code == 0
        mock_kill_port.assert_called_once_with(8080, force=False)
        assert "Closed" in result.stdout

    @patch('portctl.kill_port')
    @patch('portctl.get_open_ports')
    def test_kill_with_force_flag(self, mock_get_ports, mock_kill_port):
        """Test kill command with --force flag"""
        mock_get_ports.return_value = [
            {
                'port': 8080,
                'pid': 1234,
                'name': 'test-app',
                'user': 'testuser',
                'status': 'LISTEN',
                'proto': 'TCP',
                'addr': '127.0.0.1',
            }
        ]
        mock_kill_port.return_value = True
        
        result = runner.invoke(app, ["kill", "8080", "--force", "--yes"])
        
        assert result.exit_code == 0
        mock_kill_port.assert_called_once_with(8080, force=True)

    @patch('portctl.kill_port')
    @patch('portctl.get_open_ports')
    def test_kill_cancelled(self, mock_get_ports, mock_kill_port):
        """Test kill command when user cancels"""
        mock_get_ports.return_value = [
            {
                'port': 8080,
                'pid': 1234,
                'name': 'test-app',
                'user': 'testuser',
                'status': 'LISTEN',
                'proto': 'TCP',
                'addr': '127.0.0.1',
            }
        ]
        
        # Simulate user saying "no" to confirmation
        result = runner.invoke(app, ["kill", "8080"], input="n\n")
        
        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_kill_port.assert_not_called()


class TestAppHelp:
    """Test help commands"""

    def test_main_help(self):
        """Test main help output"""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "portctl" in result.stdout
        assert "list" in result.stdout
        assert "kill" in result.stdout
        assert "interactive" in result.stdout

    def test_list_help(self):
        """Test list command help"""
        result = runner.invoke(app, ["list", "--help"])
        
        assert result.exit_code == 0
        assert "List open ports" in result.stdout

    def test_kill_help(self):
        """Test kill command help"""
        result = runner.invoke(app, ["kill", "--help"])
        
        assert result.exit_code == 0
        assert "Close the process" in result.stdout
