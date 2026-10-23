"""Quick read-only package validation (not a frontend build)."""
from pathlib import Path
import ast
import json
import sqlite3
import sys

base = Path(__file__).resolve().parent
required = [
    'requirements.txt', 'req.txt', 'backend/requirements.txt',
    'backend/req.txt', 'backend/app/main.py', 'backend/seed.py',
    'backend/proofgraph.db', 'frontend/package.json',
    'frontend/components/evidence-graph.tsx', 'frontend/app/demo/page.tsx',
    'docs/TRY_THE_DEMO.md', 'setup_windows.bat', 'start_windows.bat',
]
missing = [item for item in required if not (base / item).is_file()]
if missing:
    print('Missing required files:', *missing, sep='\n - ')
    sys.exit(1)
frontend = json.loads((base/'frontend/package.json').read_text(encoding='utf-8'))
assert '@xyflow/react' in frontend['dependencies']
graph = (base/'frontend/components/evidence-graph.tsx').read_text(encoding='utf-8')
assert 'import {ReactFlow,' in graph, 'EvidenceGraph still has an incorrect default import.'
for source in (base/'backend/app').glob('*.py'):
    ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
with sqlite3.connect(base/'backend/proofgraph.db') as conn:
    stored = [name for (name,) in conn.execute('SELECT path FROM documents')]
    missing_evidence = [name for name in stored if not (base/'backend/storage'/name).is_file()]
    if missing_evidence:
        print('Missing evidence files:', *missing_evidence, sep='\n - ')
        sys.exit(1)
print(f'PASS: dependencies, source, demo database and {len(stored)} referenced evidence files')
print('PASS: ReactFlow named import and backend Python syntax')
print('NOTE: full Next.js build still requires npm install in a connected environment.')
