import json
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from profiles.models import Countries

def import_countries():
    json_file_path = '../frontend/src/data/countries.json'
    
    Countries.objects.all().delete()
    print('Cleared existing countries data')
 
    with open(json_file_path, 'r', encoding='utf-8') as file:
        countries_data = json.load(file)
        countries_to_create = [
            Countries(
                num_code=int(country['numeric_code']),
                alpha_2_code=country['iso2'],
                alpha_3_code=country['iso3'],
                en_short_name=country['name'],
                nationality=country['nationality'].strip()
            )
            for country in countries_data
        ]
        
        # Sort by name before creating
        countries_to_create.sort(key=lambda x: x.en_short_name)
        
        Countries.objects.bulk_create(countries_to_create)
        
        print(f'Successfully imported {len(countries_to_create)} countries in alphabetical order')

if __name__ == '__main__':
    import_countries() 