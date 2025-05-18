from sqlalchemy import create_engine, MetaData, and_
from bot_db_entities import Base, City, Neighborhood, CriminalCategory, Store
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
import pandas as pd
import logging
import os


class DatabaseUpdater:
    def __init__(self):
        self.logger = logging.getLogger('DatabaseUpdater')
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.engine = create_engine(DATABASE_URL)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
        self.file_path = os.getenv('FILE_PATH')

    def update_from_excel(self):
        """Update the database from the Excel file"""
        self.logger.info(f"Updating database from Excel file: {self.file_path}")
        if not os.path.exists(self.file_path):
            self.logger.error(f"Excel file not found: {self.file_path}")
            return False
            
        try:
            xls = pd.ExcelFile(self.file_path)
            
            # Read all data frames
            df_categories = pd.read_excel(xls, 'category')
            df_cities = pd.read_excel(xls, 'city')
            df_neighborhoods = pd.read_excel(xls, 'neighborhood')
            df_stores = pd.read_excel(xls, 'store')
            
            # Bulk insert for CriminalCategory
            categories_to_insert = []
            for index, row in df_categories.iterrows():
                cat_id = row['id']
                cat_title = row['title']
                category_exists = self.session.query(exists().where(and_(CriminalCategory.id == cat_id, CriminalCategory.title == cat_title))).scalar()
                if not category_exists:
                    self.logger.info(f"Adding new category: {cat_title}")
                    categories_to_insert.append({
                        'id': row['id'],
                        'title': row['title'],
                        'created_at': datetime.now()
                    })
            if categories_to_insert:
                self.session.bulk_insert_mappings(CriminalCategory, categories_to_insert)

            # Bulk insert for City
            cities_to_insert = []
            for index, row in df_cities.iterrows():
                city_id = row['id']
                city_name = row['name']
                city_exists = self.session.query(exists().where(and_(City.id == city_id, City.name == city_name))).scalar()
                if not city_exists:
                    self.logger.info(f"Adding new city: {city_name}")
                    cities_to_insert.append({
                        'id': row['id'],
                        'name': row['name'],
                        'created_at': datetime.now()
                    })
            if cities_to_insert:
                self.session.bulk_insert_mappings(City, cities_to_insert)

            # Bulk insert for Neighborhood
            neighborhoods_to_insert = []
            for index, row in df_neighborhoods.iterrows():
                n_id = row['id']
                n_name = row['name']
                n_city_id = row['city_id']
                n_exists = self.session.query(exists().where(and_(Neighborhood.id == n_id, Neighborhood.name == n_name, Neighborhood.city_id == n_city_id))).scalar()
                if not n_exists:
                    self.logger.info(f"Adding new neighborhood: {n_name}")
                    neighborhoods_to_insert.append({
                        'id': row['id'],
                        'name': row['name'],
                        'created_at': datetime.now(),
                        'city_id': row['city_id']
                    })
            if neighborhoods_to_insert:
                self.session.bulk_insert_mappings(Neighborhood, neighborhoods_to_insert)

            # Bulk update/insert for Store
            stores_to_upsert = []
            updated_count = 0
            for index, row in df_stores.iterrows():
                store = self.session.query(Store).filter_by(id=row['id'], name=row['name']).first()
                if store:
                    store.address = row['address']
                    store.vote = row['vote']
                    store.latitude = row['latitude']
                    store.longitude = row['longitude']
                    store.full_vote = row['full_vote']
                    store.comment = row['comment']
                    store.updated_at = datetime.now()
                    store.criminal_category_id = row['criminal_category_id']
                    store.neighborhood_id = row['neighborhood_id']
                    updated_count += 1
                else:
                    stores_to_upsert.append({
                        'id': row['id'],
                        'name': row['name'],
                        'address': row['address'],
                        'vote': row['vote'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'full_vote': row['full_vote'],
                        'comment': row['comment'],
                        'created_at': datetime.now(),
                        'updated_at': datetime.now(),
                        'criminal_category_id': row['criminal_category_id'],
                        'neighborhood_id': row['neighborhood_id']
                    })
            
            if updated_count > 0:
                self.logger.info(f"Updated {updated_count} existing stores")
                
            if stores_to_upsert:
                self.logger.info(f"Adding {len(stores_to_upsert)} new stores")
                self.session.bulk_insert_mappings(Store, stores_to_upsert)

            self.session.commit()
            self.logger.info("Database update completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating database: {e}")
            if 'session' in locals():
                self.session.rollback()
            return False
        finally:
            if 'session' in locals():
                self.session.close()

    def pre_populateDB(self):
        """Initial database population (for backward compatibility)"""
        return self.update_from_excel()