'use client'

import {useMemo,useState} from 'react'
// @xyflow/react v12 exposes ReactFlow as a NAMED export, not the default export.
// A default import resolves to undefined at runtime and crashes this component.
import {ReactFlow,Background,Controls,MiniMap,MarkerType,type Edge,type Node} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type {Evidence,Graph} from '@/lib/types'
import {Status} from '@/components/ui/card'
import {ExternalLink,GitBranch,Network} from 'lucide-react'

type GraphNode=Graph['nodes'][number]
const colors:Record<string,{bg:string;border:string;text:string}>={
 Institution:{bg:'#0b2545',border:'#0b2545',text:'#fff'},
 Application:{bg:'#1d5478',border:'#1d5478',text:'#fff'},
 Document:{bg:'#e5f3fa',border:'#aad4e9',text:'#0b4265'},
 Claim:{bg:'#e8f8f6',border:'#a9e1da',text:'#087a71'},
 ExtractedField:{bg:'#fff',border:'#a5b3c4',text:'#334155'},
 Finding:{bg:'#fff0ed',border:'#eeb6ac',text:'#af2e20'},
 Rule:{bg:'#f0edff',border:'#c4b5fd',text:'#6445a3'},
 OfficialRecord:{bg:'#fff8e8',border:'#e9c879',text:'#815711'},
}
const rowOrder:Record<string,number>={Institution:0,Application:1,OfficialRecord:2,Document:3,ExtractedField:4,Claim:5,Finding:6,Rule:7}
function toEvidence(node:GraphNode):Evidence {
 return {document_id:Number(node.data?.document_id),page:Number(node.data?.page)||1,bbox:Array.isArray(node.data?.bbox)?node.data.bbox:[],field:node.label}
}

