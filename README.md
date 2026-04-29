# NetworkGuard-Suite

A comprehensive network security hardening toolkit that combines ARP spoofing detection with intelligent port and firewall management for Windows systems.

## 🎯 Overview

NetworkGuard-Suite is a dual-module security application designed to protect your network infrastructure through:

1. **ARP Spoofing Detection & Mitigation** - Real-time monitoring and automatic response to ARP-based attacks
2. **Network Hardening** - Automated identification and closure of vulnerable network services

## 🚀 Features

### Network_Guard Module
- **Real-time ARP Monitoring**: Continuously sniffs network traffic for ARP anomalies
- **Static ARP Binding**: Prevents ARP cache poisoning of critical gateway entries
- **Automatic Threat Response**: Restores ARP cache and alerts on detection
- **Honeypot Integration**: Automatically bridges detected attackers to a C2 honeypot for analysis
- **System Notifications**: Audio and logging alerts for security events

### Port Hardening Module
- **Vulnerability Scanning**: Identifies open RPC, SMB, and RDP ports
- **Service Management**: Automatically stops vulnerable network services
- **Firewall Hardening**: Creates Windows Firewall rules to block exploitation
- **Comprehensive Coverage**: Targets ports 135, 139, 445, 3389
- **Error Handling**: Graceful failure with detailed logging

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11 or Windows Server 2016+
- **Privileges**: Administrator/SYSTEM level access required
- **Python**: 3.8+
- **Network Interface**: Must have active network adapter

### Dependencies
```
scapy>=2.4.5
```

## 📦 Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/Full-Stack-Systems-Strategist/NetworkGuard-Suite.git
cd NetworkGuard-Suite
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure (Optional)
Edit the configuration in both scripts:
- `Network_Guard.py`: Modify `gateway_ip` and `gateway_mac` for your network
- `Python_script_to_identify_and_close_open.py`: Customize `PORTS_TO_CLOSE` and `SERVICES` dicts

## 🔧 Usage

### Run as Administrator
Both scripts **MUST** run with administrator privileges:

```bash
# Port Hardening (One-time or periodic)
python Python_script_to_identify_and_close_open.py
```

```bash
# ARP Protection (Long-running daemon)
python Network_Guard.py
```

### Running Both Simultaneously
```bash
# In separate administrator PowerShell/CMD windows:
# Terminal 1
python Network_Guard.py

# Terminal 2
python Python_script_to_identify_and_close_open.py
```

### Integration with Honeypot (Optional)
If you have the `arp_honeypot_bridge.py` module:
1. Place it in the project root directory
2. Network_Guard will automatically detect and use it
3. Attackers are automatically registered with the C2 honeypot

## 🏗️ How It Works

### Network_Guard.py Workflow

```
┌─────────────────────────────────────────┐
│  Application Start                      │
├─────────────────────────────────────────┤
│  1. Initialize Gateway IP & MAC         │
│  2. Set Static ARP Entry                │
│  3. Try Import Honeypot Module          │
│  4. Start Background Sniffer Thread     │
├─────────────────────────────────────────┤
│  Continuous Operation                   │
│  ↓                                      │
│  Packet Sniffer (separate thread)       │
│  ↓                                      │
│  Check if ARP Response                  │
│  ↓                                      │
│  Validate Against Static Entry          │
│  ↓                                      │
│  Match? YES → ALERT & RESPOND           │
│     └→ Restore ARP Cache                │
│     └→ Register Attacker to Honeypot    │
│     └→ System Beep & Logging            │
│  ↓                                      │
│  Continue Monitoring...                 │
└─────────────────────────────────────────┘
```

### Port Hardening Workflow

```
┌─────────────────────────────────────────┐
│  Script Start                           │
├─────────────────────────────────────────┤
│  For Each Vulnerable Port (135,139...)  │
│  ↓                                      │
│  Scan Port Status                       │
│  ↓                                      │
│  Port Open?                             │
│  ├─ YES                                 │
│  │  ├→ Stop Associated Service          │
│  │  └→ Add Firewall Block Rule          │
│  │  └→ Log Success                      │
│  ├─ NO                                  │
│  │  └→ Log Already Closed               │
│  ↓                                      │
│  Continue to Next Port...               │
└─────────────────────────────────────────┘
```

