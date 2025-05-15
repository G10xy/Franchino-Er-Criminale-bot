import re
from typing import Optional

class InputValidator:

    @staticmethod
    def validate_name(city_name: str) -> Optional[str]:
        """Validate city name input"""
        if not city_name:
            raise ValueError("Il nome della città non può essere vuoto")
        
        city_name = city_name.strip()
        
        if len(city_name) < 2:
            raise ValueError("Il nome della città deve avere almeno 2 caratteri")
        if len(city_name) > 20:
            raise ValueError("Il nome della città è troppo lungo (max 50 caratteri)")
        
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', city_name):
            raise ValueError("Il nome della città contiene caratteri non validi")
        
        return city_name

    @staticmethod
    def validate_category_id(category_id: str) -> int:
        """Validate category ID"""
        try:
            cat_id = int(category_id)
            if cat_id < 1 or cat_id > 10:  
                raise ValueError("Categoria non valida")
            return cat_id
        except ValueError:
            raise ValueError("ID categoria non valido")    