'use client'
import {createContext,useContext,useEffect,useState,type ReactNode} from 'react'
import {usePathname,useRouter} from 'next/navigation'
import Link from 'next/link'
import {LayoutDashboard,FolderOpen,ShieldCheck,DatabaseZap,ClipboardCheck,Scale,LogOut,Network,Menu,Languages,BookOpen,ChevronRight,PlayCircle} from 'lucide-react'
import {request} from '@/lib/api'
import {User} from '@/lib/types'
import {cn} from '@/lib/utils'
import {Button} from '@/components/ui/button'

type AuthContextType={user:User|null;refresh:()=>Promise<void>;logout:()=>void;lang:'EN'|'HI';setLang:(l:'EN'|'HI')=>void}
const AuthContext=createContext<AuthContextType>({user:null,refresh:async()=>{},logout:()=>{},lang:'EN',setLang:()=>{}})
export const useAuth=()=>useContext(AuthContext)
export function Shell({children}:{children:ReactNode}){
  const [user,setUser]=useState<User|null>(null)
  const [ready,setReady]=useState(false)
  const [expanded,setExpanded]=useState(false)
  const [lang,setLang]=useState<'EN'|'HI'>('EN')
  const pathname=usePathname(),router=useRouter()
  async function refresh(){try{setUser(await request<User>('/auth/me'))}catch{setUser(null)}finally{setReady(true)}}
  useEffect(()=>{refresh()},[])
  useEffect(()=>{if(ready&&!user&&pathname!=='/login')router.replace('/login')},[ready,user,pathname,router])
  function logout(){localStorage.removeItem('proofgraph_token');setUser(null);router.push('/login')}
  const items=[
    {href:'/',name:lang==='EN'?'Overview':'अवलोकन',icon:LayoutDashboard},
    {href:'/demo',name:lang==='EN'?'Interactive Demo':'इंटरैक्टिव डेमो',icon:PlayCircle},
    {href:'/cases',name:lang==='EN'?'Case Workbench':'केस कार्यक्षेत्र',icon:FolderOpen},
    {href:'/portal',name:lang==='EN'?'Institution Portal':'संस्थान पोर्टल',icon:ClipboardCheck},
    {href:'/evaluation',name:lang==='EN'?'Evaluation':'मूल्यांकन',icon:DatabaseZap},
    {href:'/rules',name:lang==='EN'?'Rule Library':'नियम संग्रह',icon:Scale},
    {href:'/audit',name:lang==='EN'?'Audit Trail':'ऑडिट ट्रेल',icon:ShieldCheck},
    {href:'/guide',name:lang==='EN'?'Demo Guide':'डेमो गाइड',icon:BookOpen}
  ]
  const isLogin=pathname==='/login'
  return <AuthContext.Provider value={{user,refresh,logout,lang,setLang}}>
    {isLogin?<>{children}</>:!ready||!user?<div className="min-h-screen flex items-center justify-center text-teal font-semibold">Loading secure demo workspace…</div>:
    <div className="min-h-screen md:pl-[250px]">
      {expanded&&<button aria-label="Close menu" onClick={()=>setExpanded(false)} className="fixed inset-0 bg-navy/60 z-30 md:hidden"/>}
      <aside className={cn('fixed z-40 inset-y-0 left-0 w-[250px] bg-navy text-white flex flex-col transition-transform md:translate-x-0',expanded?'translate-x-0':'-translate-x-full')}>
        <div className="px-6 pt-7 pb-8 border-b border-white/10">
          <Link href="/" onClick={()=>setExpanded(false)} className="flex items-center gap-3">
            <span className="w-10 h-10 grid place-items-center rounded-xl bg-teal/20 border border-teal/40"><Network size={23} strokeWidth={2.3} color="#72e6dc"/></span>
            <span><b className="block text-[19px] tracking-[-.04em]">ProofGraph</b><span className="block text-[10px] text-slate-300 tracking-wide">EVIDENCE INTELLIGENCE</span></span>
          </Link>
        </div>
        <div className="px-5 pt-6 pb-2 text-[10px] uppercase font-bold tracking-[.16em] text-slate-400">WORKSPACE</div>
        <nav className="flex-1 px-3 space-y-1">
          {items.filter(x=>!(['Evaluation','मूल्यांकन','Rule Library','नियम संग्रह','Audit Trail','ऑडिट ट्रेल'].includes(x.name)&&user.role==='Institution')).map(x=>{
            const active=x.href==='/'?pathname==='/':pathname.startsWith(x.href)
            return <Link key={x.href} href={x.href} onClick={()=>setExpanded(false)} className={cn('flex items-center gap-3 px-4 py-3 rounded-xl text-[13px] transition-colors',active?'bg-[#183e61] text-white font-bold border-l-[3px] border-teal':'text-slate-300 hover:text-white hover:bg-white/10')}><x.icon size={18} className={active?'text-[#5de1d1]':''}/>{x.name}{active&&<ChevronRight size={14} className="ml-auto"/>}</Link>
          })}
        </nav>
        <div className="p-4"><div className="bg-white/7 rounded-xl border border-white/10 p-3 mb-4"><div className="text-[10px] font-bold tracking-wider text-[#5fe4d6]">DEMONSTRATION BUILD</div><p className="mt-1 text-[11px] leading-relaxed text-slate-300">SIH 2026 · PS SIH26263<br/>Team Binary Battalion</p></div><button onClick={logout} className="flex gap-2 items-center px-3 py-2 text-xs text-slate-300 hover:text-white"><LogOut size={16}/> Sign out</button></div>
      </aside>
      <div className="sticky z-20 top-0 bg-white/95 backdrop-blur border-b border-slate-200">
        <div className="h-16 px-5 md:px-9 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3"><button className="md:hidden" onClick={()=>setExpanded(true)} aria-label="Open menu"><Menu/></button><div><p className="font-bold text-sm text-navy">ProofGraph Workspace</p><p className="text-[11px] text-slate-500">Smart Automation · SIH 2026</p></div></div>
          <div className="flex items-center gap-3"><button onClick={()=>setLang(lang==='EN'?'HI':'EN')} className="rounded-lg border px-2.5 py-2 text-xs flex items-center gap-1.5 hover:bg-slate-50" title="Toggle English / Hindi"><Languages size={15}/>{lang}</button><div className="hidden sm:flex items-center gap-2 border-l pl-4"><div className="bg-navy text-white font-semibold w-8 h-8 rounded-full grid place-items-center text-xs">{user.username.slice(0,2).toUpperCase()}</div><div><p className="font-semibold text-xs">{user.username}</p><p className="text-[10px] text-slate-500">{user.role}</p></div></div></div>
        </div>
        <div className="bg-[#fff8eb] border-t border-[#faedd0] px-4 md:px-9 py-2 text-[11px] text-[#895b23] flex items-center gap-2"><ShieldCheck size={13} className="flex-shrink-0"/><span>Prototype with synthetic data. Decisions rest with competent AICTE authorities. <b>Not an official AICTE system.</b></span></div>
      </div>
      <main className="max-w-[1570px] mx-auto p-5 md:p-9">{children}</main>
      <footer className="px-9 pb-6 text-[11px] text-slate-400">© 2026 ProofGraph prototype · Binary Battalion · Synthetic demonstration environment</footer>
    </div>}
  </AuthContext.Provider>
}
