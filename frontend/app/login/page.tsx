'use client'
import {useState} from 'react'
import {useRouter} from 'next/navigation'
import {Network,ShieldCheck,ArrowRight,Layers3,LockKeyhole} from 'lucide-react'
import {Button} from '@/components/ui/button'
import {API} from '@/lib/api'
import {useAuth} from '@/components/shell'
export default function Login(){
 const router=useRouter(),{refresh}=useAuth()
 const [username,setUsername]=useState('officer'),[password,setPassword]=useState('Demo@12345'),[error,setError]=useState(''),[busy,setBusy]=useState(false)
 async function signIn(e:React.FormEvent){e.preventDefault();setBusy(true);setError('');try{const r=await fetch(API+'/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,password})});const json=await r.json();if(!r.ok)throw new Error(json.detail||'Login failed');localStorage.setItem('proofgraph_token',json.access_token);await refresh();router.push('/')}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 return <div className="min-h-screen grid lg:grid-cols-[1.08fr_1fr] bg-white">
  <div className="hidden lg:flex flex-col justify-between p-12 xl:p-20 bg-navy text-white relative overflow-hidden"><div className="absolute pointer-events-none rounded-full w-[600px] h-[600px] border border-white/10 -right-80 top-20"/><div className="absolute pointer-events-none rounded-full w-[450px] h-[450px] border border-white/10 -right-56 top-40"/>
    <div className="flex gap-3 items-center"><span className="bg-teal/20 border border-teal/50 rounded-xl p-3"><Network color="#73e4d9"/></span><span><b className="text-2xl tracking-tight">ProofGraph</b><small className="block tracking-[.2em] text-slate-300 text-[10px]">EVIDENCE INTELLIGENCE</small></span></div>
    <div className="relative max-w-xl"><p className="text-[#6de1d3] uppercase tracking-[.25em] text-xs font-bold mb-6">Document review workspace</p><h1 className="text-5xl xl:text-[60px] leading-[1.08] font-bold tracking-[-.055em]">Every claim.<br/><span className="text-[#71e4db]">Connected to evidence.</span></h1><p className="text-slate-300 text-lg mt-7 leading-relaxed max-w-[450px]">From static document checks to explainable, cross-document scrutiny with historical change intelligence.</p><div className="grid grid-cols-2 gap-4 mt-11"><div className="flex items-center gap-3 border border-white/15 bg-white/5 rounded-2xl p-4"><Layers3 className="text-[#70e2d8]"/><span className="text-xs">Linked evidence graph</span></div><div className="flex items-center gap-3 border border-white/15 bg-white/5 rounded-2xl p-4"><ShieldCheck className="text-[#70e2d8]"/><span className="text-xs">Human-led decisions</span></div></div></div>
    <div className="text-xs text-slate-400">ProofGraph · Prototype workflow · Not an official AICTE service</div>
  </div>
  <div className="flex flex-col justify-center px-6 py-16 sm:px-16 xl:px-28"><div className="lg:hidden flex items-center gap-2 mb-16 text-navy"><Network className="text-teal"/> <b className="text-2xl">ProofGraph</b></div><p className="text-teal font-bold text-xs uppercase tracking-[.18em] mb-3">Secure review workspace</p><h2 className="text-4xl font-bold text-navy tracking-[-.04em]">Welcome back.</h2><p className="text-slate-500 text-sm mt-3 mb-10">Sign in to manage and validate documents.</p>
    <form onSubmit={signIn} className="space-y-5 max-w-[440px]"><label className="block"><span className="field-label">Username</span><input className="input w-full" value={username} onChange={e=>setUsername(e.target.value)} required/></label><label className="block"><span className="field-label">Password</span><input className="input w-full" type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></label>{error&&<p className="text-rose-700 text-xs" role="alert">{error}</p>}<Button disabled={busy} className="w-full py-3.5">{busy?'Signing in…':'Enter Workspace'} <ArrowRight size={17}/></Button></form>
    <p className="mt-7 text-xs text-slate-500 max-w-[440px]">Independent training system. Do not upload real institutional records or personal information.</p>
  </div>
 </div>
}
