"""Smoke/acceptance tests run against an isolated SQLite copy of the synthetic seeded DB."""
from pathlib import Path
import sqlite3
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db
from app.models import Base

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def client(tmp_path):
    source=ROOT/'proofgraph.db'
    if not source.is_file():pytest.skip('Seed the demo with python seed.py --reset before testing.')
    target=tmp_path/'test.db'
    with sqlite3.connect(str(source)) as original,sqlite3.connect(str(target)) as copy:
        original.backup(copy)
    engine=create_engine(f'sqlite:///{target}',connect_args={'check_same_thread':False})
    factory=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
    def replacement():
        with factory() as s:yield s
    app.dependency_overrides[get_db]=replacement
    with TestClient(app) as c:
        c.test_factory=factory
        yield c
    app.dependency_overrides.clear()
    engine.dispose()

@pytest.fixture
def auth(client):
    def login(name='officer'):
        r=client.post('/api/auth/login',json={'username':name,'password':'Demo@12345'})
        assert r.status_code==200,r.text
        return {'Authorization':'Bearer '+r.json()['access_token']}
    return login
