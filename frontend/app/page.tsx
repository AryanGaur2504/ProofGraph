'use client'
import {useEffect,useState} from 'react'
import Link from 'next/link'
import {ArrowRight,BookOpen,CheckCircle2,FileCheck2,FilePlus2,FileSearch,FolderOpen,GitCompareArrows,PlayCircle,RefreshCw,ShieldAlert,UploadCloud} from 'lucide-react'
import {request} from '@/lib/api'
import {CaseSummary} from '@/lib/types'
import {Card,PriorityPill} from '@/components/ui/card'
import {Button} from '@/components/ui/button'

export default function Dashboard(){
 const [cases,setCases]=useState<CaseSummary[]>([])
 const [error,setError]=useState('')
 useEffect(()=>{request<CaseSummary[]>('/cases').then(setCases).catch(e=>setError(e.message))},[])
 const recent=[...cases].sort((a,b)=>b.id-a.id).slice(0,5)
 return <div className="space-y-7 max-w-6xl mx-auto">
  <section className="rounded-3xl bg-navy text-white p-6 md:p-9 relative overflow-hidden"><div className="absolute -right-16 -top-16 w-60 h-60 rounded-full bg-teal/20 blur-3xl"/><div className="relative"><p className="text-xs text-[#6ce1d5] font-bold tracking-wider uppercase">ProofGraph · Evidence intelligence</p><h1 className="mt-3 text-3xl md:text-4xl font-bold tracking-tight max-w-3xl leading-tight">Check institution documents without the paperwork confusion.</h1><p className="text-sm md:text-base text-slate-200 mt-4 max-w-2xl leading-relaxed">Upload supporting PDFs, let ProofGraph compare their claims, and see which differences need human attention—along with the exact source evidence.</p><div className="flex flex-wrap gap-3 mt-7"><Link href="/check"><Button className="!py-3.5 !px-5"><FilePlus2 size={18}/> Upload & check documents <ArrowRight size={17}/></Button></Link><Link href="/demo"><Button variant="outline" className="!border-white/40 !bg-white/10 !text-white !py-3.5 hover:!bg-white/20"><PlayCircle size={18}/> Try with demo data</Button></Link></div></div></section>
  <section><div className="mb-4"><h2 className="font-bold text-xl text-navy">How to use ProofGraph</h2><p className="text-sm text-slate-500 mt-1">Four simple actions. You do not need to understand the evidence graph to get started.</p></div><div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3">{[
   {num:'1',title:'Start a check',desc:'Choose an institution and create or open an application.',icon:FolderOpen},
   {num:'2',title:'Upload files',desc:'Add application forms, certificates and evidence PDFs.',icon:UploadCloud},
   {num:'3',title:'Check results',desc:'Spot missing records, mismatched values and expired evidence.',icon:FileSearch},
   {num:'4',title:'Decide next action',desc:'Inspect exact pages, request evidence or export a draft report.',icon:CheckCircle2},
  ].map((s,i)=><Link href="/check" key={s.num} className="block"><Card className="h-full hover:border-teal/60 transition-colors"><div className="flex justify-between items-center"><span className="w-9 h-9 rounded-xl bg-teal/10 text-teal grid place-items-center font-bold">{s.num}</span><s.icon size={21} className="text-teal"/></div><h3 className="font-bold text-navy mt-4">{s.title}</h3><p className="text-xs text-slate-500 mt-2 leading-relaxed">{s.desc}</p></Card></Link>)}</div></section>
  <section><div className="flex flex-wrap justify-between items-center gap-2 mb-4"><div><h2 className="font-bold text-xl text-navy">Try a real demonstration</h2><p className="text-sm text-slate-500 mt-1">Pick an example and inspect how the checking engine responds.</p></div><Link href="/demo" className="text-teal text-xs font-bold flex items-center gap-1">See all demo cases <ArrowRight size={14}/></Link></div><div className="grid md:grid-cols-3 gap-3">{[
    {id:1,title:'18 vs 15 laboratories',help:'Compare two conflicting claims and the previous year’s count.',icon:GitCompareArrows},
    {id:2,title:'Expired + reused certificate',help:'See expiry and duplicate-file review signals.',icon:ShieldAlert},
    {id:3,title:'Consistent documents',help:'See an application without high-priority findings.',icon:FileCheck2},
   ].map(s=><Link key={s.id} href={`/demo?case=${s.id}`} className="block"><Card className="h-full hover:border-teal/60"><div className="flex items-center gap-2 text-teal"><s.icon size={19}/><span className="text-[11px] font-bold">EXAMPLE {s.id}</span></div><h3 className="text-sm text-navy font-bold mt-3">{s.title}</h3><p className="text-xs leading-relaxed text-slate-500 mt-2">{s.help}</p><span className="flex items-center gap-1 text-teal font-bold text-xs mt-4">Open example <ArrowRight size={14}/></span></Card></Link>)}</div></section>
  <section><div className="flex flex-wrap justify-between items-end gap-2 mb-4"><div><h2 className="font-bold text-xl text-navy">Your applications</h2><p className="text-sm text-slate-500 mt-1">Select one to upload more documents or rerun checks.</p></div><Link href="/cases" className="text-teal font-bold text-xs flex items-center gap-1">All applications <ArrowRight size={14}/></Link></div><Card className="!p-0 overflow-hidden">{error&&<p role="alert" className="text-red-700 p-4 text-sm">{error}</p>}{recent.length?recent.map(c=><Link key={c.id} href={`/check?case=${c.id}`} className="flex flex-wrap sm:flex-nowrap items-center gap-3 px-5 py-4 border-b border-slate-100 last:border-b-0 hover:bg-slate-50"><span className="shrink-0 w-10 h-10 grid place-items-center bg-teal/10 text-teal rounded-xl text-xs font-bold">#{c.id}</span><div className="flex-1 min-w-32"><p className="font-bold text-sm text-navy">{c.institution}</p><p className="text-xs text-slate-500 mt-1">{c.category} · {c.findings_count} findings</p></div><PriorityPill level={c.priority.label}/><span className="font-bold text-xs text-teal flex items-center gap-1">Open check <ArrowRight size={13}/></span></Link>):<div className="p-8 text-center text-slate-500 text-sm">No applications found yet. <Link href="/check" className="text-teal font-bold underline">Start your first check.</Link></div>}</Card></section>
  <p className="text-xs text-slate-500 leading-relaxed">All records and rules in this demonstration are synthetic. Inconsistencies are review signals, not proof of document forgery, non-compliance or official authentication.</p>
 </div>
}
