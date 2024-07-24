import sqlite3

# create db
db = sqlite3.connect('web-performance.db')
cursor = db.cursor()


def create_measurements_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id string,
            protocol string,
            server string,
            domain string,
            vantagePoint string,
            timestamp datetime,
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
            redirectCount integer,
            PRIMARY KEY (id)
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
                number_dns_queries INT
            );
            """)
    db.commit()


create_measurements_table()
create_lookups_table()
create_qlogs_table()
create_resolvers_table()
create_websites_table()


db.close()
