"""Small LLM seam: offline by default, no uncited knowledge allowed."""
from dataclasses import dataclass
from typing import Protocol

@dataclass
class CaseEvidence:
    title:str
    reason:str
    next_action:str
    source_a:dict
    source_b:dict
    rule_id:str
    version:int

class LLMProvider(Protocol):
    def explain(self,question:str,evidence:list[CaseEvidence])->str:...

class DisabledLLM:
    """Deterministic evidence-only explanation. Works with no keys or network."""
    def explain(self,question:str,evidence:list[CaseEvidence])->str:
        return '\n'.join(f'{x.title}: {x.reason} Suggested next action: {x.next_action}' for x in evidence) if evidence else 'Insufficient cited case evidence to answer that question.'

class ExternalLLMNotConfigured:
    """Explicit extension point: requires a vetted API client, provider credentials and a citation validator."""
    def explain(self,question:str,evidence:list[CaseEvidence])->str:
        raise RuntimeError('External LLM not configured. Use DisabledLLM and cited local evidence.')
