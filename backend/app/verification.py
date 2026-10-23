"""Adapter contract. No real government endpoints are contacted or presumed."""
from abc import ABC,abstractmethod
from dataclasses import dataclass
from typing import Literal
from .models import Verification

VerificationStatus=Literal['VERIFIED_OFFICIAL','PENDING','SOURCE_UNAVAILABLE','MANUAL_REQUIRED','MISMATCH']
@dataclass
class VerificationOutcome:
    status:VerificationStatus
    simulated:bool
    source:str
    detail:str

class VerificationAdapter(ABC):
    @abstractmethod
    def verify(self, doc_id:int|None=None)->VerificationOutcome: ...

class SimulatedAdapter(VerificationAdapter):
    def __init__(self,status:Literal['PENDING','SOURCE_UNAVAILABLE','MANUAL_REQUIRED']='SOURCE_UNAVAILABLE'):
        self.status=status
    def verify(self,doc_id=None):
        return VerificationOutcome(self.status,True,'SIMULATED DEMO ADAPTER — NO GOVERNMENT CONNECTION','Synthetic demonstration outcome, not issued by an authority')

class AuthorizedSourceStub(VerificationAdapter):
    def verify(self,doc_id=None):
        return VerificationOutcome('MANUAL_REQUIRED',False,'AUTHORIZED SOURCE: NOT CONFIGURED','No authority-provided API or certificate chain has been configured. Verify manually.')

def save_outcome(db,application_id,document_id,outcome:VerificationOutcome):
    row=Verification(application_id=application_id,document_id=document_id,source=outcome.source,status=outcome.status,simulated=outcome.simulated,detail=outcome.detail)
    db.add(row);db.flush();return row
