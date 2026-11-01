CREATE TABLE `atlas_entities` (
	`id` text PRIMARY KEY NOT NULL,
	`kind` text NOT NULL,
	`data` text NOT NULL,
	`version` integer DEFAULT 1 NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `atlas_entities_kind_idx` ON `atlas_entities` (`kind`);--> statement-breakpoint
CREATE TABLE `atlas_events` (
	`id` text PRIMARY KEY NOT NULL,
	`parcel_id` text,
	`event_type` text NOT NULL,
	`previous_data` text,
	`data` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `atlas_events_parcel_idx` ON `atlas_events` (`parcel_id`,`created_at`);--> statement-breakpoint
CREATE TABLE `atlas_jobs` (
	`id` text PRIMARY KEY NOT NULL,
	`kind` text NOT NULL,
	`state` text NOT NULL,
	`data` text NOT NULL,
	`lease_token` text,
	`lease_until` text,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `atlas_outbox` (
	`id` text PRIMARY KEY NOT NULL,
	`event_key` text NOT NULL,
	`data` text NOT NULL,
	`status` text DEFAULT 'PENDING' NOT NULL,
	`attempts` integer DEFAULT 0 NOT NULL,
	`last_attempt_at` text,
	`delivered_at` text,
	`receipt` text,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `atlas_outbox_event_key_unique` ON `atlas_outbox` (`event_key`);--> statement-breakpoint
CREATE TABLE `atlas_parcels` (
	`id` text PRIMARY KEY NOT NULL,
	`county_fips` text NOT NULL,
	`apn` text NOT NULL,
	`state` text NOT NULL,
	`county` text NOT NULL,
	`source_id` text NOT NULL,
	`minx` real NOT NULL,
	`miny` real NOT NULL,
	`maxx` real NOT NULL,
	`maxy` real NOT NULL,
	`geometry` text NOT NULL,
	`data` text NOT NULL,
	`version` integer DEFAULT 1 NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `atlas_parcels_bbox_idx` ON `atlas_parcels` (`minx`,`maxx`,`miny`,`maxy`);--> statement-breakpoint
CREATE INDEX `atlas_parcels_apn_idx` ON `atlas_parcels` (`county_fips`,`apn`);--> statement-breakpoint
CREATE TABLE `atlas_results` (
	`id` text PRIMARY KEY NOT NULL,
	`parcel_id` text NOT NULL,
	`profile_id` text NOT NULL,
	`color` text NOT NULL,
	`data` text NOT NULL,
	`input_hash` text NOT NULL,
	`computed_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `atlas_results_profile_idx` ON `atlas_results` (`profile_id`,`color`);--> statement-breakpoint
CREATE INDEX `atlas_results_parcel_idx` ON `atlas_results` (`parcel_id`);--> statement-breakpoint
CREATE TABLE `atlas_runs` (
	`id` text PRIMARY KEY NOT NULL,
	`hash` text NOT NULL,
	`data` text NOT NULL,
	`created_at` text NOT NULL
);
