'use client'
import {createContext,useContext,useEffect,useState,type ReactNode} from 'react'
import {usePathname,useRouter} from 'next/navigation'
import Link from 'next/link'
import {LayoutDashboard,FolderOpen,LogOut,Network,Menu,Sun,Moon,FilePlus2,ChevronDown,BookOpen,ShieldCheck,Scale,DatabaseZap,ArrowRight} from 'lucide-react'
import {request} from '@/lib/api'
import {User} from '@/lib/types'
import {cn} from '@/lib/utils'

type Context={user:User|null;refresh:()=>Promise<void>;logout:()=>void;lang:'EN'|'HI';setLang:(x:'EN'|'HI')=>void;theme:'light'|'dark';toggleTheme:()=>void}
const AuthContext=createContext<Context>({user:null,refresh:async()=>{},logout:()=>{},lang:'EN',setLang:()=>{},theme:'light',toggleTheme:()=>{}})
export const useAuth=()=>useContext(AuthContext)
export function Shell({children}:{children:ReactNode}){
 const [user,setUser]=useState<User|null>(null),[ready,setReady]=useState(false),[drawer,setDrawer]=useState(false),[advanced,setAdvanced]=useState(false)
 const [theme,setTheme]=useState<'light'|'dark'>('light'),[lang,setLang]=useState<'EN'|'HI'>('EN')
 const pathname=usePathname(),router=useRouter()
 async function refresh(){try{setUser(await request<User>('/auth/me'))}catch{setUser(null)}finally{setReady(true)}}
 useEffect(()=>{refresh();const saved=localStorage.getItem('proofgraph-theme');const dark=saved==='dark'||(saved!=='light'&&window.matchMedia('(prefers-color-scheme: dark)').matches);setTheme(dark?'dark':'light');document.documentElement.classList.toggle('dark',dark)},[])
 useEffect(()=>{if(ready&&!user&&pathname!=='/login')router.replace('/login')},[ready,user,pathname,router])
 function toggleTheme(){setTheme(v=>{const n=v==='light'?'dark':'light';document.documentElement.classList.toggle('dark',n==='dark');localStorage.setItem('proofgraph-theme',n);return n})}
 function logout(){localStorage.removeItem('proofgraph_token');setUser(null);router.push('/login')}
 const links=[{href:'/',name:'Home',icon:LayoutDashboard},{href:'/check',name:'Upload & validate',icon:FilePlus2},{href:'/cases',name:'Applications',icon:FolderOpen}]
 const more=[{href:'/rules',name:'Validation rules',icon:Scale},{href:'/audit',name:'Activity log',icon:ShieldCheck},{href:'/evaluation',name:'Quality checks',icon:DatabaseZap},{href:'/guide',name:'Help',icon:BookOpen}]
 const nav=(item:{href:string;name:string;icon:typeof Network})=>{const active=item.href==='/'?pathname==='/':pathname.startsWith(item.href);return <Link href={item.href} key={item.href} aria-current={active?'page':undefined} onClick={()=>setDrawer(false)} className={cn('flex gap-3 items-center rounded-xl px-4 py-3.5 text-sm',active?'bg-white/15 text-white font-bold':'text-slate-300 hover:bg-white/10 hover:text-white')}><item.icon size={19}/>{item.name}{active&&<ArrowRight size={14} className="ml-auto"/>}</Link>}
 if(pathname==='/login')return <AuthContext.Provider value={{user,refresh,logout,lang,setLang,theme,toggleTheme}}>{children}</AuthContext.Provider>
 return <AuthContext.Provider value={{user,refresh,logout,lang,setLang,theme,toggleTheme}}>{!ready||!user?<div className="min-h-screen flex items-center justify-center text-teal">Opening ProofGraph…</div>:
 <div className="min-h-screen md:pl-[248px]">
  {drawer&&<button className="fixed z-30 inset-0 bg-black/60 md:hidden" aria-label="Close menu" onClick={()=>setDrawer(false)}/>}
  <aside className={cn('fixed z-40 inset-y-0 left-0 w-[248px] bg-navy text-white flex flex-col transition-transform md:translate-x-0',drawer?'translate-x-0':'-translate-x-full')}>
   <div className="px-5 py-7 border-b border-white/10"><Link href="/" onClick={()=>setDrawer(false)} className="flex gap-3 items-center"><span className="p-2.5 bg-teal/20 rounded-xl"><Network size={25} className="text-[#70e4d9]"/></span><span><b className="block text-xl">ProofGraph</b><small className="text-slate-300 text-[11px]">Document validation</small></span></Link></div>
   <nav className="flex-1 overflow-y-auto p-3 space-y-1" aria-label="Main menu">{links.map(nav)}<div className="pt-5"><button className="px-4 py-3 flex gap-2 w-full items-center text-slate-300 text-xs" onClick={()=>setAdvanced(!advanced)} aria-expanded={advanced}><ChevronDown size={17} className={cn('transition-transform',advanced&&'rotate-180')}/>Advanced features (optional)</button>{advanced&&more.filter(x=>user.role!=='Institution'||x.href==='/guide').map(nav)}</div></nav>
   <div className="p-4 border-t border-white/10"><p className="text-[11px] text-slate-300 mb-2">{user.role}</p><button onClick={logout} className="flex items-center gap-2 text-slate-300 hover:text-white text-sm py-2"><LogOut size={16}/> Sign out</button></div>
  </aside>
  <header className="sticky z-20 top-0 bg-white border-b border-slate-200"><div className="mx-auto max-w-[1300px] px-4 md:px-8 min-h-[72px] flex items-center justify-between gap-3"><div className="flex items-center gap-3"><button onClick={()=>setDrawer(true)} aria-label="Open menu" className="md:hidden p-2"><Menu size={21}/></button><div><p className="text-sm font-bold text-navy">Document review workspace</p><p className="text-xs text-slate-500 hidden sm:block">Upload, validate, and resolve differences</p></div></div><div className="flex items-center gap-2"><Link href="/check" className="bg-teal text-white text-xs sm:text-sm font-bold px-3 sm:px-4 py-3 rounded-xl hover:opacity-90"><FilePlus2 size={16} className="inline mr-1"/> New check</Link><button className="p-3 rounded-xl border border-slate-200" onClick={toggleTheme} title={theme==='dark'?'Switch to light mode':'Switch to dark mode'} aria-label={theme==='dark'?'Switch to light mode':'Switch to dark mode'}>{theme==='dark'?<Sun size={18}/>:<Moon size={18}/>}</button></div></div></header>
  <main className="mx-auto max-w-[1300px] p-4 md:p-8">{children}</main>
  <footer className="px-5 md:px-8 pb-5 text-[11px] text-slate-400">ProofGraph · Automated checks support human review. Sample rule checks do not establish official document authenticity or regulatory approval.</footer>
 </div>}</AuthContext.Provider>
}
