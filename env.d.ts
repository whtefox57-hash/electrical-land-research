/// <reference types="vite/client" />
declare module 'cloudflare:workers' { export const env: Record<string, any>; }
interface Fetcher { fetch(request: Request): Promise<Response>; }
interface D1Database { prepare(query:string): any; batch(queries:any[]):Promise<any[]>; }
