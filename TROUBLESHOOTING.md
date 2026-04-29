# Troubleshooting Guide - NetworkGuard-Suite

## Common Issues & Solutions

### 1. Permission Denied Errors

**Symptoms:**
```
PermissionError: [WinError 5] Access is denied
```

**Cause:** Scripts require administrator/SYSTEM level privileges

**Solutions:**
1. Run Command Prompt as Administrator:
   - Press `Win + X` → Select "Command Prompt (Admin)" or "PowerShell (Admin)"
   - Navigate to script directory
   - Run: `python script_name.py`

2. Create batch file wrapper (save as `run_as_admin.bat`):
   ```batch
   @echo off
   cd /d %~dp0
   python Network_Guard.py
   pause
   ```
   - Right-click → "Run as administrator"

3. Check current privilege level:
   ```bash
   whoami /priv
   ```
   - Should show multiple privileges including `SeDebugPrivilege`

---

### 2. "Network is Unreachable" / Adapter Errors

**Symptoms:**
```
No such device exists
Error binding to interface
```

**Cause:** Network interface not properly configured or detected

**Solutions:**
1. Verify network adapter:
   ```bash
   ipconfig /all
   # Look for "Ethernet adapter" or "WiFi" with IPv4 address
   ```

2. Check Scapy interface:
   ```bash
   python -c "from scapy.all import conf; print(conf.iface)"
   ```

3. List all interfaces:
   ```bash
   python -c "from scapy.all import get_windows_if_list; print(get_windows_if_list())"
   ```

4. Set interface explicitly in code:
   ```python
   from scapy.all import conf
   conf.iface = "Ethernet"  # or "WiFi" or specific interface name
   ```

---

### 3. Module Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'scapy'
ImportError: cannot import name 'srp'
```

**Cause:** Dependencies not installed

**Solutions:**
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. If pip not in PATH:
   ```bash
   python -m pip install scapy
   ```

3. Install specific version:
   ```bash
   pip install scapy==2.4.5
   ```

4. Verify installation:
   ```bash
   python -c "from scapy.all import *; print('Scapy OK')"
   ```

---

### 4. Honeypot Module Not Found

**Symptoms:**
```
WARNING - Could not import honeypot bridge module
```

**Cause:** Optional `arp_honeypot_bridge.py` not present

**Status:** ✓ Not critical - NetworkGuard continues without it

**Solution:** If honeypot integration needed:
1. Place `arp_honeypot_bridge.py` in project root directory
2. Ensure it implements `ARPHoneypotBridge` class with `register_attacker_with_c2()` method
3. Restart Network_Guard

---

### 5. ARP Spoofing Not Detected

**Symptoms:**
- Network_Guard running but no alerts
- ARP attacks not being detected

**Causes & Solutions:**

1. **Wrong gateway configuration:**
   ```bash
   # Verify gateway
   ipconfig /all
   # Find "Default Gateway"
   
   # Check gateway MAC
   arp -a
   # Find gateway IP, note Physical Address
   ```
   Update in Network_Guard.py:
   ```python
   self.gateway_ip = '192.168.X.X'        # Your actual gateway
   self.gateway_mac = 'AA:BB:CC:DD:EE:FF' # Your actual MAC
   ```

2. **Static ARP entry not set:**
   ```bash
   # Verify static entry
   arp -a
   # Look for "Static" entries
   
   # Check manually
   netsh interface ip show neighbors
   ```

3. **Sniffer not capturing traffic:**
   - Ensure network is active
   - Check firewall isn't blocking Scapy
   - Verify ARP filter is working:
   ```bash
   python -c "from scapy.all import sniff; sniff(filter='arp', count=5)"
   # Should show ARP packets if network has ARP traffic
   ```

4. **Wrong network interface:**
   - Network_Guard might be sniffing wrong adapter
   - Update interface in code:
   ```python
   from scapy.all import conf
   conf.iface = "Ethernet"  # Use your correct interface
   ```

---

### 6. Port Not Closing After Script Runs

**Symptoms:**
```
Port 445 closed successfully (message shows)
But port still responds to scans
```

**Causes & Solutions:**

1. **Service didn't stop properly:**
   ```bash
   # Check service status
   sc query rpcss
   sc query lanmanserver
   sc query termservice
   
   # Force stop if still running
   net stop lanmanserver /y
   net stop rpcss /y
   ```

2. **Firewall rule not created:**
   ```bash
   # Check rules exist
   netsh advfirewall firewall show rule name="BlockPort*"
   
   # Check specific port rules
   netsh advfirewall firewall show rule name="BlockPort445"
   ```

3. **Service restarted automatically:**
   - Windows dependencies may auto-restart services
   - Disable service startup:
   ```bash
   sc config rpcss start=disabled
   sc config lanmanserver start=disabled
   ```

4. **Port still showing open:**
   - Verify with netstat:
   ```bash
   netstat -an | findstr /E "(135|139|445|3389)"
   ```

---

### 7. Script Crashes on Startup

**Symptoms:**
```
Traceback (most recent call last):
  File "Network_Guard.py", line X, in <module>
    ...
