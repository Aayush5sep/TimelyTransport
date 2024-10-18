import datetime
import pytz
import bcrypt
from sqlalchemy import text


def get_current_time():
    return datetime.datetime.now(pytz.timezone("Asia/Kolkata"))


def add_country_code(phone_number: str, country_code="+91"):
    if phone_number.startswith(country_code):
        return phone_number
    else:
        return country_code + phone_number
    

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()


def convert_ll_to_point(latitude: float, longitude: float):
    point = f'POINT({longitude} {latitude})'
    return text(f"ST_GeomFromText('{point}', 4326)")


def convert_point_to_ll(point):
    longitude, latitude = map(float, point.strip('POINT()').split())
    return {"latitude": latitude, "longitude": longitude}