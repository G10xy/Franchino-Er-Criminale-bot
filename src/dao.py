from bot_db_entities import Base, City, Neighborhood, Store
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager # Importato per la gestione del contesto
import os
import logging # Importato per il logging degli errori

class DAO:
    def __init__(self):
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=5,           
            max_overflow=30,        
            pool_recycle=3600,      
            pool_pre_ping=True      
        )
        Base.metadata.create_all(self.engine) 
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    @contextmanager 
    def get_session(self):
        session = self.Session() 
        try:
            yield session 
            session.commit() 
        except Exception as e:
            session.rollback() 
            logging.error(f"Errore database: {e}") 
            raise 
        finally:
            session.close()

    def find_city(self, city_name: str):
        with self.get_session() as session:
            return session.query(City).filter(
                func.lower(City.name) == func.lower(city_name.strip())
            ).first()

    def find_neighborhood(self, neighborhood_name: str, city_id: int):
        with self.get_session() as session:
            return session.query(Neighborhood).filter(
                func.lower(Neighborhood.name) == func.lower(neighborhood_name.strip()),
                Neighborhood.city_id == city_id
            ).first()

    def get_stores(self, neighborhood_id: int, category_id: int):
        with self.get_session() as session:
            return session.query(Store).filter_by(
                neighborhood_id=neighborhood_id,
                criminal_category_id=category_id
            ).order_by(Store.vote.desc()).all()

    def close_engine(self):
        self.engine.dispose() 