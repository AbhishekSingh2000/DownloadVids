#!/bin/bash
# All pending/error rows - prepare with modest parallelism (3 at a time)
IDX_LIST=$(curl -s http://localhost:8001/api/stats > /dev/null; curl -s http://localhost:8001/api/videos | python -c "
import json,sys
for r in json.load(sys.stdin):
    if r['status'] != 'ready':
        print(r['idx'])")

i=0
for idx in $IDX_LIST; do
  curl -s -X POST http://localhost:8001/api/videos/$idx/prepare > /dev/null &
  i=$((i+1))
  if [ $((i % 3)) -eq 0 ]; then wait; sleep 1; fi
done
wait
echo "done" > /app/tests/prep_v3b.marker
