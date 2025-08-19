import geoip2.database

class GeoIPManager:
    def __init__(self, db_path):
        try:
            self.reader = geoip2.database.Reader(db_path)
        except FileNotFoundError:
            print(f"Error: GeoIP database not found at {db_path}")
            raise
    
    def get_country_from_ip(self, ip_address):
        try:
            response = self.reader.country(ip_address)
            return response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            return None
        except Exception as e:
            print(f"GeoIP lookup error for {ip_address}: {e}")
            return None
