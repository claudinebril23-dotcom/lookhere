from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.conf import settings
import json

class Command(BaseCommand):
    help = 'Display database tables and their structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            type=str,
            help='Show details for a specific table',
        )
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export table structure to JSON file',
        )

    def handle(self, *args, **options):
        # Check if we can connect to the database
        try:
            connection.ensure_connection()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Cannot connect to database: {e}')
            )
            self.stdout.write('\n💡 Make sure:')
            self.stdout.write('   1. PostgreSQL is running')
            self.stdout.write('   2. Database credentials in .env are correct')
            self.stdout.write('   3. Database exists (run: python setup_database.py)')
            return
        
        self.stdout.write(
            self.style.SUCCESS('📊 Database Structure - Photobooth Booking System')
        )
        self.stdout.write('=' * 60)
        
        # Show database info
        self.show_database_info()
        
        if options['table']:
            self.show_table_details(options['table'])
        else:
            self.show_all_tables()
            
        if options['export']:
            self.export_structure()

    def show_database_info(self):
        """Display basic database information"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version_result = cursor.fetchone()
                version = version_result[0] if version_result else "Unknown"
                
                cursor.execute("SELECT current_database();")
                db_result = cursor.fetchone()
                db_name = db_result[0] if db_result else "Unknown"
                
            self.stdout.write(f"\n🔗 Connection Info:")
            self.stdout.write(f"   Database: {db_name}")
            self.stdout.write(f"   Engine: {settings.DATABASES['default']['ENGINE']}")
            self.stdout.write(f"   Host: {settings.DATABASES['default']['HOST']}")
            self.stdout.write(f"   Port: {settings.DATABASES['default']['PORT']}")
            if version != "Unknown":
                version_parts = version.split()
                pg_version = version_parts[1] if len(version_parts) > 1 else "Unknown"
                self.stdout.write(f"   PostgreSQL: {pg_version}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting database info: {e}")
            )

    def show_all_tables(self):
        """Display all tables with row counts"""
        try:
            with connection.cursor() as cursor:
                # Get all tables
                cursor.execute("""
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                
                self.stdout.write(f"\n📋 Tables ({len(tables)}):")
                self.stdout.write("-" * 60)
                
                for table_name, table_type in tables:
                    # Get row count
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
                        count_result = cursor.fetchone()
                        row_count = count_result[0] if count_result else 0
                    except Exception:
                        row_count = "N/A"
                    
                    # Check if it's a Django model table
                    model_info = self.get_model_info(table_name)
                    
                    self.stdout.write(
                        f"   📊 {table_name:<30} | Rows: {row_count:<8} | {model_info}"
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting tables: {e}")
            )

    def get_model_info(self, table_name):
        """Get Django model information for a table"""
        try:
            # Try to find corresponding Django model
            for model in apps.get_models():
                if model._meta.db_table == table_name:
                    return f"Model: {model.__name__} ({model._meta.app_label})"
            return "System table"
        except:
            return "Unknown"

    def show_table_details(self, table_name):
        """Show detailed information about a specific table"""
        try:
            with connection.cursor() as cursor:
                # Get column information
                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position;
                """, [table_name])
                
                columns = cursor.fetchall()
                
                if not columns:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Table '{table_name}' not found")
                    )
                    return
                
                self.stdout.write(f"\n🔍 Table Details: {table_name}")
                self.stdout.write("-" * 60)
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
                count_result = cursor.fetchone()
                row_count = count_result[0] if count_result else 0
                self.stdout.write(f"   Total Rows: {row_count}")
                
                # Show columns
                self.stdout.write(f"\n   Columns ({len(columns)}):")
                for col_name, data_type, nullable, default, max_length in columns:
                    nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                    length_str = f"({max_length})" if max_length else ""
                    default_str = f" DEFAULT {default}" if default else ""
                    
                    self.stdout.write(
                        f"     • {col_name:<25} | {data_type}{length_str:<15} | {nullable_str}{default_str}"
                    )
                
                # Get indexes
                cursor.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes 
                    WHERE tablename = %s;
                """, [table_name])
                
                indexes = cursor.fetchall()
                if indexes and len(indexes) > 0:
                    self.stdout.write(f"\n   Indexes ({len(indexes)}):")
                    for idx_name, idx_def in indexes:
                        self.stdout.write(f"     • {idx_name}")
                
                # Show sample data
                cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT 3;")
                sample_rows = cursor.fetchall()
                
                if sample_rows:
                    self.stdout.write(f"\n   Sample Data (first 3 rows):")
                    col_names = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    for i, row in enumerate(sample_rows, 1):
                        self.stdout.write(f"     Row {i}:")
                        for col_name, value in zip(col_names, row):
                            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                            self.stdout.write(f"       {col_name}: {display_value}")
                        self.stdout.write("")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting table details: {e}")
            )

    def export_structure(self):
        """Export database structure to JSON file"""
        try:
            structure = {}
            
            with connection.cursor() as cursor:
                # Get all tables
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                table_results = cursor.fetchall()
                tables = [row[0] for row in table_results] if table_results else []
                
                for table_name in tables:
                    # Get columns
                    cursor.execute("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position;
                    """, [table_name])
                    
                    columns = []
                    column_results = cursor.fetchall()
                    if column_results:
                        for col_name, data_type, nullable, default, max_length in column_results:
                            columns.append({
                                'name': col_name,
                                'type': data_type,
                                'nullable': nullable == 'YES',
                                'default': default,
                                'max_length': max_length
                            })
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
                    count_result = cursor.fetchone()
                    row_count = count_result[0] if count_result else 0
                    
                    structure[table_name] = {
                        'columns': columns,
                        'row_count': row_count,
                        'model_info': self.get_model_info(table_name)
                    }
            
            # Export to file
            filename = 'database_structure.json'
            with open(filename, 'w') as f:
                json.dump(structure, f, indent=2, default=str)
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Database structure exported to {filename}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error exporting structure: {e}")
            )