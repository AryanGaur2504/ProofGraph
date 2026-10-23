"""Single-domain hosting launcher. Demo data is recreated on empty, ephemeral storage."""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = Path('/data/proofgraph.db')
DATA = Path('/data/storage')


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    if not DB.exists():
        subprocess.run([sys.executable, 'seed.py'], cwd=ROOT / 'backend', check=True)
    port = os.environ.get('PORT', '10000')
    commands = [
        ([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], ROOT / 'backend'),
        (['/usr/local/bin/node', 'node_modules/next/dist/bin/next', 'start', '--hostname', '0.0.0.0', '--port', port], ROOT / 'frontend'),
    ]
    children = []
    def shutdown(*_):
        for child in children:
            if child.poll() is None:
                child.terminate()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    try:
        for command, cwd in commands:
            children.append(subprocess.Popen(command, cwd=cwd))
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        raise RuntimeError('A ProofGraph service exited; review the logs')
    finally:
        shutdown()
        for child in children:
            try: child.wait(timeout=8)
            except subprocess.TimeoutExpired: child.kill()


if __name__ == '__main__':
    main()
