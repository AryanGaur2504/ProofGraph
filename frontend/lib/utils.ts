import {clsx,type ClassValue} from 'clsx'
import {twMerge} from 'tailwind-merge'
export function cn(...inputs:ClassValue[]){return twMerge(clsx(inputs))}
export function titlecase(s:string){return s.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}
