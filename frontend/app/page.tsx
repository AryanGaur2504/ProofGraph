'use client'
import {useEffect,useState} from 'react'
import Link from 'next/link'
import {ArrowRight,ArrowUpRight,Building2,FileWarning,Network,History,ShieldAlert,CheckCircle2,FileText,ClipboardCheck,GitCompareArrows,Play} from 'lucide-react'
import {ResponsiveContainer,BarChart,Bar,XAxis,YAxis,Tooltip,CartesianGrid} from 'recharts'
import {request} from '@/lib/api'
import {CaseSummary} from '@/lib/types'
import {Card,PriorityPill,SectionHeading} from '@/components/ui/card'
import {Button} from '@/components/ui/button'
import {useAuth} from '@/components/shell'

const samples=[
 {id:1,topic:'Contradictory claims',title:'18 labs ≠ 15 labs',detail:'Application form versus room inventory. Earlier year declared 12.',link:'Explore inconsistency'},
 {id:2,topic:'Questionable documents',title:'Expired + reused file',detail:'Detect an expired certificate and a cross-institution document match.',link:'Inspect documents'},
 {id:3,topic:'Control example',title:'No false alarm',detail:'Same checks on consistent source data should produce no high-severity findings.',link:'See a clean case'},
]
export default function Dashboard(){
 const [cases,setCases]=useState<CaseSummary[]>([])
 const [error,setError]=useState('')
 const {user}=useAuth()
 useEffect(()=>{request<CaseSummary[]>('/cases').then(setCases).catch(e=>setError(e.message))},[])
 const stats=[
  {title:'Applications checked',value:cases.length,icon:Building2,foot:'Synthetic case records'},
  {title:'High-attention cases',value:cases.filter(c=>c.priority.label==='High').length,icon:ShieldAlert,foot:'Officer triage only'},
  {title:'Findings to review',value:cases.reduce((n,c)=>n+c.findings_count,0),icon:FileWarning,foot:'Supported by evidence / sample rules'},
  {title:'Unexplained changes',value:cases.reduce((n,c)=>n+c.unexplained_count,0),icon:History,foot:'Changes versus historical snapshots'},
 ]
 const chart=[{name:'High',cases:cases.filter(x=>x.priority.label==='High').length},{name:'Medium',cases:cases.filter(x=>x.priority.label==='Medium').length},{name:'Low',cases:cases.filter(x=>x.priority.label==='Low').length}]
 return <div className="space-y-7">
  <section className="bg-navy text-white rounded-3xl p-6 md:p-9 overflow-hidden relative">
   <div className="absolute -right-20 -top-28 h-72 w-72 rounded-full bg-teal/20 blur-3xl pointer-events-none"/>
   <div className="relative max-w-4xl"><p className="text-[#69e2d5] font-bold text-xs uppercase tracking-[.18em]">ProofGraph · AICTE application scrutiny prototype</p><h1 className="text-2xl md:text-4xl font-extrabold tracking-tight mt-3 leading-tight">From scattered documents to <span className="text-[#6de1d5]">evidence-backed findings.</span></h1>
    <p className="text-sm md:text-base text-slate-200 mt-4 leading-relaxed max-w-3xl">ProofGraph helps a scrutiny officer compare what an institution <b>declares</b>, what its supporting documents <b>actually say</b>, and what previous applications <b>recorded</b>. It highlights inconsistencies, identifies the source PDF and relevant sample rule, and lets a human decide what happens next.</p>
    <div className="flex flex-wrap gap-3 mt-6"><Link href="/demo"><Button><Play size={16}/> Run an interactive demonstration</Button></Link><Link href="/portal"><Button variant="outline" className="!border-slate-400 !text-white !bg-white/10 hover:!bg-white/20"><FileText size={16}/> Upload sample evidence</Button></Link><Link className="inline-flex items-center gap-1 text-xs font-semibold text-[#9af5ec] px-2 py-2" href="/guide">5-minute judge presentation <ArrowRight size={14}/></Link></div>
   </div>
  </section>
  <section className="space-y-3"><div><h2 className="font-bold text-lg text-navy">Exactly what the software does</h2><p className="text-xs text-slate-600 mt-1">Four observable stages, from intake to officer decision</p></div><div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">{[
   {n:'1',title:'Reads PDFs',icon:FileText,description:'Extracts fields such as lab count and certificate expiry, with confidence and page highlights.'},
   {n:'2',title:'Finds discrepancies',icon:GitCompareArrows,description:'Runs sample validation rules across files, dates, document hashes and older submissions.'},
   {n:'3',title:'Shows the proof',icon:Network,description:'Connects conflicting values to documents and rules in a navigable evidence graph.'},
   {n:'4',title:'Assists human review',icon:ClipboardCheck,description:'Allows officers to request evidence, record decisions and export a draft report.'},
  ].map(s=><div key={s.n} className="bg-white border rounded-2xl p-4"><div className="flex justify-between items-center"><span className="text-xs font-bold text-teal">STEP 0{s.n}</span><s.icon className="text-teal" size={20}/></div><p className="text-sm font-bold text-navy mt-3">{s.title}</p><p className="text-xs text-slate-600 leading-relaxed mt-2">{s.description}</p></div>)}</div></section>
  <section><div className="flex flex-wrap items-end justify-between gap-3 mb-3"><div><h2 className="font-bold text-lg text-navy">Three demos that show the actual checks</h2><p className="text-xs text-slate-600 mt-1">Select a scenario, run its backend validation and inspect the resulting evidence</p></div><Link href="/demo" className="text-teal text-xs font-bold flex gap-1 items-center">Open demo lab <ArrowRight size={14}/></Link></div><div className="grid md:grid-cols-3 gap-4">{samples.map((s,i)=>{
   const c=cases.find(x=>x.id===s.id)
   return <Link key={s.id} href={`/demo?case=${s.id}`} className="block bg-white border-2 border-slate-100 hover:border-teal/40 rounded-2xl p-5 transition-colors group"><div className="flex justify-between items-center"><span className="text-[11px] uppercase tracking-wider font-bold text-teal">Scenario 0{i+1}</span>{c&&<PriorityPill level={c.priority.label}/>}</div><p className="mt-2 font-bold text-lg text-navy">{s.title}</p><p className="text-xs font-semibold text-slate-500 mt-1">{s.topic}</p><p className="text-xs text-slate-600 leading-relaxed mt-3 min-h-[50px]">{s.detail}</p><p className="text-xs font-bold text-teal flex items-center gap-2 mt-5 group-hover:gap-3 transition-all">{s.link} <ArrowRight size={14}/></p></Link>
  })}</div><p className="text-xs text-slate-500 mt-2">Each scenario uses labeled synthetic data. The results are not official authentication or AICTE compliance decisions.</p></section>
  {error&&<div role="alert" className="text-red-700 border border-red-200 rounded-xl p-3 text-sm">Unable to fetch live case totals: {error}</div>}
  <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">{stats.map(s=><Card key={s.title} className="p-4"><s.icon size={19} className="text-teal mb-2"/><p className="text-xs font-semibold text-slate-500">{s.title}</p><p className="kpi-number mt-1">{s.value}</p><p className="text-[11px] text-slate-400 mt-1">{s.foot}</p></Card>)}</div>
  <div className="grid lg:grid-cols-[1.25fr_1fr] gap-5"><Card><SectionHeading title="What happens after a finding?" subtitle="From a detected inconsistency to a traceable review action"/><div className="space-y-3">{[
   {title:'Open case findings',detail:'See the rule ID, the two conflicting source values and their original PDF pages.',href:'/cases/1?tab=findings',cta:'Inspect the findings'},
   {title:'Review the evidence graph',detail:'Click the connected claim and extracted field to locate its supporting document.',href:'/cases/1?tab=graph',cta:'Open evidence graph'},
   {title:'Record an officer action',detail:'Confirm, dismiss with a reason, request evidence or escalate for inspection.',href:'/cases/1?tab=findings',cta:'Open review actions'},
  ].map((item,i)=><div className="flex gap-3 items-start border rounded-xl p-4" key={i}><span className="rounded-lg text-xs font-bold text-white bg-navy w-8 h-8 grid place-items-center flex-shrink-0">{i+1}</span><div><p className="font-bold text-navy text-sm">{item.title}</p><p className="text-xs leading-relaxed text-slate-600 mt-1">{item.detail}</p><Link className="text-xs font-semibold text-teal mt-2 inline-flex gap-1 items-center" href={item.href}>{item.cta} <ArrowRight size={13}/></Link></div></div>)}</div></Card>
   <Card><SectionHeading title="Officer queue distribution" subtitle="Transparent priority, not a fraud score"/><div className="h-56"><ResponsiveContainer width="100%" height="100%"><BarChart data={chart} margin={{top:5,right:12,left:-27,bottom:0}}><CartesianGrid strokeDasharray="3 6" vertical={false} stroke="#e9eff5"/><XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill:'#728297',fontSize:11}}/><YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{fill:'#728297',fontSize:11}}/><Tooltip/><Bar dataKey="cases" fill="#13A89E" radius={[6,6,0,0]} maxBarSize={48}/></BarChart></ResponsiveContainer></div><p className="text-xs border-t pt-3 text-slate-600">High × 5 + Medium × 3 + Low × 1. <b>Each contributing finding remains inspectable.</b></p><Link href="/cases" className="inline-flex gap-2 items-center mt-4 text-xs font-semibold text-teal">Open full case queue <ArrowUpRight size={14}/></Link></Card></div>
 </div>
}
