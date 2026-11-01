export type BuyerSource = {title:string;url:string;publisher:string;date:string|null;retrieved:string};
export type Buyer = {
 id:string;name:string;parentGroup:string;role:string;usRelevance:string;regions:string[];
 strategy:string;scale:string;publishedRequirements:{fact:string;sourceUrl:string;kind:string}[];
 inferredPreferences:string[];differentiators:string[];dealStructure:string;acquisitionSignal:string;
 searchBrief:string;rejectionTriggers:string[];buyerQuestions:string[];sources:BuyerSource[];
 lane:string;priority:string;matchStatus:string;noMatchReason:string;
};
export type SiteMatch = {buyerId:string;low:number|null;high:number|null;base:number|null;rationale:string;rejection:string;raiseIf:string;powerScenario:string;scenarioHold:string;assumptionInputs:{stage:string;low:number;base:number;high:number}[]};
export type BuyerSite = {
 id:string;name:string;location:string;state:string;address:string;acreage:number|null;
 askingPrice:number|null;priceNote:string;apn:string|null;apnStatus:string;listingUrl:string;
 sourceUrls:string[];status:string;evidenceDate:string;availabilityNote:string;powerClaim:string;
 powerVerified:boolean;fitRationale:string;blockers:string[];controlFeasibility:string;nextProof:string;
 lane:string;capitalLane:string;rank:number;matches:SiteMatch[];
};
export type BuyerResearch = {asOf:string;buyers:Buyer[];sites:BuyerSite[];summary:string;methodology:{event:string;assumptions:string[];limitations:string[]};actions:{title:string;contactUrl:string;contactLabel:string;why:string;script:string;voicemail:string;questions:string[];success:string;stop:string}[]};
