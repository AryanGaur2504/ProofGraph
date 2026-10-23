import type {Metadata} from 'next'
import './globals.css'
import {Shell} from '@/components/shell'
export const metadata:Metadata={title:'ProofGraph | Evidence Intelligence',description:'Synthetic evidence-linked institutional application scrutiny prototype for SIH26263'}
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><Shell>{children}</Shell></body></html>}
