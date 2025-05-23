import os
import django
import random
from faker import Faker
from products.models import Product, Category, Color, Size

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cn2bn.settings')  # Change to your Django project name
django.setup()

# Initialize Faker
fake = Faker()

def populate_db():
    print("Starting database population...")

    # Create Categories if not exist
    category_names = ["Electronics", "Clothing", "Toys", "Books", "Furniture"]
    categories = [Category.objects.get_or_create(name=name)[0] for name in category_names]

    # Create Colors if not exist
    color_names = ["Red", "Blue", "Green", "Black", "White", "Yellow"]
    colors = [Color.objects.get_or_create(name=color)[0] for color in color_names]

    # Create Sizes if not exist
    size_names = ["S", "M", "L", "XL"]
    sizes = [Size.objects.get_or_create(name=size)[0] for size in size_names]

    products = []  # List to hold products for bulk create

    # Generate 150 fake products
    for _ in range(150):
        product = Product(
            name=fake.sentence(nb_words=3),
            product_images=['https://picsum.photos/200/300'],  # Empty JSON field for now
            category=random.choice(categories),
            quantity=random.randint(1, 100),
            price=round(random.uniform(5.0, 500.0), 2),
            available=random.choice([True, False])
        )
        products.append(product)

    # Bulk insert products for efficiency
    created_products = Product.objects.bulk_create(products)
    print(f"Created {len(created_products)} products.")

    # Assign random colors and sizes
    for product in created_products:
        product.colors.set(random.sample(colors, random.randint(1, len(colors))))
        product.sizes.set(random.sample(sizes, random.randint(1, len(sizes))))

    print("Database population completed successfully!")

# Run script
if __name__ == "__main__":
    populate_db()
