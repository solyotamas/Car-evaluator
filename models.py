from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, Text, ForeignKey

Base = declarative_base()

class CarData(Base):
    __tablename__ = 'car_data'

    id = Column(Integer, ForeignKey("car_details.id"), primary_key=True)
    active = Column(Boolean)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    url = Column(Text)


class CarDetails(Base):
    __tablename__ = 'car_details'

    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    manufacturer = Column(Text)
    model = Column(Text)
    year = Column(Integer)
    kilometers = Column(Integer)
    fuel_type = Column(Text)
    kw = Column(Integer)
    le = Column(Integer)
    condition = Column(Text)
    trunk_capacity = Column(Integer)
    body_type = Column(Text)
    seats = Column(Integer)
    color = Column(Text)
    engine_capacity = Column(Float)
    drive_type = Column(Text)
    transmission_type = Column(Text)
    number_of_gears = Column(Integer)
    transmission_subtype = Column(Text)