```

**Common Causes & Solutions:**

1. **Python version too old:**
   ```bash
   python --version
   # Should be 3.8 or higher
   
   # Update Python from python.org
   ```

2. **Missing Scapy on import:**
   ```bash
   # Reinstall Scapy
   pip uninstall scapy -y
   pip install scapy --upgrade
   ```

3. **Network interface enumeration fails:**
   - Try with specific interface:
   ```python
   from scapy.all import conf
   conf.iface = "Ethernet"
   # Then run
   ```

4. **Subprocess call fails (Windows-specific):**
   - Ensure running as Administrator
   - Verify netsh path:
   ```bash
   where netsh
   # Should show: C:\Windows\System32\netsh.exe
   ```

---

### 8. High CPU Usage

**Symptoms:**
- Network_Guard using 50%+ CPU
- System becomes sluggish

**Causes & Solutions:**

1. **Extremely busy network:**
   - Add BPF filter to sniff fewer packets:
   ```python
   # In Network_Guard.py, modify sniff call
   sniff(prn=self.detect_arp_spoofing, filter='arp and ip', store=False)
   ```

2. **Inefficient packet processing:**
   - Check for infinite loops in detect_arp_spoofing()
   - Add processing throttle:
   ```python
   import time
   # In detect_arp_spoofing
   time.sleep(0.01)  # Small delay between packets
   ```

3. **Excessive logging:**
   - Reduce logging level:
   ```python
   logging.basicConfig(level=logging.WARNING)  # Less verbose
   ```

---

### 9. Firewall Rules Won't Apply

**Symptoms:**
```
netsh advfirewall firewall add rule ... 
Returns: "The object already exists"
```

**Solutions:**

1. **Rule already exists:**
   ```bash
   # Delete existing rule
   netsh advfirewall firewall delete rule name="BlockPort445"
   
   # Then re-create
   ```

2. **Firewall disabled:**
   ```bash
   # Enable Windows Firewall
   netsh advfirewall set allprofiles state on
   ```

3. **Group Policy override:**
   - Check Group Policy doesn't override:
   ```bash
   gpedit.msc
   # Navigate to: Windows Settings > Security Settings > Windows Firewall
   ```

---

### 10. ARP Cache Flush Fails

**Symptoms:**
```
ERROR: Failed to restore ARP cache: Access is denied
```

**Solutions:**

1. **Not running as Administrator:**
   - Must have Administrator privileges
   - Verify:
   ```bash
   whoami
   # Should show SYSTEM or Admin account
   ```

2. **Firewall blocking netsh:**
   - Add netsh to firewall exceptions
   - Or disable firewall temporarily for testing:
   ```bash
   netsh advfirewall set allprofiles state off
   ```

3. **Antivirus interference:**
   - Temporarily disable antivirus
   - Add script to antivirus whitelist

---

## Diagnostic Steps

### Complete System Check

Run this script to verify all prerequisites:

```python
import socket
import subprocess
import sys
from scapy.all import conf, get_windows_if_list

print("=== NETWORKGUARD-SUITE DIAGNOSTIC ===\n")

# 1. Python Version
print(f"✓ Python Version: {sys.version}")

# 2. Scapy Installation
try:
    from scapy.all import ARP, Ether, sniff
    print("✓ Scapy: INSTALLED")
except ImportError:
    print("✗ Scapy: NOT INSTALLED - Run: pip install scapy")

# 3. Windows Network Adapters
print(f"\n✓ Network Adapters:")
try:
    adapters = get_windows_if_list()
    for adapter in adapters:
        print(f"  - {adapter}")
except Exception as e:
    print(f"✗ Could not enumerate adapters: {e}")

# 4. Current Interface
print(f"\n✓ Current Scapy Interface: {conf.iface}")

# 5. Port Availability
print(f"\n✓ Vulnerable Port Status:")
for port in [135, 139, 445, 3389]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        status = "OPEN" if result == 0 else "CLOSED"
        print(f"  - Port {port}: {status}")
    except Exception as e:
        print(f"  - Port {port}: ERROR ({e})")

# 6. Administrator Status
print(f"\n✓ Privilege Level:")
try:
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    print(f"  - Administrator: {'YES ✓' if is_admin else 'NO ✗ (Required!)'}")
except:
    print(f"  - Administrator: UNKNOWN")

# 7. Firewall Status
print(f"\n✓ Windows Firewall Status:")
try:
    result = subprocess.check_output(
        'netsh advfirewall show allprofiles',
        shell=True,
        stderr=subprocess.DEVNULL,
        universal_newlines=True
    )
    if 'State' in result:
        print("  - Firewall detected and accessible")
except:
    print("  - Could not determine firewall status")

print("\n=== END DIAGNOSTIC ===")
```

### Network Traffic Analysis

To verify ARP spoofing detection is working:

```bash
# Terminal 1: Run Network_Guard
python Network_Guard.py

# Terminal 2: Generate test ARP traffic
python -c "
from scapy.all import *
for i in range(5):
    pkt = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst='192.168.1.1')
    sendp(pkt)
    print(f'ARP request {i+1} sent')
"
```

---

## Getting Help

If issues persist:

1. **Collect diagnostic data:**
   ```bash
   # Save to file
   python diagnostic.py > diagnostic_report.txt
   
   # Collect logs
   netstat -an > netstat_report.txt
   arp -a > arp_report.txt
   ipconfig /all > ipconfig_report.txt
   ```

2. **Check logs:**
   - Look at application console output
   - Check Windows Event Viewer: `eventvwr.msc`

3. **Search existing issues:**
   - GitHub Issues: https://github.com/Full-Stack-Systems-Strategist/NetworkGuard-Suite/issues

4. **Create detailed bug report with:**
   - Full error message/traceback
   - Diagnostic report output
   - Steps to reproduce
   - Network configuration (sanitized)
   - Python version and OS

---

**Last Updated:** 2026-04-29