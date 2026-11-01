CREATE INDEX `origination_kind_state_idx` ON `origination_records` (`kind`,`state`);--> statement-breakpoint
CREATE INDEX `origination_disposition_idx` ON `origination_records` (`kind`,`disposition`);--> statement-breakpoint
CREATE INDEX `origination_county_idx` ON `origination_records` (`county`);