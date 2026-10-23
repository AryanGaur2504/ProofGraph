'use client'
import {createContext,useContext,useEffect,useState,type ReactNode} from 'react'
import {usePathname,useRouter} from 'next/navigation'
import Link from 'next/link'
import {LayoutDashboard,FolderOpen,ShieldCheck,DatabaseZap,ClipboardCheck,Scale,LogOut,Network,Menu,Languages,BookOpen,ChevronRight,PlayCircle,Sun,Moon,FilePlus2,ChevronDown,HelpCircle} from 'lucide-react'
import {request} from '@/lib/api'
import {User} from '@/lib/types'
import {cn} from '@/lib/utils'

type AuthContextType={user:User|null;refresh:()=>Promise<void>;logout:()=>void;lang:'EN'|'HI';setLang:(l:'EN'|'HI')=>void;theme:'light'|'dark';toggleTheme:()=>void}
const AuthContext=createContext<AuthContextType>({user:null,refresh:async()=>{},logout:()=>{},lang:'EN',setLang:()=>{},theme:'light',toggleTheme:()=>{}})
export const useAuth=()=>useContext(AuthContext)
export function Shell({children}:{children:ReactNode}){
  const [user,setUser]=useState<User|null>(null)
  const [ready,setReady]=useState(false)
  const [expanded,setExpanded]=useState(false)
  const [lang,setLang]=useState<'EN'|'HI'>('EN')
  const [theme,setTheme]=useState<'light'|'dark'>('light')
  const [more,setMore]=useState(false)
  const pathname=usePathname(),router=useRouter()
  async function refresh(){try{setUser(await request<User>('/auth/me'))}catch{setUser(null)}finally{setReady(true)}}
  useEffect(()=>{refresh();const saved=localStorage.getItem('proofgraph-theme');const preference=saved==='dark'||(saved!=='light'&&window.matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light';setTheme(preference);document.documentElement.classList.toggle('dark',preference==='dark')},[])
  useEffect(()=>{if(ready&&!user&&pathname!=='/login')router.replace('/login')},[ready,user,pathname,router])
  function logout(){localStorage.removeItem('proofgraph_token');setUser(null);router.push('/login')}
  function toggleTheme(){setTheme(t=>{const next=t==='light'?'dark':'light';localStorage.setItem('proofgraph-theme',next);document.documentElement.classList.toggle('dark',next==='dark');return next})}
  const primary=[
    {href:'/',name:'Home',icon:LayoutDashboard},
    {href:'/check',name:'Upload & check',icon:FilePlus2},
    {href:'/cases',name:'Applications',icon:FolderOpen},
    {href:'/demo',name:'Try demo cases',icon:PlayCircle},
  ]
  const advanced=[
    {href:'/evaluation',name:'Evaluation',icon:DatabaseZap},
    {href:'/rules',name:'Sample rules',icon:Scale},
    {href:'/audit',name:'Audit trail',icon:ShieldCheck},
    {href:'/guide',name:'Demo guide',icon:BookOpen},
  ]
  const isLogin=pathname==='/login'
  function navLink(item:{href:string;name:string;icon:typeof Network}){const active=item.href==='/'?pathname==='/':pathname.startsWith(item.href);return <Link key={item.href} href={item.href} onClick={()=>setExpanded(false)} aria-current={active?'page':undefined} className={cn('flex items-center gap-3 px-4 py-3 rounded-xl text-[13px] transition-colors',active?'bg-[#183e61] text-white font-bold border-l-[3px] border-teal':'text-slate-300 hover:text-white hover:bg-white/10')}><item.icon size={18} className={active?'text-[#5de1d1]':''}/>{item.name}{active&&<ChevronRight size={14} className="ml-auto"/>}</Link>}
  return <AuthContext.Provider value={{user,refresh,logout,lang,setLang,theme,toggleTheme}}>
    {isLogin?<>{children}</>:!ready||!user?<div className="min-h-screen flex items-center justify-center text-teal font-semibold">Opening ProofGraph…</div>:
    <div className="min-h-screen md:pl-[250px]">
      {expanded&&<button aria-label="Close menu" onClick={()=>setExpanded(false)} className="fixed inset-0 bg-navy/60 z-30 md:hidden"/>}
      <aside className={cn('fixed z-40 inset-y-0 left-0 w-[250px] bg-navy text-white flex flex-col transition-transform md:translate-x-0',expanded?'translate-x-0':'-translate-x-full')}>
        <div className="px-6 pt-7 pb-6 border-b border-white/10"><Link href="/" onClick={()=>setExpanded(false)} className="flex items-center gap-3"><span className="w-10 h-10 grid place-items-center rounded-xl bg-teal/20 border border-teal/40"><Network size={23} color="#72e6dc"/></span><span><b className="block text-[19px] tracking-[-.04em]">ProofGraph</b><span className="block text-[10px] text-slate-300">DOCUMENT REVIEW, SIMPLIFIED</span></span></Link></div>
        <nav aria-label="Main navigation" className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
          <div className="px-4 text-[10px] mb-3 uppercase font-bold tracking-[.16em] text-slate-400">Start here</div>
          {primary.map(navLink)}
          <div className="pt-5"><button aria-expanded={more} onClick={()=>setMore(!more)} className="flex w-full items-center justify-between px-4 py-3 rounded-xl text-slate-300 hover:bg-white/10 text-xs font-semibold"><span className="flex items-center gap-2"><ChevronDown size={15} className={cn('transition-transform',more?'rotate-180':'')}/>Advanced tools</span><span className="text-[10px] text-slate-400">Optional</span></button>{more&&<div className="mt-1 space-y-1">{advanced.filter(x=>user.role!=='Institution'||['/guide'].includes(x.href)).map(navLink)}</div>}</div>
        </nav>
        <div className="p-4 border-t border-white/10"><p className="text-[11px] text-slate-300 mb-3">New here? Open <Link href="/demo" className="font-semibold text-[#6de1d5] underline">Try demo cases</Link>.</p><button onClick={logout} className="flex gap-2 items-center px-3 py-2 text-xs text-slate-300 hover:text-white"><LogOut size={16}/> Sign out</button></div>
      </aside>
      <header className="sticky z-20 top-0 bg-white/95 backdrop-blur border-b border-slate-200">
        <div className="min-h-16 px-4 md:px-8 py-3 flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-3"><button className="md:hidden p-2" onClick={()=>setExpanded(true)} aria-label="Open menu"><Menu/></button><div><p className="font-bold text-sm text-navy">ProofGraph Workspace</p><p className="text-[11px] text-slate-500">Check documents and review evidence</p></div></div>
          <div className="flex items-center gap-2"><Link href="/check" className="inline-flex gap-1.5 items-center bg-teal text-white rounded-xl px-3 py-2.5 font-bold text-xs hover:opacity-90"><FilePlus2 size={15}/> Upload documents</Link><button onClick={toggleTheme} aria-label={theme==='dark'?'Use light theme':'Use dark theme'} title={theme==='dark'?'Light theme':'Dark theme'} className="rounded-lg border border-slate-200 p-2.5 hover:bg-slate-100">{theme==='dark'?<Sun size={17}/>:<Moon size={17}/>}</button><button onClick={()=>setLang(lang==='EN'?'HI':'EN')} className="hidden sm:flex rounded-lg border border-slate-200 px-2 py-2.5 text-xs items-center gap-1" title="English / Hindi"><Languages size={15}/>{lang}</button><span className="text-[11px] hidden lg:inline text-slate-500 border-l pl-3">{user.role}</span></div>
        </div>
        <div className="demo-banner bg-[#fff8eb] border-t border-[#faedd0] px-4 md:px-8 py-2 text-[11px] text-[#895b23] flex items-center gap-2"><ShieldCheck size={14} className="shrink-0"/> Synthetic demo only. This is not an official AICTE service; human review is required.</div>
      </header>
      <main className="max-w-[1500px] mx-auto p-4 md:p-8">{children}</main>
      <footer className="px-8 pb-6 text-[11px] text-slate-400">ProofGraph · Binary Battalion · SIH 2026 · Fictional data only</footer>
    </div>}
  </AuthContext.Provider>
}
