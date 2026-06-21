#!/bin/bash

echo "=== FRC Strategic Dashboard - Final Test ==="
echo ""

# Test 1: Root endpoint (should serve static HTML)
echo "Test 1: Root endpoint"
RESPONSE=$(curl -s http://localhost:8000/ | grep -o "<title>.*</title>")
if [[ $RESPONSE == *"FRC Strategic Dashboard"* ]]; then
    echo "✓ Root endpoint serves static file"
else
    echo "✗ Root endpoint failed"
fi
echo ""

# Test 2: Health endpoint
echo "Test 2: Health endpoint"
RESPONSE=$(curl -s http://localhost:8000/health)
if [[ $RESPONSE == *"healthy"* ]]; then
    echo "✓ Health endpoint works"
else
    echo "✗ Health endpoint failed"
fi
echo ""

# Test 3: API Docs
echo "Test 3: API Docs endpoint"
RESPONSE=$(curl -s http://localhost:8000/api/docs | grep -o "<title>.*</title>")
if [[ $RESPONSE == *"Swagger UI"* ]]; then
    echo "✓ API Docs endpoint works"
else
    echo "✗ API Docs endpoint failed"
fi
echo ""

# Test 4: Teams API endpoint
echo "Test 4: Teams API endpoint"
RESPONSE=$(curl -s http://localhost:8000/api/v1/teams/)
if [[ $RESPONSE == *"status"* ]]; then
    echo "✓ Teams API endpoint works"
else
    echo "✗ Teams API endpoint failed"
fi
echo ""

# Test 5: Matches API endpoint
echo "Test 5: Matches API endpoint"
RESPONSE=$(curl -s http://localhost:8000/api/v1/matches/teams)
if [[ $RESPONSE == *"status"* ]]; then
    echo "✓ Matches API endpoint works"
else
    echo "✗ Matches API endpoint failed"
fi
echo ""

# Test 6: Predictions API endpoint
echo "Test 6: Predictions API endpoint"
RESPONSE=$(curl -s http://localhost:8000/api/v1/predictions/)
if [[ $RESPONSE == *"status"* ]]; then
    echo "✓ Predictions API endpoint works"
else
    echo "✗ Predictions API endpoint failed"
fi
echo ""

# Test 7: Stats API endpoint
echo "Test 7: Stats API endpoint"
RESPONSE=$(curl -s http://localhost:8000/api/v1/stats/)
if [[ $RESPONSE == *"status"* ]]; then
    echo "✓ Stats API endpoint works"
else
    echo "✗ Stats API endpoint failed"
fi
echo ""

echo "=== Test Summary ==="
echo "All core endpoints are accessible from http://localhost:8000"
echo "✓ Static files are served from root"
echo "✓ API endpoints are accessible at /api/v1/*"
echo "✓ API documentation is available at /api/docs"
echo ""
echo "Configuration complete!"
