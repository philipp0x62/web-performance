
-- alter collumns table 'resolver_measurement';
  CREATE TABLE "resolver_measurement" (
    rtt integer,
    total_time integer,
    round_trips integer,
    warm_up bool,
    rtt0 bool,
    session_resumption bool,
    raw_data VARCHAR
  );
-- --------------------------------------------------------;

-- alter collumns table 'resolvers';
  ALTER TABLE "resolvers"
    ADD COLUMN host VARCHAR,
    ADD COLUMN protocol VARCHAR,
    ADD COLUMN port integer,
    ADD COLUMN rtt0 bool DEFAULT FALSE,
    ADD COLUMN session_resumption bool DEFAULT FALSE,
    DROP COLUMN ip,
    DROP COLUMN dns,
    ADD UNIQUE (host, port),
    ADD UNIQUE (host, protocol);

-- --------------------------------------------------------;


ALTER TABLE "resolvers"
  ADD COLUMN serv_fail_rtt0 bool DEFAULT FALSE,
  ADD COLUMN unreliable bool DEFAULT FALSE;


ALTER TABLE "websites"
  ADD COLUMN har_file bool DEFAULT FALSE;


COMMIT;
