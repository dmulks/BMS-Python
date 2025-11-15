# Excel Import Guide

## Overview

The Bond Management System includes an Excel import feature that allows you to bulk import users and bond purchases from Excel spreadsheets.

## Script Location

```
backend/scripts/import_bonds_from_excel.py
```

## Usage

### Basic Command

```bash
cd backend
./venv/bin/python scripts/import_bonds_from_excel.py <excel_file_path>
```

### With Options

```bash
./venv/bin/python scripts/import_bonds_from_excel.py <excel_file_path> \
  --date YYYY-MM-DD \
  --bond-type "Bond Type Name"
```

### Options

- `file_path` (required): Path to the Excel file
- `--date` (optional): Purchase date in YYYY-MM-DD format (default: today)
- `--bond-type` (optional): Bond type name (default: "2-Year Bond")

### Example

```bash
./venv/bin/python scripts/import_bonds_from_excel.py \
  "/path/to/Coupon Payment Calculations 2023.xlsx" \
  --date 2023-12-20 \
  --bond-type "2-Year Bond"
```

## Excel File Format

### Required Columns

The Excel file should have the following columns (with exact names):

| Column Name | Description | Example |
|------------|-------------|---------|
| `No` | Member number | 1 |
| `First Name` | Member first name | James |
| `Last Name` | Member last name | Smith |
| `Email` | Member email (unique) | james.smith@example.com |
| `Bond Shares` | Number of bond shares | 10000 |
| `FACE Value ` | Face value of bonds (note trailing space) | 21891.42 |
| `Discount Value Paid on Maturity` | Discount value | 2863.68 |
| `Less 2%\n Co-op  Discount Fee` | Co-op discount fee (2% of discount) | 57.27 |

### Notes

- The script expects the data to start on **row 2** (row 1 should be headers)
- Email addresses must be unique and valid
- Bond Shares must be a positive number
- All monetary values should be numeric

## What the Script Does

### 1. User Management

- **Creates new users** if they don't exist (based on email)
- **Updates existing users** if names have changed
- Generates usernames from email addresses (before @)
- Sets default password: `change123` for new users
- Assigns role: `MEMBER` to all imported users

### 2. Bond Purchase Creation

For each row with valid data:
- Creates a bond purchase record
- Links to the user (by email)
- Links to the specified bond type
- Calculates:
  - Purchase month (first day of month)
  - Maturity date (based on bond type)
  - Co-op discount fee (2% of discount value)
  - Net discount value
  - Purchase price (face value - discount value)
- Sets status: `ACTIVE`

### 3. Duplicate Detection

The script checks for duplicate bond purchases based on:
- User
- Bond type
- Purchase date
- Face value

If a duplicate is found, it skips that record.

## Output

The script provides detailed output including:

```
📊 Reading Excel file: /path/to/file.xlsx
✅ Using bond type: 2-Year Bond
  ✅ Created user: james.smith@example.com (username: james.smith)
  💰 Created bond for james.smith@example.com: Face Value=21891.42, Price Paid=19027.74
  ...

============================================================
📈 IMPORT SUMMARY
============================================================
✅ Users created: 20
📝 Users updated: 0
💰 Bond purchases created: 20
============================================================

🔑 Default password for new users: change123
   Users should change their password after first login.
```

## Error Handling

### Common Errors

1. **Invalid email**: Skipped with error message
2. **Missing required data**: Row skipped
3. **Duplicate bond**: Row skipped with notification
4. **Bond type not found**: Import stops, shows available types

### Error Log

Errors are displayed in the summary:

```
⚠️  Errors encountered: 3
  - Row 5: Invalid email 'badformat'
  - Row 12: 'FACE Value'
  - Row 23: Missing Bond Shares
```

## Post-Import Tasks

After successful import:

1. **Notify users** to login and change their default password
2. **Verify data** in the web interface at http://localhost:5173
3. **Review bond purchases** in the Bonds page
4. **Check user accounts** in the admin panel

## Troubleshooting

### "Bond type not found"

Available bond types:
- 2-Year Bond
- 5-Year Bond
- 15-Year Bond

Make sure to specify the exact name with `--bond-type`.

### "Column not found"

Check that your Excel file has the exact column names, including:
- Spaces
- Newlines (`\n`)
- Trailing spaces (e.g., `FACE Value ` has a trailing space)

### "No bonds created"

Possible causes:
- All rows have `Bond Shares = 0` or empty
- All bonds are duplicates
- Column names don't match

Run with Python directly to see full error traceback:

```bash
./venv/bin/python scripts/import_bonds_from_excel.py your_file.xlsx
```

## Best Practices

1. **Backup first**: Always backup your database before importing
2. **Test with small file**: Test with a few rows first
3. **Verify column names**: Ensure exact matches including spaces
4. **Check dates**: Verify purchase dates are correct
5. **Review output**: Check the summary for any errors

## Database Backup

Before importing, create a backup:

```bash
# SQLite backup
cp bond_management.db bond_management.db.backup.$(date +%Y%m%d)
```

## Support

If you encounter issues:

1. Check the error messages in the output
2. Verify Excel file format matches requirements
3. Ensure all required columns exist
4. Check that bond type exists in database
5. Review the bond purchase model requirements

## Advanced Usage

### Import Multiple Files

```bash
for file in *.xlsx; do
  ./venv/bin/python scripts/import_bonds_from_excel.py "$file" --date 2023-12-20
done
```

### Custom Bond Types

First, ensure the bond type exists in the database, then:

```bash
./venv/bin/python scripts/import_bonds_from_excel.py file.xlsx --bond-type "5-Year Bond"
```

### Scripted Import

Create a bash script for regular imports:

```bash
#!/bin/bash
EXCEL_FILE="/path/to/monthly_bonds.xlsx"
DATE=$(date +%Y-%m-01)  # First day of current month

cd /path/to/backend
./venv/bin/python scripts/import_bonds_from_excel.py \
  "$EXCEL_FILE" \
  --date "$DATE" \
  --bond-type "2-Year Bond"
```
