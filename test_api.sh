#!/bin/bash

echo "Testing FRC Strategic Dashboard API..."
echo ""

# Test root endpoint
echo "1. Testing root endpoint (should serve static file):"
curl -s http://localhost:8000/ | grep -o "<title>.*</title>" | head -1
echo ""

# Test health endpoint
echo "2. Testing health endpoint:"
curl -s http://localhost:8000/health
echo ""
echo ""

# Test API docs
echo "3. Testing API docs endpoint:"
curl -s http://localhost:8000/api/docs | grep -o "<title>.*</title>" | head -1
echo ""
echo ""

# Test teams endpoint
echo "4. Testing teams endpoint:"
curl -s http://localhost:8000/api/v1/teams/ | python3 -m json.tool | head -10
echo ""
echo ""

# Test matches endpoint
echo "5. Testing matches/teams endpoint:"
curl -s http://localhost:8000/api/v1/matches/teams | python3 -m json.tool | head -10
echo ""
echo ""

# Test predictions endpoint
echo "6. Testing predictions endpoint:"
curl -s http://localhost:8000/api/v1/predictions/ | python3 -m json.tool | head -10
echo ""
echo ""

# Test stats endpoint
echo "7. Testing stats endpoint:"
curl -s http://localhost:8000/api/v1/stats/ | python3 -m json.tool | head -10
echo ""
echo ""

echo "All tests completed!"