## 🔐 Security Architecture

### Threat Models Addressed

**1. ARP Spoofing Attack**
- **Threat**: Attacker sends fake ARP replies claiming to be gateway
- **Detection**: Compare response MAC against known gateway MAC
- **Response**: Flush poisoned cache, restore static entry
- **Prevention**: Static ARP binding makes future spoofing ineffective

**2. Network Service Exploitation**
- **Threat**: Attackers target RPC, SMB, RDP services for lateral movement
- **Detection**: Port scanning identifies listening services
- **Response**: Stop service + firewall rule = dual hardening
- **Prevention**: Services cannot restart and ports are blocked

### Defense Layers

```
Layer 1: Detection
  └─ Real-time packet analysis (Network_Guard)
  └─ Vulnerability scanning (Port Hardening)

Layer 2: Prevention
  └─ Static ARP binding (prevents cache poisoning)
  └─ Service termination (removes attack surface)

Layer 3: Response
  └─ Automatic cache restoration (active defense)
  └─ Firewall rules (persistent blocking)
  └─ Honeypot integration (threat collection)

Layer 4: Alerting
  └─ System audio alerts
  └─ Structured logging
  └─ Automatic threat reporting
```

## 📊 Ports & Services

| Port | Protocol | Service | Risk Level |
|------|----------|---------|-----------|
| 135  | TCP      | RPC Endpoint Mapper | HIGH |
| 139  | TCP      | NetBIOS Session Service | HIGH |
| 445  | TCP      | SMB over TCP | CRITICAL |
| 3389 | TCP      | Remote Desktop Protocol | CRITICAL |

## ⚠️ Important Warnings

### Prerequisites
- ⚠️ **Administrator Access Required**: Both scripts require elevated privileges
- ⚠️ **Network Disruption**: Improper configuration may disconnect you from network
- ⚠️ **Service Dependencies**: Stopping services may break legitimate functionality
- ⚠️ **Production Testing**: Test in non-production environments first
- ⚠️ **Backup Configuration**: Save firewall rules before running

### Before Running

1. **Identify Your Gateway**:
```bash
ipconfig /all
# Find "Default Gateway" IP and note associated MAC
```

2. **Update Configuration**:
```python
self.gateway_ip = '192.168.1.1'  # Your gateway IP
self.gateway_mac = '50:42:89:4A:F8:94'  # Your gateway MAC
```

3. **Test Network Services**:
```bash
netstat -an | findstr /E "(135|139|445|3389)"
```

4. **Document Open Ports**:
```bash
netstat -an | find /i "listening" > ports_before.txt
```

## 🛠️ Configuration Guide

### Network_Guard.py

```python
class NetworkGuard:
    def __init__(self):
        self.gateway_ip = '192.168.1.1'        # ← CHANGE THIS
        self.gateway_mac = '50:42:89:4A:F8:94' # ← CHANGE THIS
        # ... rest of init
```

**How to find your gateway MAC**:
```bash
# Windows CMD
arp -a
# Find your gateway IP in the list, note the Physical Address
```

### Python_script_to_identify_and_close_open.py

```python
PORTS_TO_CLOSE = [135, 139, 445, 3389]  # ← Customize as needed

SERVICES = {
    135: 'rpcss',
    139: 'lanmanworkstation',
    445: 'lanmanserver',
    3389: 'termservice'
}
```

## 📝 Logging & Monitoring

### Log Output Levels

```
DEBUG:   ARP entry already exists, detailed system calls
INFO:    Normal operations, service started, honeypot registered
WARNING: ARP spoofing detected, suspicious activity
ERROR:   Service stop failures, honeypot bridge errors
```

### Sample Log Output

