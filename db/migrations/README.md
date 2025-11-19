# Database Migration Scripts

This directory contains migration scripts for database schema changes.

> **Note**: For general project information, see [README.md](../../README.md). For deployment instructions, see [DEPLOYMENT.md](../../DEPLOYMENT.md).

## Migration: Add ID Columns (v4.1.0)

**For Production/Existing Databases Only**

If you have an existing database (not recreated from seed), use these scripts to add the `id` columns to `orderdetails` and `payments` tables.

### Using Docker Compose

**Note**: If you're using Docker Compose for a demo database that should be recreated from the seed script every time you restart, you don't need these migration scripts. Simply run:

```bash
docker compose down -v  # Remove volumes to recreate database
docker compose up       # Database will be recreated from seed script
```

### For Existing Production Databases

If you have a production database with existing data that needs to be migrated:

1. **Backup your database first!**
   ```bash
   mysqldump -u your_user -p classicmodels > backup_before_migration.sql
   ```

2. **Run the migration** (choose one):
   
   **Idempotent version** (checks if columns already exist):
   ```bash
   mysql -u your_user -p classicmodels < db/migrations/add_id_columns_v4.1.0.sql
   ```
   
   **Simple version** (direct migration):
   ```bash
   mysql -u your_user -p classicmodels < db/migrations/add_id_columns_v4.1.0_simple.sql
   ```

3. **Verify the migration**:
   ```sql
   DESCRIBE orderdetails;
   DESCRIBE payments;
   ```

Both scripts will:
- Add `id INT NOT NULL AUTO_INCREMENT` as the primary key
- Convert the old composite primary keys to unique constraints
- Preserve all existing data

