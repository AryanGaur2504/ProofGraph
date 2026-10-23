'use client'
import {useEffect,useState} from 'react'
import {Document as PDFDocument,Page,pdfjs} from 'react-pdf'
import {documentBlob} from '@/lib/api'
import {Doc,Evidence} from '@/lib/types'
import {Status} from '@/components/ui/card'
import {FileText,Image as ImageIcon} from 'lucide-react'

pdfjs.GlobalWorkerOptions.workerSrc=new URL('pdfjs-dist/build/pdf.worker.min.mjs',import.meta.url).toString()
export default function DocumentViewer({doc,evidence,width=520}:{doc:Doc|undefined;evidence?:Evidence|null;width?:number}){
 const [uri,setUri]=useState(''),[error,setError]=useState(''),[pageWidth,setPageWidth]=useState(595),[pageHeight,setPageHeight]=useState(842)
 const pageNum=evidence?.page||1
 useEffect(()=>{let alive=true;let url='';setUri('');setError('');if(doc){documentBlob(doc.id).then(blob=>{url=URL.createObjectURL(blob);if(alive)setUri(url);else URL.revokeObjectURL(url)}).catch(e=>{if(alive)setError(e.message)})}return()=>{alive=false;if(url)URL.revokeObjectURL(url)}},[doc?.id])
 if(!doc)return <div className="border border-dashed rounded-xl p-10 text-center text-sm text-slate-400">Select a source document</div>
 if(error)return <p className="text-rose-700 text-xs">{error}</p>
 const bb=evidence?.document_id===doc.id?evidence.bbox:undefined
 const hasHighlight=!!bb&&bb.length===4
 const highlight=hasHighlight?{left:`${Math.max(0,bb![0])/pageWidth*100}%`,top:`${Math.max(0,bb![1])/pageHeight*100}%`,width:`${Math.max(0,(bb![2]-bb![0]))/pageWidth*100}%`,height:`${Math.max(0,(bb![3]-bb![1]))/pageHeight*100}%`}:undefined
 return <div className="min-w-0"><div className="mb-3 flex items-center gap-2"><span className="text-teal">{doc.mime==='application/pdf'?<FileText size={17}/>:<ImageIcon size={17}/>}</span><div className="min-w-0"><p className="text-xs font-bold text-navy truncate">{doc.name}</p><p className="text-[10px] text-slate-500">{doc.kind} · page {pageNum} · synthetic</p></div></div>
 {hasHighlight&&<div className="mb-2"><Status tone="amber">Highlighted extracted region · not authenticated</Status></div>}
 {!uri?<p className="text-xs p-6 text-slate-400">Loading protected source file…</p>:doc.mime==='application/pdf'?<div className="overflow-auto rounded-xl border bg-slate-100 p-2 max-h-[680px]"><PDFDocument file={uri} loading={<p className="p-6 text-sm">Rendering PDF…</p>} error={<p className="p-4 text-red-600 text-xs">Unable to render PDF. View the source from a local PDF reader.</p>}><div className="pdf-doc" style={{width}}><Page pageNumber={pageNum} width={width} renderTextLayer={false} renderAnnotationLayer={false} onLoadSuccess={p=>{setPageWidth(p.view[2]-p.view[0]);setPageHeight(p.view[3]-p.view[1])}}/>{highlight&&<div title="Extracted region" className="absolute border-[3px] border-rose-500 bg-rose-500/20 pointer-events-none" style={highlight}/>}</div></PDFDocument></div>:<div className="relative inline-block max-w-full border rounded-xl overflow-hidden"><img alt="Uploaded infrastructure evidence" src={uri} className="block max-w-full h-auto"/>{highlight&&<div className="absolute border-[3px] border-rose-500 bg-rose-500/20 pointer-events-none" style={highlight}/>}</div>}
 <p className="text-[10px] text-slate-400 mt-2">Bounding boxes derive from extracted page coordinates. Officer must inspect the underlying source.</p>
 </div>
}