```
2026-04-29 14:23:45,123 - INFO - Honeypot bridge initialized
2026-04-29 14:25:12,456 - WARNING - ARP spoofing attempt detected from aa:bb:cc:dd:ee:ff!
2026-04-29 14:25:12,789 - INFO - Automatically bridged attacker 192.168.1.50 to C2 server
2026-04-29 14:26:00,000 - INFO - Firewall rule added successfully for port 445
```

## 🚨 Incident Response

### If ARP Spoofing Detected

1. **Immediate Response** (Automatic):
   - System beep sounds
   - ARP cache flushed and restored
   - Attacker logged and registered

2. **Manual Investigation**:
```bash
# Check ARP table
arp -a

# Check ARP cache statistics
netsh interface ip show ipstats

# View recent network connections
netstat -anb

# Check firewall logs
Get-NetFirewallRule -DisplayName "*BlockPort*" | Get-NetFirewallRuleStatistic
```

3. **Forensics Collection**:
```bash
# Export network connections
netstat -anb > incident_netstat.txt

# Export ARP table
arp -a > incident_arp.txt

# Check event logs
wevtutil qe Security /c:100 /f:text > incident_security_events.txt
```

## 📚 Advanced Usage

### Integration with SIEM

Export logs to your SIEM platform:
```python
# Modify logging handler to send to syslog/splunk
handler = logging.handlers.SysLogHandler(address=('siem_server', 514))
```

### Custom Honeypot Module

If using custom `arp_honeypot_bridge.py`:

```python
class ARPHoneypotBridge:
    def register_attacker_with_c2(self, attacker_ip, attacker_mac):
        # Your C2 integration logic
        return client_id  # Must return ID for logging
```

### Schedule Periodic Port Hardening

Create a Windows Task Scheduler job:
```bash
# Run port hardening daily at 2 AM
schtasks /create /tn "NetworkGuard-PortHardening" /tr "C:\path\to\python.exe C:\path\to\script.py" /sc daily /st 02:00
```

## 🐛 Troubleshooting

### Issue: "Permission denied" errors

**Solution**: Run CMD/PowerShell as Administrator
```bash
# Check privilege level
whoami /priv
# Should show "SeDebugPrivilege" and other elevated privileges
```

### Issue: "Network is unreachable"

**Solution**: Verify network adapter configuration
```bash
# Check active adapters
ipconfig /all

# Verify default gateway
route print
```

### Issue: Honeypot module not found

**Solution**: This is non-critical; Network_Guard will continue without it
- Place `arp_honeypot_bridge.py` in project root to enable integration
- Check logs for "Could not import honeypot bridge module" message

### Issue: Port still open after script runs

**Solution**: Verify service was stopped and firewall rule added
```bash
# Check service status
sc query rpcss

# Check firewall rules
netsh advfirewall firewall show rule name="BlockPort*"
```

### Issue: ARP spoofing not detected

**Solution**: Verify gateway configuration and network interface
```bash
# Check static ARP entry
arp -a

# Verify interface
python -c "from scapy.all import conf; print(conf.iface)"
```

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Linux/macOS compatibility
- [ ] IPv6 support
- [ ] GUI dashboard
- [ ] REST API for remote management
- [ ] Machine learning for anomaly detection
- [ ] Integration with threat intelligence feeds
- [ ] Kubernetes network monitoring

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Disclaimer

This tool is provided for **authorized security testing and network protection only**. Users are responsible for:

- Ensuring they have authorization to monitor and modify target networks
- Complying with local, state, and federal laws
- Understanding the security implications of network modifications
- Testing in controlled environments before production deployment

Misuse of this tool for unauthorized network access is illegal.

## 📞 Support & Documentation

For issues, questions, or suggestions:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review logs in the application output
3. Open an issue on GitHub with:
   - Error message
   - Network configuration (sanitized)
   - Steps to reproduce

## 🎓 Educational Resources

- [ARP Spoofing Explained](https://www.comptia.org/blog/what-is-arp-spoofing)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Windows Firewall Rules](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/)
- [Network Hardening Guide](https://www.nist.gov/publications/security-network)

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-29  
**Maintained by**: Full-Stack-Systems-Strategist