CREATE TABLE `origination_events` (
	`id` text PRIMARY KEY NOT NULL,
	`run_id` text NOT NULL,
	`record_id` text NOT NULL,
	`previous_data` text,
	`data` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `origination_records` (
	`id` text PRIMARY KEY NOT NULL,
	`kind` text NOT NULL,
	`state` text,
	`county` text,
	`disposition` text,
	`stage` text,
	`data` text NOT NULL,
	`version` integer DEFAULT 1 NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `origination_runs` (
	`id` text PRIMARY KEY NOT NULL,
	`hash` text NOT NULL,
	`data` text NOT NULL,
	`created_at` text NOT NULL
);
