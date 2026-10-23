'use client'
import {useEffect,useState} from 'react'
import {ShieldCheck,ShieldX,RefreshCcw,Hash} from 'lucide-react'
import {Card,SectionHeading,Status} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {request} from '@/lib/api'
type Audit={id:number;user_id:number|null;action:string;entity:string;at:string;before:Record<string,any>;after:Record<string,any>;hash:string;prev_hash:string}
export default function Audit(){
 const [events,setEvents]=useState<Audit[]>([]),[check,setCheck]=useState<{valid:boolean;checked:number;reason:string}|null>(null),[error,setError]=useState('')
 async function reload(){try{setEvents(await request('/audit'))}catch(e){setError((e as Error).message)}}
 async function verify(){try{setCheck(await request('/audit/verify'))}catch(e){setError((e as Error).message)}}
 useEffect(()=>{reload();verify()},[])
 return <div className="space-y-6"><div className="flex justify-between flex-wrap gap-3"><div><p className="text-xs font-bold text-teal uppercase tracking-widest mb-2">Governance & accountability</p><h1 className="page-title">Append-only Audit Trail</h1><p className="text-sm text-slate-500 mt-2">See who changed what and test hash-chain integrity.</p></div><div className="flex gap-2"><Button variant="outline" onClick={reload}><RefreshCcw size={14}/>Reload</Button><Button onClick={verify}><Hash size={15}/>Verify integrity</Button></div></div>
 {error&&<p role="alert" className="text-xs text-rose-700">{error}</p>}
 <Card className="flex items-center justify-between flex-wrap gap-4"><div className="flex gap-3 items-center">{check?.valid?<ShieldCheck className="text-emerald-700" size={28}/>:<ShieldX className="text-amber-600" size={28}/>}<div><p className="font-bold text-navy">{check?check.valid?'Audit integrity check passed':'Audit integrity check failed':'Not yet checked'}</p><p className="text-xs mt-1 text-slate-500">{check?.reason||'Reading chain…'} · {check?.checked||0} event(s) checked</p></div></div><Status tone={check?.valid?'green':'amber'}>{check?.valid?'CHAIN VERIFIED':'REVIEW REQUIRED'}</Status></Card>
 <Card><SectionHeading title="Recent audit events" subtitle="Each row includes a previous hash and content hash"/><div className="table-wrap"><table className="clean"><thead><tr><th>Event</th><th>Timestamp</th><th>Actor</th><th>Action / Target</th><th>Chain hash (prefix)</th></tr></thead><tbody>{events.map(e=><tr key={e.id}><td className="font-bold">#{e.id}</td><td className="whitespace-nowrap text-xs">{new Date(e.at).toLocaleString()}</td><td>{e.user_id===null?'Seed process':`User #${e.user_id}`}</td><td><b className="text-xs">{e.action}</b><div className="text-[11px] text-slate-400">{e.entity}</div>{e.after?.reason&&<p className="text-[11px] text-slate-500 mt-1">Reason: {String(e.after.reason)}</p>}</td><td className="font-mono text-[11px] text-slate-500">{e.hash.slice(0,17)}…</td></tr>)}</tbody></table></div><p className="text-xs text-slate-500 mt-4">Hash chaining provides app-level tamper evidence. This prototype does not offer external anchoring, immutable hardware storage or guarantees against privileged database rewriting.</p></Card>
 </div>
}
