import batch from '@/data/research-sept26/listings.json';
import excludedSources from '@/data/research-sept26/excluded-sources.json';

export const SEPT26_BATCH='listing-50-sept26';
export const sept26Candidates:any[]=batch.listings.map(d=>({
 id:`sep26-${d.state.toLowerCase()}-${String(d.id).padStart(2,'0')}`,batch:SEPT26_BATCH,rank:d.id,
 name:d.site,state:d.state,county:'Jurisdiction to verify',acres:d.acres,price:d.price,
 apns:/^(unknown|unresolved|not |request|new split)/i.test(d.apn)?[]:[d.apn],apnStatus:d.apn+' — listing identifier, not title verified',
 listingUrl:d.url,checkedAt:batch.as_of,listingStatus:'Online offering reviewed; seller has not confirmed availability',
 marketingDate:d.date,marketingDateNote:d.date_note,priceNote:d.date_note+'; advertised price and offered scope require confirmation.',
 why:d.positive,risk:d.gate,market:d.market,power:d.utility+'; firm 20–30 MW, delivery date and upgrade cost unverified.',
 fiber:d.fiber+'; route diversity, capacity, cost and latency unverified.',
 phaseMW:'20–30 MW inference hypothesis; IT versus facility load not validated',
 nextTest:'Confirm still available, current price, exact offered APNs and seller willingness to authorize preliminary inquiries. '+d.gate,
 recommendation:d.tier==='CALL FIRST'?'CALL SPRINT':'HOLD / RESEARCH',callTier:d.tier,
 assignmentAssessment:{status:'NOT ESTIMABLE',percent:null,reason:batch.common_unknowns,definition:'No calibrated probability or assignment premium is supported.'},
 contacts:[{role:d.contact_type,name:d.contact,phone:d.phone,url:d.url,note:'Listing contact; reconfirm current representation.'},{role:'Planning / local government',name:'Exact jurisdiction and contact unresolved',phone:null,url:null,note:'Obtain the correct planning contact after confirming the offered APNs.'},{role:'Electric utility',name:d.utility,phone:null,url:null,note:'Territory and large-load representative must be confirmed for the exact parcel.'}],
 supporting:'secondary_url' in d&&d.secondary_url?[['Secondary listing evidence',d.secondary_url]]:[],
 missing:[batch.common_unknowns],ratings:{},location:null,
 option:{initialFee:1000,extensionFee:2000,initialDays:180,extensionDays:180,controlExposure:3000},
}));

export const sept26Run={id:'sept26-listing-50',date:batch.as_of,completedAt:batch.as_of,timezone:'UTC · research date; completion time not recorded',
 title:'50 additional listing leads · September 26',summary:batch.scope+' '+batch.buyer_hypothesis+' '+batch.common_unknowns,
 newIds:sept26Candidates.map(d=>d.id),updatedIds:[],statesReviewed:[...new Set(batch.listings.map(d=>d.state))],
 rejected:batch.excluded.map(d=>({name:d.site,status:'EXCLUDED FROM THIS RUN',reason:d.reason,source:(excludedSources as Record<string,string|null>)[d.ref]||null})),holds:[],
 delivery:'Founder-requested research published through a site update; not an automated delivery receipt.',
 coverage:[{source:'Bounded public listing search',status:'PARTIAL',detail:batch.scope,url:null}],
};
