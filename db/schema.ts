import { sqliteTable, text, integer, real, index } from 'drizzle-orm/sqlite-core';
export const workspace = sqliteTable('workspace', {id:text('id').primaryKey(), data:text('data').notNull(), version:integer('version').notNull().default(1)});
export const documents = sqliteTable('documents',{id:text('id').primaryKey(), name:text('name').notNull(), mime:text('mime').notNull(), content:text('content').notNull(), hash:text('hash').notNull()});
export const snapshots = sqliteTable('snapshots',{id:text('id').primaryKey(), data:text('data').notNull(), version:integer('version').notNull(), createdAt:text('created_at').notNull()});

// Listing intake is separate from founder-approved opportunities and capital decisions.
export const originationRecords = sqliteTable('origination_records', {
 id:text('id').primaryKey(), kind:text('kind').notNull(), state:text('state'), county:text('county'),
 disposition:text('disposition'), stage:text('stage'), data:text('data').notNull(),
 version:integer('version').notNull().default(1), updatedAt:text('updated_at').notNull(),
}, table => [index('origination_kind_state_idx').on(table.kind,table.state), index('origination_disposition_idx').on(table.kind,table.disposition), index('origination_county_idx').on(table.county)]);
export const originationRuns = sqliteTable('origination_runs', {
 id:text('id').primaryKey(), hash:text('hash').notNull(), data:text('data').notNull(), createdAt:text('created_at').notNull(),
});
export const originationEvents = sqliteTable('origination_events', {
 id:text('id').primaryKey(), runId:text('run_id').notNull(), recordId:text('record_id').notNull(),
 previousData:text('previous_data'), data:text('data').notNull(), createdAt:text('created_at').notNull(),
});

// Atlas records never overwrite the founder's workspace or origination register.
export const atlasEntities = sqliteTable('atlas_entities', {
 id:text('id').primaryKey(),kind:text('kind').notNull(),data:text('data').notNull(),version:integer('version').notNull().default(1),updatedAt:text('updated_at').notNull(),
},t=>[index('atlas_entities_kind_idx').on(t.kind)]);
export const atlasParcels = sqliteTable('atlas_parcels', {
 id:text('id').primaryKey(),countyFips:text('county_fips').notNull(),apn:text('apn').notNull(),state:text('state').notNull(),county:text('county').notNull(),sourceId:text('source_id').notNull(),
 minx:real('minx').notNull(),miny:real('miny').notNull(),maxx:real('maxx').notNull(),maxy:real('maxy').notNull(),geometry:text('geometry').notNull(),data:text('data').notNull(),version:integer('version').notNull().default(1),updatedAt:text('updated_at').notNull(),
},t=>[index('atlas_parcels_bbox_idx').on(t.minx,t.maxx,t.miny,t.maxy),index('atlas_parcels_apn_idx').on(t.countyFips,t.apn)]);
export const atlasResults = sqliteTable('atlas_results', {
 id:text('id').primaryKey(),parcelId:text('parcel_id').notNull(),profileId:text('profile_id').notNull(),color:text('color').notNull(),data:text('data').notNull(),inputHash:text('input_hash').notNull(),computedAt:text('computed_at').notNull(),
},t=>[index('atlas_results_profile_idx').on(t.profileId,t.color),index('atlas_results_parcel_idx').on(t.parcelId)]);
export const atlasRuns = sqliteTable('atlas_runs',{id:text('id').primaryKey(),hash:text('hash').notNull(),data:text('data').notNull(),createdAt:text('created_at').notNull()});
export const atlasEvents = sqliteTable('atlas_events',{id:text('id').primaryKey(),parcelId:text('parcel_id'),eventType:text('event_type').notNull(),previousData:text('previous_data'),data:text('data').notNull(),createdAt:text('created_at').notNull()},t=>[index('atlas_events_parcel_idx').on(t.parcelId,t.createdAt)]);
export const atlasJobs = sqliteTable('atlas_jobs',{id:text('id').primaryKey(),kind:text('kind').notNull(),state:text('state').notNull(),data:text('data').notNull(),leaseToken:text('lease_token'),leaseUntil:text('lease_until'),updatedAt:text('updated_at').notNull()});
export const atlasOutbox = sqliteTable('atlas_outbox',{id:text('id').primaryKey(),eventKey:text('event_key').notNull().unique(),data:text('data').notNull(),status:text('status').notNull().default('PENDING'),attempts:integer('attempts').notNull().default(0),lastAttemptAt:text('last_attempt_at'),deliveredAt:text('delivered_at'),receipt:text('receipt'),createdAt:text('created_at').notNull()});
