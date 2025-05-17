#!/bin/bash

echo "Checking connectivity to skillgrid.tech..."
echo ""

# Check if the domain resolves
echo "Checking DNS resolution:"
host skillgrid.tech
echo ""

# Check if port 80 is open
echo "Checking if port 80 is open:"
nc -zv skillgrid.tech 80 2>&1
echo ""

# Try making a request to the domain
echo "Trying to make an HTTP request:"
curl -v http://skillgrid.tech 2>&1
echo ""

echo "Done checking connectivity." 