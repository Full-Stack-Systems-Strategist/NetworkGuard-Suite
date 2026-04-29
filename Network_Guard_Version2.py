"""
Network_Guard.py - ARP Spoofing Detection & Mitigation System

This module provides real-time monitoring and automatic response to ARP-based attacks.
It maintains static ARP entries for critical network hosts and integrates with optional
honeypot systems for threat collection and analysis.

Author: Full-Stack-Systems-Strategist
License: MIT
Version: 1.0.0
"""

import subprocess
import threading
from scapy.all import srp1, Ether, ARP, sniff, get_if_addr, getmacbyip, conf, srp
import os
import logging
import time
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NetworkGuard:
    """
    ARP Spoofing Detection and Prevention System
    
    Monitors network traffic for ARP anomalies and automatically responds to detected attacks.
    Maintains static ARP bindings to prevent cache poisoning of critical network infrastructure.
    """
    
    def __init__(self):
        """Initialize NetworkGuard with gateway configuration and monitoring."""
        self.gateway_ip = '192.168.1.1'  # ← CONFIGURE FOR YOUR NETWORK
        self.gateway_mac = '50:42:89:4A:F8:94'  # ← CONFIGURE FOR YOUR NETWORK
        self.set_static_arp()
        
        # Import and initialize the honeypot bridge (optional)
        try:
            from arp_honeypot_bridge import ARPHoneypotBridge
            self.honeypot = ARPHoneypotBridge()
            logging.info("Honeypot bridge initialized")
        except ImportError:
            logging.warning("Could not import honeypot bridge module")
            self.honeypot = None
        
        # Start packet sniffer in background thread
        sniffer_thread = threading.Thread(target=self.start_sniffer)
        sniffer_thread.daemon = True
        sniffer_thread.start()

    def get_mac(self, ip_address):
        """
        Retrieve MAC address for a given IP using ARP resolution.
        
        Args:
            ip_address (str): Target IP address
            
        Returns:
            str: MAC address if found, None otherwise
        """
        result = srp1(
            Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address),
            timeout=1,
            verbose=False
        )
        if result:
            return result.hwsrc
        else:
            return None

    def send_arp_request(self, ip):
        """
        Send ARP request and collect responses.
        
        Args:
            ip (str): Target IP address
            
        Returns:
            list: ARP responses
        """
        arp = ARP(pdst=ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        result = srp(packet, timeout=3, verbose=0)[0]
        return result

    def set_static_arp(self):
        """
        Create static ARP entry for gateway to prevent cache poisoning.
        Uses Windows netsh command to bind gateway IP to known MAC address.
        """
        try:
            interface_name = str(conf.iface)
            subprocess.check_output([
                'netsh',
                'interface',
                'ip',
                'add',
                'neighbors',
                interface_name,
                self.gateway_ip,
                self.gateway_mac
            ])
            logging.info(f"Static ARP entry set for {self.gateway_ip}")
        except subprocess.CalledProcessError:
            logging.debug('ARP entry for gateway already exists')
        except Exception as e:
            logging.info(f"Failed to set static ARP: {str(e)}")
            time.sleep(2)

    def detect_arp_spoofing(self, packet):
        """
        Analyze packet for ARP spoofing indicators.
        
        Triggers on ARP responses claiming to be the gateway but with
        a different MAC address than the known gateway MAC.
        
        Args:
            packet: Scapy packet object
        """
        if packet.haslayer(ARP):
            if packet[ARP].op == 2:  # ARP response (op code 2)
                # Check if response claims to be from gateway but has wrong MAC
                if packet[ARP].psrc == self.gateway_ip and packet[ARP].hwsrc != self.gateway_mac:
                    attacker_mac = packet[ARP].hwsrc
                    
                    # Log the attack
                    logging.warning(
                        f'ARP spoofing attempt detected from {attacker_mac}! '
                        f'Claiming to be gateway {self.gateway_ip}'
                    )
                    
                    # System alert
                    print("\a")  # System beep for immediate attention
                    
                    # Restore ARP cache
                    self.restore_arp_cache()
                    
                    # Bridge attacker to honeypot if available
                    if self.honeypot:
                        try:
                            from arp_honeypot_bridge import ARPHoneypotBridge
                            client_id = self.honeypot.register_attacker_with_c2(
                                packet[ARP].psrc,
                                attacker_mac
                            )
                            if client_id:
                                logging.info(
                                    f"Automatically bridged attacker {packet[ARP].psrc} "
                                    f"to C2 server with client ID {client_id}"
                                )
                        except Exception as e:
                            logging.error(f"Failed to bridge attacker to C2: {str(e)}")

    def restore_arp_cache(self):
        """
        Remove poisoned ARP entry and restore static binding.
        
        Flushes the ARP cache entry for the gateway and re-establishes
        the static ARP binding with the known-good MAC address.
        """
        try:
            interface_name = str(conf.iface)
            subprocess.check_output([
                'netsh',
                'interface',
                'ip',
                'delete',
                'neighbors',
                interface_name,
                self.gateway_ip
            ])
            logging.info(f"Flushed ARP entry for {self.gateway_ip}")
            self.set_static_arp()
        except Exception as e:
            logging.error(f"Failed to restore ARP cache: {str(e)}")

    def start_sniffer(self):
        """
        Start packet sniffer in continuous mode.
        
        Sniffs ARP packets and passes each to detect_arp_spoofing for analysis.
        Runs indefinitely until application exit.
        """
        logging.info("ARP sniffer started")
        sniff(prn=self.detect_arp_spoofing, filter='arp', store=False)

    def run(self):
        """
        Main application loop.
        
        Keeps the application running indefinitely, allowing background
        threads to continue monitoring.
        """
        logging.info("NetworkGuard started - monitoring for ARP spoofing attacks")
        try:
            while True:
                time.sleep(1)
                time.sleep(10)
        except KeyboardInterrupt:
            logging.info("NetworkGuard stopped by user")
            sys.exit(0)

if __name__ == '__main__':
    network_guard = NetworkGuard()
    network_guard.run()