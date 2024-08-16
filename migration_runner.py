import importlib
import os
from models import MigrationRecord
from datetime import datetime

# Directory where migration scripts are stored
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")

async def run_migrations():
    migration_files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.startswith("migration_") and f.endswith(".py"))

    for migration_file in migration_files:
        migration_name = migration_file.split('.')[0]
        
        # Check if migration has already been applied
        existing_migration = await MigrationRecord.find_one({"name": migration_name})
        if existing_migration:
            print(f"Migration {migration_name} already applied.")
            continue
        
        # Import and run the migration
        try:
            module_name = f"migrations.{migration_name}"
            module = importlib.import_module(module_name)
            await module.migrate()
        except AttributeError as e:
            print(f"Migration {migration_name} does not have a 'migrate' function. Error: {e}")
            continue
        except ModuleNotFoundError as e:
            print(f"Migration file {migration_name} not found. Error: {e}")
            continue
        
        # Record the migration
        migration_record = MigrationRecord(name=migration_name, applied_at=datetime.now())
        await migration_record.insert()

        print(f"Migration {migration_name} applied successfully.")
