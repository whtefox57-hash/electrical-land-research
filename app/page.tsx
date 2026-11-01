import DeskApp from './desk-app';
import Setup from './setup/page';
import {blobConfigured,createBlobStorage} from '@/lib/vercel-blob.mjs';
export const dynamic='force-dynamic';
export default async function Page(){
 if(!blobConfigured())return <Setup/>;
 try{if(!await createBlobStorage().get())return <Setup/>;}catch{return <Setup/>;}
 return <DeskApp/>;
}
