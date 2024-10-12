
-- alter collumns table 'resolver_measurement';
  ALTER TABLE `resolver_measurement`
    ADD COLUMN rtt integer,
    ADD COLUMN total_time integer,
    ADD COLUMN round_trips integer,
    ADD COLUMN warm_up bool,
    ADD COLUMN rtt0 bool,
    ADD COLUMN session_resumption bool,
    ADD COLUMN raw_data VARCHAR;
-- --------------------------------------------------------;

-- alter collumns table 'resolvers';
  ALTER TABLE `resolvers`
    ADD COLUMN host VARCHAR,
    ADD COLUMN rtt0 bool DEFAULT FALSE,
    ADD COLUMN session_resumption bool DEFAULT FALSE,
    ADD UNIQUE (host, port),
    ADD UNIQUE (host, protocol);

-- --------------------------------------------------------;
COMMIT;
