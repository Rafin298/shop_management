# core/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Product

class Command(BaseCommand):
    help = 'Seed initial users, categories, and products'

    def handle(self, *args, **options):
        User = get_user_model()

        # 1. Create Users
        users_data = [
            {'username': 'admin1',   'email': 'admin1@example.com',   'password': 'pass1234', 'role': 'admin'},
            {'username': 'seller1',  'email': 'seller1@example.com',  'password': 'pass1234', 'role': 'seller'},
            {'username': 'seller2',  'email': 'seller2@example.com',  'password': 'pass1234', 'role': 'seller'},
            {'username': 'customer1','email': 'cust1@example.com',    'password': 'pass1234', 'role': 'customer'},
            {'username': 'customer2','email': 'cust2@example.com',    'password': 'pass1234', 'role': 'customer'},
        ]
        created_users = []
        for u in users_data:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'role': u['role']}
            )
            if created:
                user.set_password(u['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {user.username} ({user.role})"))
            else:
                self.stdout.write(f"User {user.username} already exists")
            created_users.append(user)

        # 2. Create Categories
        categories = ['Electronics','Books','Clothing','Home','Sports']
        created_cats = []
        for name in categories:
            cat, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category {name}"))
            else:
                self.stdout.write(f"Category {name} already exists")
            created_cats.append(cat)

        # 3. Create Products (10 total, 2 per category)
        sellers = [u for u in created_users if u.role == 'seller']
        if not sellers:
            self.stderr.write("No seller users found—cannot seed products.")
            return

        prod_count = 0
        for idx, cat in enumerate(created_cats, start=1):
            for i in range(2):  # 2 products per category
                prod_count += 1
                name = f"{cat.name} Item {i+1}"
                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'seller': sellers[(idx + i) % len(sellers)],
                        'category': cat,
                        'description': f"Sample {name}",
                        'price': 10.0 * prod_count,
                        'stock': 50 + prod_count * 5
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created product {product.name}"))
                else:
                    self.stdout.write(f"Product {product.name} already exists")

        self.stdout.write(self.style.SUCCESS("Seeding complete."))