from bot_db_entities import Base, City, Neighborhood, Store
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
import os

class DAO:
    def __init__(self):
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def find_city(self, city_name):
        return self.session.query(City).filter(func.lower(City.name) == func.lower(city_name.strip())).first()

    def find_neighborhood(self, neighborhood_name, city_id):
        return self.session.query(Neighborhood).filter(func.lower(Neighborhood.name)==func.lower(neighborhood_name.strip()), Neighborhood.city_id==city_id).first()

    def get_stores(self, neighborhood_id, category_id):
        return self.session.query(Store).filter_by(neighborhood_id=neighborhood_id, criminal_category_id=category_id).order_by(Store.vote.desc()).all()  
