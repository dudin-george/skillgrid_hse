#!/bin/bash

echo "Checking firewall status and port configuration..."

# Check if ufw is installed
if command -v ufw &> /dev/null; then
    echo "UFW Firewall status:"
    sudo ufw status
else
    echo "UFW not installed."
fi

# Check if iptables is available
if command -v iptables &> /dev/null; then
    echo "IPTables rules:"
    sudo iptables -L | grep -E "(Chain|ACCEPT|DROP|REJECT|80|443|http|https)"
else
    echo "IPTables not accessible."
fi

# Check ports with netstat
echo "Active ports (netstat):"
if command -v netstat &> /dev/null; then
    sudo netstat -tulpn | grep -E "(80|443)"
else
    echo "netstat not installed."
fi

# Check ports with ss (newer alternative to netstat)
echo "Active ports (ss):"
if command -v ss &> /dev/null; then
    sudo ss -tulpn | grep -E "(80|443)"
else
    echo "ss not installed."
fi

# Check if ports are bound by Docker
echo "Docker port mappings:"
docker ps --format "{{.Names}}: {{.Ports}}"

# Check if we can connect locally
echo "Testing local connections:"
echo "Port 80:"
curl -v http://localhost:80 -m 5 2>&1 | grep -E "(Connected to|Failed to connect)"
echo "Port 443:"
curl -v https://localhost:443 -k -m 5 2>&1 | grep -E "(Connected to|Failed to connect)" 