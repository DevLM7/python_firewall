import geoip2.database

class GeoIPManager:
    def __init__(self, db_path):
        self.reader = geoip2.database.Reader(db_path)

    def get_country_from_ip(self, ip_address):
        try:
            response = self.reader.country(ip_address)
            return response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            return None
        except Exception:
            return None
