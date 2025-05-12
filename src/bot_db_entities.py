from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    neighborhoods = relationship('Neighborhood', backref='city', lazy=True)

class Neighborhood(Base):
    __tablename__ = 'neighborhood'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    city_id = Column(Integer, ForeignKey('city.id'), nullable=False)
    stores = relationship('Store', backref='neighborhood', lazy=True)

class CriminalCategory(Base):
    __tablename__ = 'criminal_category'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    stores = relationship('Store', backref='criminal_category', lazy=True)

class Store(Base):
    __tablename__ = 'store'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    vote = Column(Float, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    full_vote = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    criminal_category_id = Column(Integer, ForeignKey('criminal_category.id'), nullable=False)
    neighborhood_id = Column(Integer, ForeignKey('neighborhood.id'), nullable=False)


