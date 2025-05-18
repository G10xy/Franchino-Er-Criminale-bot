import re
from typing import Optional

class InputValidator:

    @staticmethod
    def validate_name(city_name: str) -> Optional[str]:
        """Validate string input"""
        if not city_name:
            raise ValueError("Il valore inserito non può essere vuoto")
        
        city_name = city_name.strip()
        
        if len(city_name) < 2:
            raise ValueError("Il valore inserito deve avere almeno 2 caratteri")
        if len(city_name) > 20:
            raise ValueError("Il valore inserito è troppo lungo (max 50 caratteri)")
        
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', city_name):
            raise ValueError("Il nome contiene caratteri non validi")
        
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

    @staticmethod
    def contains_google_maps_url(text: str) -> bool:
        """ Check if the text contains a Google Maps URL """
        google_maps_pattern = r'https://(maps\.app\.goo\.gl/[a-zA-Z0-9]+|g\.co/kgs/[a-zA-Z0-9]+)'
        return re.search(google_maps_pattern, text)        