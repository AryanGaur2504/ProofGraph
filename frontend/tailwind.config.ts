import type { Config } from 'tailwindcss'
export default {
  content:['./app/**/*.{ts,tsx}','./components/**/*.{ts,tsx}'],
  theme:{extend:{colors:{navy:'#0B2545',teal:'#13A89E',subtle:'#F6F8FC',ink:'#172B4D'},fontFamily:{sans:['Inter','ui-sans-serif','system-ui']},boxShadow:{panel:'0 3px 20px rgba(30,50,85,.045)'}}},
  plugins:[]
} satisfies Config
