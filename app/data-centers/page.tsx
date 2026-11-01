import DataCenterRegistry from '@/components/data-center-registry';
export const dynamic='force-dynamic';
export default function Page(){return <main style={{padding:'24px',maxWidth:1800,margin:'auto'}}><a href="/?view=today" className="dc-link">← Deal Desk</a><DataCenterRegistry/></main>}
