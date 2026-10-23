'use client'
import {useEffect,useState} from 'react'
import Link from 'next/link'
import {ArrowRight,FilePlus2,FolderOpen,Search,RefreshCw} from 'lucide-react'
import {request} from '@/lib/api'
import {CaseSummary} from '@/lib/types'
import {Card,Status} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
export default function Applications(){
 const [all,setAll]=useState<CaseSummary[]>([]),[query,setQuery]=useState(''),[error,setError]=useState('')
 async function load(){try{setAll(await request<CaseSummary[]>('/cases'));setError('')}catch(e){setError((e as Error).message)}}
 useEffect(()=>{load()},[])
 const filtered=all.filter(c=>!c.institution_code.startsWith('SYN-EVAL-')&&!(['SYN-BLUERIDGE','SYN-NORTHSTAR'].includes(c.institution_code))).filter(c=>(c.institution+' '+c.id+' '+c.category).toLowerCase().includes(query.toLowerCase())).sort((a,b)=>b.id-a.id)
 return <div className="max-w-5xl mx-auto space-y-5"><div className="flex flex-wrap gap-3 items-center justify-between"><div><p className="text-xs font-bold uppercase text-teal">Your workspace</p><h1 className="text-3xl font-bold text-navy mt-1">Applications</h1><p className="text-sm text-slate-500 mt-2">Open an application to add documents or view its latest result.</p></div><Link href="/check"><Button><FilePlus2 size={16}/> New check</Button></Link></div>
 <Card><div className="flex items-center gap-3 border border-slate-200 rounded-xl px-3 py-2"><Search size={18} className="text-slate-500"/><input className="w-full border-0 outline-none bg-transparent text-sm" placeholder="Find an institution or application number" value={query} onChange={e=>setQuery(e.target.value)}/><button aria-label="Refresh applications" onClick={load} className="p-1 text-teal"><RefreshCw size={18}/></button></div>{error&&<p className="text-red-700 mt-3 text-sm">{error}</p>}</Card>
 <div className="space-y-2">{filtered.length?filtered.map(c=><Link href={`/check?case=${c.id}`} key={c.id} className="flex gap-3 md:gap-5 items-center rounded-2xl border bg-white p-4 md:p-5 hover:border-teal transition-colors"><div className="p-3 rounded-xl bg-teal/10 text-teal shrink-0"><FolderOpen size={23}/></div><div className="min-w-0 flex-1"><h2 className="text-sm md:text-base text-navy font-bold truncate">{c.institution}</h2><p className="text-xs text-slate-500 mt-1">Application #{c.id} · {c.category}</p><p className="text-xs text-slate-500 mt-1">{c.state}</p></div><div className="shrink-0"><Status tone={c.findings_count?'amber':'green'}>{c.findings_count?`${c.findings_count} to review`:'No findings'}</Status></div><ArrowRight className="text-teal shrink-0" size={20}/></Link>):<Card className="text-center text-sm text-slate-500 !p-9">No matching applications. <Link className="text-teal font-bold" href="/check">Create a new check</Link>.</Card>}</div>
 </div>
}
