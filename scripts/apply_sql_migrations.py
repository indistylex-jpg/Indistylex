#!/usr/bin/env python3
"""Apply pending SQL migration scripts using DATABASE_URL from .env."""
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import dotenv_values  # noqa: E402

DEFAULT_SCRIPTS = [
    'scripts/alter_product_age_groups_v2.sql',
    'scripts/create_expenses_table.sql',
    'scripts/alter_product_cost_price.sql',
    'scripts/alter_order_item_cost_price.sql',
]


def parse_database_url(url):
    if not url or not url.startswith('mysql'):
        raise SystemExit('DATABASE_URL must be a mysql:// or mysql+pymysql:// URI')
    raw = url.split('://', 1)[1]
    creds, hostpart = raw.rsplit('@', 1)
    user, password = creds.split(':', 1)
    hostport, dbname = hostpart.split('/', 1)
    dbname = dbname.split('?', 1)[0]
    return unquote(user), unquote(password), dbname


def main():
    env = dotenv_values(ROOT / '.env')
    db_url = env.get('DATABASE_URL') or os.environ.get('DATABASE_URL')
    user, password, dbname = parse_database_url(db_url)
    scripts = sys.argv[1:] or DEFAULT_SCRIPTS

    for rel in scripts:
        path = ROOT / rel
        if not path.is_file():
            print(f'SKIP missing {rel}')
            continue
        print(f'Applying {rel}…')
        result = subprocess.run(
            ['mysql', f'-u{user}', f'-p{password}', dbname],
            input=path.read_bytes(),
            capture_output=True,
        )
        if result.returncode != 0:
            err = result.stderr.decode(errors='replace').strip()
            if 'Duplicate column name' in err or 'already exists' in err.lower():
                print(f'  already applied ({rel})')
                continue
            print(err)
            raise SystemExit(result.returncode)
        print(f'  OK ({rel})')

    print('Migrations complete.')


if __name__ == '__main__':
    main()
