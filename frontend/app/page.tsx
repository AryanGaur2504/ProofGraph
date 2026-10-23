'use client'
import {useEffect,useState} from 'react'
import Link from 'next/link'
import {ArrowRight,CheckCircle2,ClipboardCheck,FileCheck,FolderOpen,UploadCloud} from 'lucide-react'
import {request} from '@/lib/api'
import {CaseSummary} from '@/lib/types'
import {Card,Status} from '@/components/ui/card'
export default function Home(){
 const [cases,setCases]=useState<CaseSummary[]>([])
 useEffect(()=>{request<CaseSummary[]>('/cases').then(setCases).catch(()=>{})},[])
 const recent=cases.filter(c=>!c.institution_code.startsWith('SYN-EVAL-')&&!(['SYN-BLUERIDGE','SYN-NORTHSTAR'].includes(c.institution_code))).sort((a,b)=>b.id-a.id).slice(0,4)
 return <div className="max-w-5xl mx-auto space-y-8">
  <section className="rounded-3xl bg-navy p-7 md:p-10 text-white"><p className="text-[#77e3d9] uppercase tracking-wide font-bold text-xs">ProofGraph</p><h1 className="text-3xl md:text-4xl font-bold max-w-xl mt-3 tracking-tight">Check your documents in three simple steps.</h1><p className="text-slate-200 mt-4 max-w-2xl">Upload application documents, find missing information or conflicting details, and see exactly what needs attention.</p><Link href="/check" className="mt-7 inline-flex items-center gap-3 rounded-xl bg-teal text-white font-bold px-6 py-4">Upload & validate documents <ArrowRight size={18}/></Link></section>
  <section className="grid md:grid-cols-3 gap-4">{[
   {icon:UploadCloud,n:'01',t:'Upload',d:'Choose an institution and add the application form, inventory, and certificates.'},
   {icon:ClipboardCheck,n:'02',t:'Validate',d:'ProofGraph reads the files and compares fields, expiry dates, and required documents.'},
   {icon:CheckCircle2,n:'03',t:'Review',d:'See a simple result, open the source evidence, and download a report.'},
  ].map(s=><Card key={s.n} className="!p-6"><div className="flex items-center justify-between"><span className="text-teal font-bold text-lg">{s.n}</span><s.icon size={27} className="text-teal"/></div><h2 className="text-xl font-bold text-navy mt-4">{s.t}</h2><p className="text-sm text-slate-500 mt-2 leading-relaxed">{s.d}</p></Card>)}</section>
  <section><div className="flex flex-wrap items-end justify-between gap-3 mb-4"><div><h2 className="text-xl font-bold text-navy">Recent applications</h2><p className="text-sm text-slate-500 mt-1">Pick up where you left off.</p></div><Link href="/cases" className="text-teal text-sm font-bold">View all <ArrowRight className="inline" size={15}/></Link></div><Card className="!p-0 overflow-hidden">{recent.length?recent.map(c=><Link href={`/check?case=${c.id}`} key={c.id} className="flex items-center gap-4 px-5 py-4 border-b border-slate-100 last:border-0 hover:bg-slate-50"><span className="w-10 h-10 grid place-items-center rounded-xl bg-teal/10 text-teal shrink-0"><FolderOpen size={19}/></span><span className="flex-1 min-w-0"><b className="text-navy block text-sm truncate">{c.institution}</b><span className="text-xs text-slate-500">Application #{c.id} · {c.category}</span></span><Status tone={c.findings_count?'amber':'green'}>{c.findings_count?`${c.findings_count} items to review`:'No open findings'}</Status><ArrowRight size={18} className="text-teal shrink-0"/></Link>):<div className="p-8 text-sm text-slate-500 text-center">No applications yet. <Link className="font-bold text-teal" href="/check">Create the first check.</Link></div>}</Card></section>
  <div className="text-xs text-slate-500 flex items-start gap-2"><FileCheck size={16} className="shrink-0"/><span>Results are consistency and sample-rule checks, not official authentication. Human review is always required for institutional decisions.</span></div>
 </div>
}
