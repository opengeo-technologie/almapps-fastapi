import geoip2.database

reader = geoip2.database.Reader("GeoLite2-Country.mmdb")


def get_country(ip: str) -> str:
    try:
        response = reader.country(ip)
        return response.country.name or "Unknown"
    except Exception:
        return "Unknown"
