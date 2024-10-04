import psycopg

# create db
#db = psycopg.connect(dbname='postgres', user='postgres', autocommit=True)
db = psycopg.connect(dbname='postgres', autocommit=True)
cursor = db.cursor()
cursor.execute("DROP DATABASE web_performance")
cursor.execute("CREATE DATABASE web_performance")
db.close()
db = psycopg.connect(dbname='web_performance', autocommit=True)
cursor = db.cursor()


def create_measurements_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id SERIAL PRIMARY KEY,
            protocol VARCHAR,
            server VARCHAR,
            domain VARCHAR,
            timestamp integer,
            connectEnd integer,
            connectStart integer,
            domComplete integer,
            domContentLoadedEventEnd integer,
            domContentLoadedEventStart integer,
            domInteractive integer,
            domainLookupEnd integer,
            domainLookupStart integer,
            duration integer,
            encodedBodySize integer,
            decodedBodySize integer,
            transferSize integer,
            fetchStart integer,
            loadEventEnd integer,
            loadEventStart integer,
            requestStart integer,
            responseEnd integer,
            responseStart integer,
            secureConnectionStart integer,
            startTime integer,
            firstPaint integer,
            firstContentfulPaint integer,
            nextHopProtocol VARCHAR,
            cacheWarming integer,
            error VARCHAR,
            redirectStart integer,
            redirectEnd integer,
            redirectCount integer
        );
        """)


def create_lookups_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS lookups (
                measurement_id SERIAL,
                domain VARCHAR,
                elapsed numeric,
                status VARCHAR,
                answer VARCHAR,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            );
            """)
    

def create_resolvers_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS resolvers (
                _id SERIAL PRIMARY KEY,
                host VARCHAR,
                protocol VARCHAR,
                port integer,
                UNIQUE (host, port),
                UNIQUE (host, protocol)
            );
            """)
    
def create_resolver_measurement_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS resolver_measurement (
                _id SERIAL PRIMARY KEY,
                resolver_id SERIAL,
                protocol VARCHAR,
                rtt integer,  
                total_time integer, 
                round_trips integer,
                warm_up bool,
                raw_data VARCHAR,
                FOREIGN KEY (resolver_id) REFERENCES resolvers(_id)
            );
            """)

def create_websites_table():
    # TODO adding complexity columns
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                _id SERIAL PRIMARY KEY,
                has_website BOOL DEFAULT TRUE,
                has_error BOOL DEFAULT FALSE, 
                dns VARCHAR NOT NULL,
                number_dns_queries INT,
                number_objects_loaded INT,
                number_queried_servers INT,
                number_non_origin_servers INT,
                number_mime_types INT,
                bytes_downladed INT 
            );
            """)


def create_mime_types_table():
    # TODO adding complexity columns
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS mime_types (
                website_id INT,
                mime_type VARCHAR,
                occurences INT,
                bytes_body_download INT,
                bytes_header_download INT,
                FOREIGN KEY(website_id) REFERENCES websites(_id),
                CONSTRAINT PK_Website_MimeType PRIMARY KEY (mime_type,website_id)
            );
            """)


create_measurements_table()
create_lookups_table()
create_resolvers_table()
create_resolver_measurement_table()
create_websites_table()
create_mime_types_table()


db.close()
