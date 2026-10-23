"""One-command development launcher. No Docker or external services required."""
from pathlib import Path
import subprocess,sys,signal,time

ROOT=Path(__file__).resolve().parent
BACKEND=ROOT/'backend';FRONTEND=ROOT/'frontend'

def main():
    if not (BACKEND/'proofgraph.db').exists():
        raise SystemExit('Run: cd backend && python seed.py --reset (synthetic demo only)')
    if not (FRONTEND/'node_modules'/'next').exists():
        raise SystemExit('Node dependencies missing. Run: cd frontend && npm install')
    npm='npm.cmd' if sys.platform=='win32' else 'npm'
    cmds=[([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000'],BACKEND),([npm,'run','dev'],FRONTEND)]
    children=[]
    try:
        for cmd,cwd in cmds:
            print('Starting:',' '.join(cmd),'from',cwd,flush=True)
            children.append(subprocess.Popen(cmd,cwd=cwd))
        print('\nProofGraph: http://127.0.0.1:3000  |  API docs: http://127.0.0.1:8000/api/docs\n',flush=True)
        while all(p.poll() is None for p in children):time.sleep(.5)
        raise SystemExit('A service stopped unexpectedly; see logs above.')
    except KeyboardInterrupt:
        print('Stopping services…',flush=True)
    finally:
        for p in children:
            if p.poll() is None:p.terminate()
        for p in children:
            try:p.wait(timeout=7)
            except subprocess.TimeoutExpired:p.kill()

if __name__=='__main__':main()
