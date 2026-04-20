from django.db import migrations


def create_categories(apps, schema_editor):
    Category = apps.get_model('accounts', 'Category')
    defaults = [
        {
            'name': 'Books',
            'slug': 'books',
            'description': 'Books and study material',
            'icon': 'book',
        },
        {
            'name': 'Electronics',
            'slug': 'electronics',
            'description': 'Electronics and gadgets',
            'icon': 'bolt',
        },
        {
            'name': 'Stationery',
            'slug': 'stationery',
            'description': 'Stationery and supplies',
            'icon': 'pencil',
        },
    ]
    for item in defaults:
        Category.objects.get_or_create(
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'description': item['description'],
                'icon': item['icon'],
                'is_active': True,
            }
        )


def delete_categories(apps, schema_editor):
    Category = apps.get_model('accounts', 'Category')
    Category.objects.filter(slug__in=['books', 'electronics', 'stationery']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_category_conversation_favorite_message_notification_and_more'),
    ]

    operations = [
        migrations.RunPython(create_categories, delete_categories),
    ]