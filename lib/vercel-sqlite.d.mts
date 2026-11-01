export function openSQLite(bytes: Uint8Array): Promise<any>;
export function commitSQLite(session: any, expectedETag: string, storage: any): Promise<void>;
