"""
Unit tests for portctl core functionality
"""

import os

# Import functions from portctl
import sys
from unittest.mock import Mock, patch

import psutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from portctl import VALID_STATES, get_open_ports, kill_port, status_color


class TestGetOpenPorts:
    """Test the get_open_ports function"""

    @patch("portctl.psutil.process_iter")
    def test_get_open_ports_basic(self, mock_process_iter):
        """Test basic port listing"""
        # Create mock process
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.info = {"name": "test-app", "username": "testuser"}

        # Create mock connection
        mock_conn = Mock()
        mock_conn.laddr = Mock(port=8080, ip="127.0.0.1")
        mock_conn.status = "LISTEN"

        mock_proc.net_connections.return_value = [mock_conn]
        mock_process_iter.return_value = [mock_proc]

        # Test
        ports = get_open_ports()

        mock_proc.net_connections.assert_called_once_with(kind="tcp")
        assert len(ports) == 1
        assert ports[0]["port"] == 8080
        assert ports[0]["pid"] == 1234
        assert ports[0]["name"] == "test-app"
        assert ports[0]["user"] == "testuser"
        assert ports[0]["status"] == "LISTEN"
        assert ports[0]["proto"] == "TCP"

    @patch("portctl.psutil.process_iter")
    def test_get_open_ports_filter_by_port(self, mock_process_iter):
        """Test filtering by specific port"""
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.info = {"name": "test-app", "username": "testuser"}

        mock_conn1 = Mock()
        mock_conn1.laddr = Mock(port=8080, ip="127.0.0.1")
        mock_conn1.status = "LISTEN"

        mock_conn2 = Mock()
        mock_conn2.laddr = Mock(port=3000, ip="127.0.0.1")
        mock_conn2.status = "LISTEN"

        mock_proc.net_connections.return_value = [mock_conn1, mock_conn2]
        mock_process_iter.return_value = [mock_proc]

        # Test filtering
        ports = get_open_ports(filter_port=8080)

        assert len(ports) == 1
        assert ports[0]["port"] == 8080

    @patch("portctl.psutil.process_iter")
    def test_get_open_ports_filter_by_state(self, mock_process_iter):
        """Test filtering by connection state"""
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.info = {"name": "test-app", "username": "testuser"}

        mock_conn_listen = Mock()
        mock_conn_listen.laddr = Mock(port=8080, ip="127.0.0.1")
        mock_conn_listen.status = "LISTEN"

        mock_conn_established = Mock()
        mock_conn_established.laddr = Mock(port=3000, ip="127.0.0.1")
        mock_conn_established.status = "ESTABLISHED"

        mock_proc.net_connections.return_value = [mock_conn_listen, mock_conn_established]
        mock_process_iter.return_value = [mock_proc]

        # Test state filtering
        ports = get_open_ports(filter_state="listen")

        assert len(ports) == 1
        assert ports[0]["status"] == "LISTEN"

    @patch("portctl.psutil.process_iter")
    def test_get_open_ports_handles_no_such_process(self, mock_process_iter):
        """Test that NoSuchProcess exceptions are handled gracefully"""
        mock_proc = Mock()
        mock_proc.net_connections.side_effect = psutil.NoSuchProcess(123)
        mock_process_iter.return_value = [mock_proc]

        # Should not raise exception
        ports = get_open_ports()
        assert len(ports) == 0

    @patch("portctl.psutil.process_iter")
    def test_get_open_ports_handles_access_denied(self, mock_process_iter):
        """Test that AccessDenied exceptions are handled gracefully"""
        mock_proc = Mock()
        mock_proc.net_connections.side_effect = psutil.AccessDenied()
        mock_process_iter.return_value = [mock_proc]

        # Should not raise exception
        ports = get_open_ports()
        assert len(ports) == 0

    @patch("portctl.psutil.process_iter")
    def test_get_open_ports_sorts_by_port(self, mock_process_iter):
        """Test that results are sorted by port number"""
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.info = {"name": "test-app", "username": "testuser"}

        # Create connections with unsorted ports
        conns = []
        for port in [9000, 3000, 8080]:
            mock_conn = Mock()
            mock_conn.laddr = Mock(port=port, ip="127.0.0.1")
            mock_conn.status = "LISTEN"
            conns.append(mock_conn)

        mock_proc.net_connections.return_value = conns
        mock_process_iter.return_value = [mock_proc]

        ports = get_open_ports()

        assert len(ports) == 3
        assert ports[0]["port"] == 3000
        assert ports[1]["port"] == 8080
        assert ports[2]["port"] == 9000


class TestStatusColor:
    """Test the status_color function"""

    def test_listen_state_color(self):
        assert status_color("LISTEN") == "green"

    def test_established_state_color(self):
        assert status_color("ESTABLISHED") == "cyan"

    def test_close_wait_state_color(self):
        assert status_color("CLOSE_WAIT") == "yellow"

    def test_unknown_state_color(self):
        assert status_color("UNKNOWN") == "white"


class TestKillPort:
    """Test the kill_port function"""

    @patch("portctl.os.kill")
    @patch("portctl.psutil.process_iter")
    def test_kill_port_success(self, mock_process_iter, mock_os_kill):
        """Test successfully killing a process on a port"""
        mock_proc = Mock()
        mock_proc.pid = 1234

        mock_conn = Mock()
        mock_conn.laddr = Mock(port=8080)

        mock_proc.net_connections.return_value = [mock_conn]
        mock_process_iter.return_value = [mock_proc]

        result = kill_port(8080)

        assert result is True
        mock_os_kill.assert_called_once()

    @patch("portctl.psutil.process_iter")
    def test_kill_port_not_found(self, mock_process_iter):
        """Test killing a port that doesn't exist"""
        mock_process_iter.return_value = []

        result = kill_port(9999)

        assert result is False

    @patch("portctl.os.kill")
    @patch("portctl.psutil.process_iter")
    def test_kill_port_with_force(self, mock_process_iter, mock_os_kill):
        """Test force killing with SIGKILL"""
        import signal

        mock_proc = Mock()
        mock_proc.pid = 1234

        mock_conn = Mock()
        mock_conn.laddr = Mock(port=8080)

        mock_proc.net_connections.return_value = [mock_conn]
        mock_process_iter.return_value = [mock_proc]

        result = kill_port(8080, force=True)

        assert result is True
        mock_os_kill.assert_called_with(1234, signal.SIGKILL)


class TestValidStates:
    """Test VALID_STATES constant"""

    def test_valid_states_tuple(self):
        assert isinstance(VALID_STATES, tuple)
        assert "LISTEN" in VALID_STATES
        assert "ESTABLISHED" in VALID_STATES
        assert "CLOSE_WAIT" in VALID_STATES