export function EvidenceGraph({data,onEvidence}:{data:Graph;onEvidence:(source:Evidence)=>void}) {
 const [mode,setMode]=useState<'issues'|'all'>('issues')
 const [selectedId,setSelectedId]=useState<string|null>(null)
 const contradictions=data.edges.filter(e=>e.type==='contradicts')
 const issueRoots=new Set<string>([...contradictions.flatMap(e=>[e.source,e.target]),...data.nodes.filter(n=>n.type==='Finding').map(n=>n.id)])
 const hasIssues=issueRoots.size>0
 const filtered=useMemo(()=>{
  if(mode==='all'||!hasIssues)return data
  const ids=new Set(issueRoots)
  // Show immediate evidence neighbors, not the entire institutional graph.
  for(const edge of data.edges){
   if(issueRoots.has(edge.source))ids.add(edge.target)
   if(issueRoots.has(edge.target))ids.add(edge.source)
  }
  return {nodes:data.nodes.filter(n=>ids.has(n.id)),edges:data.edges.filter(e=>ids.has(e.source)&&ids.has(e.target))}
 },[data,mode,hasIssues])
 const elements=useMemo(()=>{
  const grouped:Record<string,number>={}
  const nodes:Node[]=filtered.nodes.map(n=>{
   const index=grouped[n.type]||0
   grouped[n.type]=index+1
   const color=colors[n.type]||colors.ExtractedField
   return {
    id:n.id,position:{x:50+index*238,y:30+(rowOrder[n.type]??8)*148},
    data:{label:<div><span style={{fontSize:9,opacity:.76,display:'block',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:5}}>{n.type.replace(/([a-z])([A-Z])/g,'$1 $2')}</span><span style={{fontSize:11,fontWeight:700,overflowWrap:'anywhere'}}>{n.label.slice(0,110)}</span></div>},
    style:{background:color.bg,border:`${selectedId===n.id?3:1.5}px solid ${selectedId===n.id?'#13a89e':color.border}`,borderRadius:12,color:color.text,minWidth:195,maxWidth:205,padding:12,boxShadow:'0 4px 14px #172b4d12'},
   }
  })
  const edges:Edge[]=filtered.edges.map(e=>({
   id:e.id,source:e.source,target:e.target,
   label:e.type==='contradicts'?'CONTRADICTION':undefined,
   animated:e.type==='contradicts',
   style:{stroke:e.type==='contradicts'?'#dc423c':e.type==='extracted_from'?'#92a6b6':'#13a89e',strokeWidth:e.type==='contradicts'?3:1.5},
   markerEnd:{type:MarkerType.ArrowClosed,color:e.type==='contradicts'?'#dc423c':'#91a4ad'},
   labelStyle:{fill:'#aa2625',fontWeight:700,fontSize:10}
  }))
  return {nodes,edges}
 },[filtered,selectedId])
 const selected=data.nodes.find(n=>n.id===selectedId)
 const selectedHasSource=selected?.data?.document_id!=null
 return <div className="space-y-4">
  <div className="rounded-xl border border-slate-200 bg-[#f7fafc] p-4 flex gap-3 items-start">
   <GitBranch className="text-teal flex-shrink-0" size={21}/>
   <div><p className="text-sm font-bold text-navy">What you are seeing</p><p className="text-xs mt-1 text-slate-600 leading-relaxed">Every box is a claim, extracted PDF field, rule, document or finding. Lines show how they relate. <b>Red lines are disagreements between sources, not proof of fraud.</b> Click any box to see its details; open its source PDF when available.</p></div>
  </div>
  <div className="flex flex-wrap items-center justify-between gap-3">
   <div className="flex gap-2 flex-wrap"><Status tone="red">{contradictions.length} contradictory links</Status><Status tone="teal">{data.nodes.length} evidence nodes</Status><Status>{data.edges.length} relationships</Status></div>
   <div className="flex border rounded-xl p-1 bg-white" aria-label="Evidence graph view">
    <button className={`text-xs font-semibold rounded-lg px-3 py-2 ${mode==='issues'?'bg-navy text-white':'text-slate-600'}`} onClick={()=>setMode('issues')}>Relevant evidence</button>
    <button className={`text-xs font-semibold rounded-lg px-3 py-2 ${mode==='all'?'bg-navy text-white':'text-slate-600'}`} onClick={()=>setMode('all')}>All relationships</button>
   </div>
  </div>
  {!hasIssues&&<p className="text-xs text-slate-500">No contradiction or finding nodes. Showing the complete evidence graph.</p>}
  {filtered.nodes.length?<div className="graph-box border rounded-2xl overflow-hidden relative bg-[#fbfdfe]">
   <ReactFlow key={mode} nodes={elements.nodes} edges={elements.edges} fitView fitViewOptions={{padding:0.2,maxZoom:1.05}} onNodeClick={(_,clicked)=>setSelectedId(clicked.id)} nodesDraggable={false} nodesConnectable={false} minZoom={0.12} maxZoom={2}>
    <Background gap={20} size={1} color="#edf2f5"/><Controls/><MiniMap nodeColor={n=>colors[data.nodes.find(x=>x.id===n.id)?.type||'']?.bg||'#fff'} zoomable pannable/>
   </ReactFlow>
  </div>:<div className="border rounded-xl p-10 text-center text-slate-500 text-sm"><Network className="mx-auto mb-3"/>No evidence relationships available yet. Upload a document to create graph nodes.</div>}
  {selected&&<div className="border border-teal/25 bg-[#f4fbfa] p-4 rounded-xl flex flex-wrap items-center justify-between gap-3" role="status">
   <div className="min-w-0"><p className="text-[11px] font-bold text-teal uppercase tracking-wider">Selected {selected.type.replace(/([a-z])([A-Z])/g,'$1 $2')}</p><p className="text-sm font-bold mt-1 text-navy break-words">{selected.label}</p>{selectedHasSource&&<p className="text-xs text-slate-500 mt-2">Evidence: document #{selected.data.document_id} · page {selected.data.page||1} · extracted region recorded</p>}</div>
   {selectedHasSource?<button type="button" className="flex gap-2 items-center rounded-xl bg-navy text-white px-4 py-2.5 font-semibold text-xs" onClick={()=>onEvidence(toEvidence(selected))}>View highlighted PDF <ExternalLink size={14}/></button>:<p className="text-xs text-slate-500">This node has no direct source page. Select a connected field or document instead.</p>}
  </div>}
 </div>
}
