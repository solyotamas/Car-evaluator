from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, Text

Base = declarative_base()

class CarData(Base):
    __tablename__ = 'car_data'

    id = Column(Integer, primary_key = True)
    active = Column(Boolean)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    url = Column(Text)


class CarDetails(Base):
    __tablename__ = 'car_details'

    id = Column(Integer, primary_key=True)
    ár = Column(Integer)
    gyártó = Column(Text)
    modell = Column(Text)
    évjárat = Column(Integer)
    km = Column(Integer)
    üzemanyag = Column(Text)
    kw = Column(Integer)
    le = Column(Integer)
    állapot = Column(Text)
    csomagtartó = Column(Integer)
    kivitel = Column(Text)
    férőhely = Column(Integer)
    szín = Column(Text)
    hengerűrtartalom = Column(Float)
    hajtás = Column(Text)
    sebességváltó_típus = Column(Text)
    fokozatszám = Column(Integer)
    sebességváltó_altípus = Column(Text)