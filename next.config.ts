import type { NextConfig } from 'next';
const config:NextConfig={outputFileTracingRoot:process.cwd(),serverExternalPackages:['node:sqlite'],outputFileTracingExcludes:{'*':['./.git/**','./.wrangler/**','./.sites-runtime/**','./outputs/**']}};
export default config;
