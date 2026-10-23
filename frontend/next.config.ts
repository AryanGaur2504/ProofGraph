import type { NextConfig } from 'next'

const config: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // The container runs FastAPI privately on port 8000 and exposes only Next.js.
  // This keeps browser API requests on the same public origin.
  async rewrites() {
    return [{ source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' }]
  },
}
export default config
