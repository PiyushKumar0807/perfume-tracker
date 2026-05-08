#!/usr/bin/env python3
"""
PerfumeAI Database Seeding Script

This script populates the database with sample perfume data for testing and demonstration.
Run this script after setting up the database to populate it with perfumes.
"""

import sys
import os
from datetime import datetime
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Perfume

def seed_perfumes():
    """Seed the database with sample perfume data."""

    perfumes_data = [
        {
            'name': 'Chanel No. 5',
            'brand': 'Chanel',
            'description': 'The iconic floral aldehyde fragrance that revolutionized perfumery. A timeless classic with powdery floral notes.',
            'fragrance_family': 'Floral',
            'gender': 'Female',  # FIX: use DB-valid value ('Female' not 'Women')
            'price_range': 'Luxury',  # FIX: use DB-valid price_range ('Luxury' not '$100-$200')
            'top_notes': json.dumps(['Aldehydes', 'Bergamot', 'Lemon', 'Neroli', 'Ylang-Ylang']),
            'middle_notes': json.dumps(['Iris', 'Jasmine', 'Rose', 'Patchouli']),
            'base_notes': json.dumps(['Vanilla', 'Sandalwood', 'Amber', 'Musk', 'Vetiver']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Winter',
            'occasion': 'Evening',
            'intensity': 'Strong',
        },
        {
            'name': 'Dior Sauvage',
            'brand': 'Dior',
            'description': 'A fresh, spicy, and masculine fragrance with a distinctive peppery kick. Perfect for the modern man.',
            'fragrance_family': 'Aromatic',
            'gender': 'Male',  # FIX: 'Male' not 'Men'
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Pepper', 'Bergamot', 'Geranium', 'Lavender']),
            'middle_notes': json.dumps(['Lavender', 'Geranium', 'Vetiver', 'Sichuan Pepper']),
            'base_notes': json.dumps(['Ambroxan', 'Cedar', 'Labdanum', 'Patchouli']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Spring',
            'occasion': 'Casual',
            'intensity': 'Strong',
        },
        {
            'name': 'Gucci Bloom',
            'brand': 'Gucci',
            'description': 'A romantic and feminine floral fragrance inspired by the beauty of Tuscany. Fresh, natural, and elegant.',
            'fragrance_family': 'Floral',
            'gender': 'Female',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Jasmine', 'Bergamot', 'Mandarin']),
            'middle_notes': json.dumps(['Jasmine', 'Tuberose', 'Range of Roses']),
            'base_notes': json.dumps(['Patchouli', 'Sandalwood', 'Amber']),
            'longevity': 'Good',
            'sillage': 'Moderate',
            'season': 'Spring',
            'occasion': 'Casual',
            'intensity': 'Moderate',
        },
        {
            'name': 'Tom Ford Oud Wood',
            'brand': 'Tom Ford',
            'description': 'A luxurious oriental woody fragrance with rich oud and rose notes. Sophisticated and intense.',
            'fragrance_family': 'Oriental',
            'gender': 'Unisex',
            'price_range': 'Ultra-luxury',  # FIX: '$200+' -> 'Ultra-luxury'
            'top_notes': json.dumps(['Rose', 'Ginger', 'Cardamom']),
            'middle_notes': json.dumps(['Oud', 'Sandalwood', 'Vetiver']),
            'base_notes': json.dumps(['Oud', 'Dark Chocolate', 'Tobacco']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Fall',
            'occasion': 'Evening',
            'intensity': 'Strong',
        },
        {
            'name': 'Acqua di Parma Colonia',
            'brand': 'Acqua di Parma',
            'description': 'A fresh and citrusy cologne with Sicilian citrus notes. Light, refreshing, and versatile.',
            'fragrance_family': 'Citrus',
            'gender': 'Unisex',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Bergamot', 'Lemon', 'Orange', 'Grapefruit']),
            'middle_notes': json.dumps(['Lavender', 'Rosemary', 'Floral Notes']),
            'base_notes': json.dumps(['Patchouli', 'Oakmoss', 'Amber']),
            'longevity': 'Good',
            'sillage': 'Moderate',
            'season': 'Summer',
            'occasion': 'Casual',
            'intensity': 'Light',
        },
        {
            'name': 'Yves Saint Laurent Black Opium',
            'brand': 'YSL',
            'description': 'A seductive oriental vanilla fragrance with coffee and white flowers. Addictive and glamorous.',
            'fragrance_family': 'Oriental',
            'gender': 'Female',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Coffee', 'Pink Pepper']),
            'middle_notes': json.dumps(['Jasmine', 'Vanilla']),
            'base_notes': json.dumps(['Vanilla', 'Patchouli', 'White Chocolate']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Fall',
            'occasion': 'Evening',
            'intensity': 'Strong',
        },
        {
            'name': 'Creed Aventus',
            'brand': 'Creed',
            'description': 'A sophisticated fruity chypre fragrance with pineapple and birch. The ultimate masculine scent.',
            'fragrance_family': 'Aromatic',
            'gender': 'Male',
            'price_range': 'Ultra-luxury',
            'top_notes': json.dumps(['Pineapple', 'Bergamot', 'Black Currant', 'Apple']),
            'middle_notes': json.dumps(['Birch', 'Jasmine', 'Rose']),
            'base_notes': json.dumps(['Musk', 'Oakmoss', 'Ambergris', 'Vanilla']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Spring',
            'occasion': 'Special',
            'intensity': 'Strong',
        },
        {
            'name': 'Jo Malone London English Pear & Freesia',
            'brand': 'Jo Malone',
            'description': 'A fresh and fruity floral fragrance with pear and freesia. Light and elegant for everyday wear.',
            'fragrance_family': 'Floral',
            'gender': 'Unisex',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Pear', 'Freesia', 'Mint']),
            'middle_notes': json.dumps(['Freesia', 'Pear', 'Rose']),
            'base_notes': json.dumps(['Patchouli', 'White Musk']),
            'longevity': 'Good',
            'sillage': 'Light',
            'season': 'Spring',
            'occasion': 'Casual',
            'intensity': 'Light',
        },
        {
            'name': "Hermès Terre d'Hermès",
            'brand': 'Hermès',
            'description': 'An earthy and woody fragrance with grapefruit and cedar. Modern and sophisticated.',
            'fragrance_family': 'Woody',
            'gender': 'Male',
            'price_range': 'Luxury',
            'top_notes': json.dumps(['Grapefruit', 'Orange']),
            'middle_notes': json.dumps(['Pepper', 'Geranium', 'Cedar']),
            'base_notes': json.dumps(['Benzoin', 'Patchouli', 'Vetiver']),
            'longevity': 'Excellent',
            'sillage': 'Moderate',
            'season': 'Fall',
            'occasion': 'Office',
            'intensity': 'Moderate',
        },
        {
            'name': 'Chloé Nomade',
            'brand': 'Chloé',
            'description': 'A free-spirited floral fragrance with peony and rose. Romantic and adventurous.',
            'fragrance_family': 'Floral',
            'gender': 'Female',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Peony', 'Lychee', 'Freesia']),
            'middle_notes': json.dumps(['Rose', 'Jasmine', 'Patchouli']),
            'base_notes': json.dumps(['Amber', 'Vanilla', 'Wood']),
            'longevity': 'Good',
            'sillage': 'Moderate',
            'season': 'Spring',
            'occasion': 'Casual',
            'intensity': 'Moderate',
        },
        {
            'name': 'Versace Eros',
            'brand': 'Versace',
            'description': 'A sensual and masculine fragrance with mint and tonka bean. Bold and confident.',
            'fragrance_family': 'Aromatic',
            'gender': 'Male',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Mint', 'Green Apple']),
            'middle_notes': json.dumps(['Tonka Bean', 'Geranium', 'Ambroxan']),
            'base_notes': json.dumps(['Vetiver', 'Cedar', 'Oakmoss']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Summer',
            'occasion': 'Casual',
            'intensity': 'Strong',
        },
        {
            'name': 'Dolce & Gabbana Light Blue',
            'brand': 'Dolce & Gabbana',
            'description': 'A fresh aquatic fragrance with apple and cedar. Perfect for warm summer days.',
            'fragrance_family': 'Fresh',
            'gender': 'Unisex',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Apple', 'Cedar', 'Sicilian Lemon']),
            'middle_notes': json.dumps(['Rose', 'Bamboo', 'Jasmine']),
            'base_notes': json.dumps(['Amber', 'Musk', 'Tobacco']),
            'longevity': 'Good',
            'sillage': 'Moderate',
            'season': 'Summer',
            'occasion': 'Casual',
            'intensity': 'Light',
        },
        {
            'name': 'Paco Rabanne 1 Million',
            'brand': 'Paco Rabanne',
            'description': 'A luxurious spicy gourmand fragrance with cinnamon and rose. Rich and opulent.',
            'fragrance_family': 'Oriental',
            'gender': 'Male',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Blood Mandarin', 'Grapefruit', 'Mint']),
            'middle_notes': json.dumps(['Cinnamon', 'Rose', 'Spicy Notes']),
            'base_notes': json.dumps(['Amber', 'Patchouli', 'Leather']),
            'longevity': 'Excellent',
            'sillage': 'Strong',
            'season': 'Fall',
            'occasion': 'Evening',
            'intensity': 'Strong',
        },
        {
            'name': 'Burberry Her',
            'brand': 'Burberry',
            'description': 'A modern floral fragrance with pear and rose. Feminine and contemporary.',
            'fragrance_family': 'Floral',
            'gender': 'Female',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Pear', 'Bergamot']),
            'middle_notes': json.dumps(['Rose', 'Jasmine', 'Patchouli']),
            'base_notes': json.dumps(['Vanilla', 'Amber', 'Wood']),
            'longevity': 'Good',
            'sillage': 'Moderate',
            'season': 'Spring',
            'occasion': 'Casual',
            'intensity': 'Moderate',
        },
        {
            'name': 'Hugo Boss Bottled',
            'brand': 'Hugo Boss',
            'description': 'A classic masculine fragrance with apple and cinnamon. Professional and reliable.',
            'fragrance_family': 'Aromatic',
            'gender': 'Male',
            'price_range': 'Mid-range',
            'top_notes': json.dumps(['Apple', 'Bergamot', 'Pineapple']),
            'middle_notes': json.dumps(['Cinnamon', 'Geranium', 'Jasmine']),
            'base_notes': json.dumps(['Vanilla', 'Amber', 'Tobacco']),
            'longevity': 'Excellent',
            'sillage': 'Moderate',
            'season': 'Fall',
            'occasion': 'Office',  # FIX: 'Work' is not in OCCASIONS; use 'Office'
            'intensity': 'Moderate',
        }
    ]

    print("Seeding perfumes database...")

    added_count = 0
    for perfume_data in perfumes_data:
        # Check if perfume already exists
        existing_perfume = Perfume.query.filter_by(
            name=perfume_data['name'],
            brand=perfume_data['brand']
        ).first()

        if existing_perfume:
            print(f"Perfume '{perfume_data['name']}' already exists, skipping...")
            continue

        # FIX: pass all available fields to Perfume(); original code only set 5 fields
        perfume = Perfume(
            name=perfume_data['name'],
            brand=perfume_data['brand'],
            description=perfume_data['description'],
            fragrance_family=perfume_data['fragrance_family'],
            gender_target=perfume_data['gender'],
            price_range=perfume_data.get('price_range', 'Mid-range'),
            top_notes=perfume_data.get('top_notes', ''),
            middle_notes=perfume_data.get('middle_notes', ''),
            base_notes=perfume_data.get('base_notes', ''),
            longevity=perfume_data.get('longevity', 'Good'),
            sillage=perfume_data.get('sillage', 'Moderate'),
            season=perfume_data.get('season', ''),
            occasion=perfume_data.get('occasion', ''),
            intensity=perfume_data.get('intensity', 'Moderate'),
        )
        db.session.add(perfume)
        added_count += 1
        print(f"Added perfume: {perfume.name}")

    # Commit all changes
    db.session.commit()
    print(f"\nSeeding complete! Added {added_count} new perfumes to the database.")

def seed_from_csv(csv_path=None):
    """Bulk-import perfumes from fra_cleaned_csv.csv into the Perfume table.

    The CSV columns used:
        Perfume, Brand, Gender, Rating Value, Rating Count,
        Top, Middle, Base, mainaccord1-5
    """
    if csv_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # FIX: typo 'fra_cleaned.csv.csv' -> 'fra_cleaned.csv'
        preferred = os.path.join(base_dir, 'fra_cleaned.csv')
        legacy = os.path.join(base_dir, 'fra_cleaned_csv.csv')
        csv_path = preferred if os.path.exists(preferred) else legacy

    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}, skipping CSV import.")
        return

    import pandas as pd  # already in requirements

    print(f"Reading CSV from {csv_path} ...")
    df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')

    # Normalise column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Map CSV gender -> DB gender_target
    gender_map = {
        'women': 'Female', 'female': 'Female',
        'men': 'Male', 'male': 'Male',
        'unisex': 'Unisex',
    }

    # Build a set of (name, brand) already in DB so we skip duplicates efficiently
    existing = {
        (p.name.lower(), p.brand.lower())
        for p in Perfume.query.with_entities(Perfume.name, Perfume.brand).all()
    }

    added = 0
    skipped = 0
    batch_size = 500

    for i, row in df.iterrows():
        name = str(row.get('Perfume', '')).strip()
        brand = str(row.get('Brand', '')).strip()

        if not name or not brand or name == 'nan' or brand == 'nan':
            skipped += 1
            continue

        if (name.lower(), brand.lower()) in existing:
            skipped += 1
            continue

        # Derive fragrance family from mainaccord columns (first non-null wins)
        family = 'Other'
        for col in ['mainaccord1', 'mainaccord2', 'mainaccord3', 'mainaccord4', 'mainaccord5']:
            val = str(row.get(col, '')).strip()
            if val and val != 'nan':
                family = val.title()
                break

        gender_raw = str(row.get('Gender', 'unisex')).strip().lower()
        gender_target = gender_map.get(gender_raw, 'Unisex')

        # Accords as a comma-separated string (reuse top_notes field for accord context)
        accords = ', '.join(
            str(row.get(c, '')).strip()
            for c in ['mainaccord1', 'mainaccord2', 'mainaccord3', 'mainaccord4', 'mainaccord5']
            if str(row.get(c, '')).strip() and str(row.get(c, '')).strip() != 'nan'
        )

        perfume = Perfume(
            name=name,
            brand=brand,
            fragrance_family=family,
            gender_target=gender_target,
            top_notes=str(row.get('Top', '')).strip() if str(row.get('Top', '')) != 'nan' else '',
            middle_notes=str(row.get('Middle', '')).strip() if str(row.get('Middle', '')) != 'nan' else '',
            base_notes=str(row.get('Base', '')).strip() if str(row.get('Base', '')) != 'nan' else '',
            description=accords,
        )

        # Seed community rating if available
        try:
            avg_r = float(row.get('Rating Value', 0) or 0)
            total_r = int(float(row.get('Rating Count', 0) or 0))
            if avg_r > 0:
                perfume.avg_rating = round(avg_r / 10.0, 2)  # Fragrantica uses 0-100 scale
                perfume.total_ratings = total_r
        except (ValueError, TypeError):
            pass

        db.session.add(perfume)
        existing.add((name.lower(), brand.lower()))
        added += 1

        if added % batch_size == 0:
            db.session.commit()
            print(f"  ... committed {added} perfumes so far")

    db.session.commit()
    print(f"CSV import complete: {added} added, {skipped} skipped.")


def main():
    """Main function to run the seeding script."""
    try:
        # Use the Flask app context
        with app.app_context():
            # Create all tables if they don't exist
            db.create_all()

            # Seed with hardcoded sample perfumes
            seed_perfumes()

            # Bulk-import from CSV (24k perfumes)
            seed_from_csv()

        print("\nDatabase seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()