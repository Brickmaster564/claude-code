#!/bin/bash
# Cashflow operational expenses sync
# Runs biweekly on Sundays at 10:00 AM

cd "/Users/jasper/Library/Application Support/Claude/Jasper OS - CC Hub"
python3 tools/cashflow_sync.py >> output/cashflow-sync/$(date +%Y-%m-%d).log 2>&1