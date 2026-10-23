export const API=process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://127.0.0.1:8000/api')
export function token(){return typeof window==='undefined'?'':localStorage.getItem('proofgraph_token')||''}
export async function request<T>(url:string,opts:RequestInit={}):Promise<T>{
  const headers:Record<string,string>={Authorization:`Bearer ${token()}`,...(opts.headers as Record<string,string>||{})}
  if(opts.body && !(opts.body instanceof FormData)) headers['Content-Type']='application/json'
  const res=await fetch(API+url,{...opts,headers,cache:'no-store'})
  if(!res.ok){const data=await res.json().catch(()=>({})); throw new Error(data.detail || `Request failed (${res.status})`)}
  return res.json()
}
export async function documentBlob(id:number):Promise<Blob>{
  const res=await fetch(`${API}/documents/${id}/file`,{headers:{Authorization:`Bearer ${token()}`}})
  if(!res.ok)throw new Error('Document access denied')
  return res.blob()
}
export async function reportBlob(reportId:number):Promise<Blob>{
  const res=await fetch(`${API}/reports/${reportId}/file`,{headers:{Authorization:`Bearer ${token()}`}})
  if(!res.ok)throw new Error('Report download unavailable')
  return res.blob()
}
export function saveBlob(blob:Blob,name:string){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
