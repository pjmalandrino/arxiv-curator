#!/bin/bash

echo "🔍 Testing ArXiv Curator Frontend Integration"
echo "============================================"

# Check if frontend is running
echo -n "✓ Frontend server: "
if curl -s http://localhost:3000 > /dev/null; then
    echo "Running on http://localhost:3000"
else
    echo "Not running"
    exit 1
fi

# Check if backend is running
echo -n "✓ Backend API: "
if curl -s http://localhost:5000/api/papers > /dev/null; then
    echo "Running on http://localhost:5000"
else
    echo "Not running"
    exit 1
fi

# Test API endpoints
echo -e "\n📊 API Status:"
echo -n "  - /api/papers: "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/papers)
if [ $STATUS -eq 200 ]; then
    COUNT=$(curl -s http://localhost:5000/api/papers | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
    echo "✓ OK ($COUNT papers)"
else
    echo "✗ Error (HTTP $STATUS)"
fi

echo -n "  - /api/stats: "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/stats)
if [ $STATUS -eq 200 ]; then
    echo "✓ OK"
else
    echo "✗ Error (HTTP $STATUS)"
fi

echo -e "\n🎉 Frontend Integration Test Complete!"
echo "======================================"
echo "You can now open http://localhost:3000 in your browser"
echo ""
echo "Available pages:"
echo "  - Dashboard: http://localhost:3000/"
echo "  - Papers: http://localhost:3000/papers"
echo "  - About: http://localhost:3000/about"
