import sqlite3

# create db
db = sqlite3.connect('web-performance3.db')
cursor = db.cursor()


def create_measurements_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            protocol string,
            server string,
            domain string,
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
            nextHopProtocol string,
            cacheWarming integer,
            error string,
            redirectStart integer,
            redirectEnd integer,
            redirectCount integer
        );
        """)
    db.commit()


def create_lookups_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS lookups (
                measurement_id string,
                domain string,
                elapsed numeric,
                status string,
                answer string,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            );
            """)
    db.commit()


def create_qlogs_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS qlogs (
                measurement_id string,
                qlog string,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            );
            """)
    db.commit()


def create_resolvers_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS resolvers (
                _id INT AUTO_INCREMENT PRIMARY KEY,
                ip string NOT NULL,
                dns string
            );
            """)
    db.commit()

def create_websites_table():
    # TODO adding complexity columns
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                _id INT AUTO_INCREMENT PRIMARY KEY,
                dns string NOT NULL,
                number_dns_queries INT,
                number_objects_loaded INT,
                number_queried_servers INT,
                number_non_origin_servers INT,
                number_mime_types INT,
                bytes_downladed INT, 
                alexa_category string
            );
            """)
    db.commit()


def create_mime_types_table():
    # TODO adding complexity columns
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS mime_types (
                website_id INT,
                mime_type string,
                occurences INT,
                bytes_body_download INT,
                bytes_header_download INT,
                FOREIGN KEY(website_id) REFERENCES websites(_id),
                CONSTRAINT PK_Website_MimeType PRIMARY KEY (mime_type,website_id)
            );
            """)
    db.commit()

create_measurements_table()
create_lookups_table()
create_qlogs_table()
create_resolvers_table()
create_websites_table()
create_mime_types_table()


db.close()
