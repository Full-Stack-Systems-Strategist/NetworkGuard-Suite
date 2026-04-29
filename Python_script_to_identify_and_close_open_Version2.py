"""
Port Hardening & Service Management System

Identifies vulnerable network services on Windows systems and automatically
closes them through service termination and firewall rule creation.

This script targets high-risk remote access and RPC services that are
frequently exploited for lateral movement and privilege escalation.

Author: Full-Stack-Systems-Strategist
License: MIT
Version: 1.0.0
"""

import socket
import subprocess
import time
import os
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define ports to close
PORTS_TO_CLOSE = [135, 139, 445, 3389]

# Define services associated with ports
SERVICES = {
    135: 'rpcss',              # RPC Endpoint Mapper
    139: 'lanmanworkstation',  # NetBIOS Session Service
    445: 'lanmanserver',       # SMB over TCP
    3389: 'termservice'        # Remote Desktop Protocol
}

# Port descriptions for logging
PORT_DESCRIPTIONS = {
    135: 'RPC Endpoint Mapper',
    139: 'NetBIOS Session Service (SMB)',
    445: 'Server Message Block (SMB)',
    3389: 'Remote Desktop Protocol (RDP)'
}

def scan_port(host, port):
    """
    Check if a network port is open on localhost.
    
    Attempts to establish a TCP connection to the specified port.
    Returns True if successful, False otherwise.
    
    Args:
        host (str): Host address to scan (typically '127.0.0.1')
        port (int): Port number to scan
        
    Returns:
        bool: True if port is open, False if closed
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True
        else:
            return False
    except socket.error as e:
        logging.error(f"Error scanning port {port}: {e}")
        return False

def stop_service(service):
    """
    Stop a Windows service.
    
    Attempts to stop the specified Windows service using 'net stop' command.
    Requires administrator privileges.
    
    Args:
        service (str): Windows service name to stop
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        subprocess.check_call(
            f"net stop {service}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logging.info(f"Service '{service}' stopped successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.warning(f"Service '{service}' not running or failed to stop: {e}")
        return False
    except Exception as e:
        logging.error(f"Error stopping service '{service}': {e}")
        return False

def add_firewall_rule(port):
    """
    Create Windows Firewall rule to block inbound traffic on port.
    
    Uses netsh to create an inbound firewall rule that blocks TCP traffic
    to the specified port. Rules are persistent across reboots.
    
    Args:
        port (int): Port number to block
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        rule_name = f"BlockPort{port}"
        subprocess.check_call(
            f"netsh advfirewall firewall add rule "
            f"name={rule_name} "
            f"dir=in "
            f"action=block "
            f"protocol=TCP "
            f"localport={port}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logging.info(f"Firewall rule '{rule_name}' created for port {port}")
        return True
    except subprocess.CalledProcessError as e:
        logging.warning(f"Firewall rule for port {port} may already exist")
        return False
    except Exception as e:
        logging.error(f"Error adding firewall rule for port {port}: {e}")
        return False

def close_ports():
    """
    Main function: Scan and close all vulnerable ports.
    
    Iterates through PORTS_TO_CLOSE:
    1. Scans port status
    2. Stops associated service if port is open
    3. Creates firewall rule to block port
    4. Logs results for each port
    """
    logging.info(f"Starting port hardening scan on {len(PORTS_TO_CLOSE)} ports")
    logging.info("=" * 60)
    
    closed_count = 0
    already_closed_count = 0
    failed_count = 0
    
    for port in PORTS_TO_CLOSE:
        port_desc = PORT_DESCRIPTIONS.get(port, "Unknown Service")
        
        logging.info(f"\nProcessing Port {port} ({port_desc})")
        logging.info("-" * 60)
        
        # Check if port is open
        if scan_port('127.0.0.1', port):
            logging.info(f"  Status: Port {port} is OPEN")
            
            # Stop associated service
            if port in SERVICES:
                service_name = SERVICES[port]
                logging.info(f"  Action: Stopping service '{service_name}'")
                stop_service(service_name)
            
            # Add firewall rule
            logging.info(f"  Action: Adding firewall block rule for port {port}")
            if add_firewall_rule(port):
                logging.warning(f"  ✓ Port {port} CLOSED successfully")
                closed_count += 1
            else:
                logging.error(f"  ✗ Port {port} FAILED to close")
                failed_count += 1
        else:
            logging.info(f"  Status: Port {port} is already CLOSED")
            already_closed_count += 1
    
    # Summary
    logging.info("\n" + "=" * 60)
    logging.info("PORT HARDENING SUMMARY")
    logging.info("=" * 60)
    logging.info(f"Successfully Closed:  {closed_count}")
    logging.info(f"Already Closed:       {already_closed_count}")
    logging.info(f"Failed to Close:      {failed_count}")
    logging.info(f"Total Scanned:        {len(PORTS_TO_CLOSE)}")
    logging.info("=" * 60)

def verify_rules():
    """
    Verify created firewall rules exist.
    
    Lists all firewall rules matching the BlockPort* pattern
    to confirm they were created successfully.
    """
    try:
        logging.info("\nVerifying firewall rules...")
        subprocess.call(
            f'netsh advfirewall firewall show rule name="BlockPort*"',
            shell=True
        )
    except Exception as e:
        logging.error(f"Error verifying rules: {e}")

def main():
    """
    Application entry point.
    
    Requires administrator privileges to:
    - Stop Windows services
    - Create firewall rules
    """
    try:
        # Check for admin privileges
        if os.name == 'nt':  # Windows
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    logging.error("ERROR: This script requires administrator privileges!")
                    logging.error("Please run Command Prompt or PowerShell as Administrator")
                    sys.exit(1)
            except:
                logging.warning("Could not verify administrator status")
        
        logging.info("=" * 60)
        logging.info("NetworkGuard - Port Hardening Module")
        logging.info("=" * 60)
        
        # Run port hardening
        close_ports()
        
        # Verify rules
        verify_rules()
        
        logging.info("\nPort hardening complete!")
        
    except KeyboardInterrupt:
        logging.info("Port hardening cancelled by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()