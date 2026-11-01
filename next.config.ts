import type { NextConfig } from 'next';
const config:NextConfig={serverExternalPackages:['node:sqlite'],outputFileTracingExcludes:{'*':['./.git/**','./.wrangler/**','./.sites-runtime/**','./outputs/**']}};
export default config;
