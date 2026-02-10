# Broken Migrations for Training Exercises

This directory contains intentionally broken migration files for troubleshooting exercises.

**DO NOT apply these migrations to your database!**

## Files

### V6__add_achievements_BROKEN.sql
**Problem:** Missing foreign key constraint on `player_id`
**Symptoms:** Data integrity issues, orphaned achievement records
**Learning Goal:** Understanding foreign key constraints

### V8__add_region_NOT_NULL.sql
**Problem:** Adding NOT NULL constraint to existing column with NULL values
**Symptoms:** Migration fails with constraint violation
**Learning Goal:** Handling data cleanup before schema changes

### V10__load_match_batch2.sql
**Problem:** Referencing non-existent player IDs
**Symptoms:** Foreign key constraint violation
**Learning Goal:** Understanding referential integrity

## Usage

These files are for reference and learning purposes only. To practice:

1. Read the migration file
2. Identify the problem
3. Propose a fix
4. Discuss with your mentor

## Fixing Approach

For each broken migration:
1. Identify what constraint/requirement is violated
2. Determine what data preparation is needed
3. Write the corrected migration
4. Test in a safe environment
