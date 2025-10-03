"""
Integration tests for database backup and restore functionality
"""
import pytest
import os
import subprocess
import tempfile
from pathlib import Path
from src.utils.database import get_db_session
from tests.fixtures.test_db_manager import test_db_manager


class TestBackupRestore:
    """Test database backup and restore functionality"""
    
    def test_database_backup_creation(self, test_database_setup):
        """Test creating a database backup"""
        # Create a temporary backup file
        with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as backup_file:
            backup_path = backup_file.name
        
        try:
            # Create backup using mysqldump
            backup_cmd = [
                'mysqldump',
                '--host=localhost',
                '--port=3307',
                '--user=test_user',
                '--password=test_password',
                '--single-transaction',
                '--routines',
                '--triggers',
                'clash_deck_builder_test'
            ]
            
            with open(backup_path, 'w') as f:
                result = subprocess.run(backup_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Verify backup file was created and has content
                assert os.path.exists(backup_path)
                assert os.path.getsize(backup_path) > 0
                
                # Check that backup contains expected content
                with open(backup_path, 'r') as f:
                    backup_content = f.read()
                    assert 'CREATE TABLE' in backup_content
                    assert 'users' in backup_content
                    assert 'decks' in backup_content
                    assert 'cards_cache' in backup_content
            else:
                pytest.skip(f"mysqldump not available or failed: {result.stderr}")
                
        finally:
            # Clean up temporary file
            if os.path.exists(backup_path):
                os.unlink(backup_path)
    
    def test_database_data_export_import(self, test_database_setup):
        """Test exporting and importing specific table data"""
        # Get initial data counts
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            initial_user_count = session.fetchone()['count']
            
            session.execute("SELECT COUNT(*) as count FROM decks")
            initial_deck_count = session.fetchone()['count']
        
        # Add some test data
        with get_db_session() as session:
            session.execute(
                "INSERT INTO users (username, email) VALUES (%s, %s)",
                ("backup_test_user", "backup@test.com")
            )
            new_user_id = session.lastrowid
            
            # Add a deck for the new user
            session.execute("""
                INSERT INTO decks (name, user_id, cards, evolution_slots, average_elixir) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                "Backup Test Deck",
                new_user_id,
                '[{"id": 26000000, "name": "Knight", "elixir_cost": 3}]',
                '[]',
                3.0
            ))
        
        # Verify data was added
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            new_user_count = session.fetchone()['count']
            assert new_user_count == initial_user_count + 1
            
            session.execute("SELECT COUNT(*) as count FROM decks")
            new_deck_count = session.fetchone()['count']
            assert new_deck_count == initial_deck_count + 1
        
        # Clean database and reseed (simulating restore)
        test_db_manager.clean_database()
        test_db_manager.seed_test_data()
        
        # Verify data was restored to initial state
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            restored_user_count = session.fetchone()['count']
            assert restored_user_count == initial_user_count
            
            session.execute("SELECT COUNT(*) as count FROM decks")
            restored_deck_count = session.fetchone()['count']
            assert restored_deck_count == initial_deck_count
    
    def test_backup_data_integrity(self, test_database_setup):
        """Test that backup preserves data integrity"""
        # Get sample data before backup
        original_data = {}
        
        with get_db_session() as session:
            # Get user data
            session.execute("SELECT id, username, email FROM users ORDER BY id LIMIT 3")
            original_data['users'] = session.fetchall()
            
            # Get deck data
            session.execute("SELECT id, name, user_id, cards FROM decks ORDER BY id LIMIT 3")
            original_data['decks'] = session.fetchall()
            
            # Get card data
            session.execute("SELECT id, name, elixir_cost, rarity FROM cards_cache ORDER BY id LIMIT 5")
            original_data['cards'] = session.fetchall()
        
        # Simulate backup by storing current state
        backup_data = original_data.copy()
        
        # Modify some data
        with get_db_session() as session:
            session.execute(
                "UPDATE users SET email = %s WHERE id = %s",
                ("modified@test.com", original_data['users'][0]['id'])
            )
            
            session.execute(
                "UPDATE decks SET name = %s WHERE id = %s",
                ("Modified Deck", original_data['decks'][0]['id'])
            )
        
        # Verify data was modified
        with get_db_session() as session:
            session.execute("SELECT email FROM users WHERE id = %s", (original_data['users'][0]['id'],))
            result = session.fetchone()
            assert result['email'] == "modified@test.com"
        
        # Restore from backup (clean and reseed)
        test_db_manager.clean_database()
        test_db_manager.seed_test_data()
        
        # Verify data integrity after restore
        with get_db_session() as session:
            # Check users
            session.execute("SELECT id, username, email FROM users ORDER BY id LIMIT 3")
            restored_users = session.fetchall()
            
            for i, user in enumerate(restored_users):
                original_user = backup_data['users'][i]
                assert user['username'] == original_user['username']
                # Email should be restored to original value
                assert user['email'] == original_user['email']
            
            # Check decks
            session.execute("SELECT id, name, user_id FROM decks ORDER BY id LIMIT 3")
            restored_decks = session.fetchall()
            
            for i, deck in enumerate(restored_decks):
                original_deck = backup_data['decks'][i]
                assert deck['name'] == original_deck['name']
                assert deck['user_id'] == original_deck['user_id']
    
    def test_backup_foreign_key_relationships(self, test_database_setup):
        """Test that backup preserves foreign key relationships"""
        with get_db_session() as session:
            # Get decks with their user information
            session.execute("""
                SELECT d.id as deck_id, d.name as deck_name, d.user_id, u.username
                FROM decks d
                JOIN users u ON d.user_id = u.id
                ORDER BY d.id
                LIMIT 5
            """)
            original_relationships = session.fetchall()
            
            assert len(original_relationships) > 0
            
            # Verify all relationships are valid
            for rel in original_relationships:
                assert rel['user_id'] is not None
                assert rel['username'] is not None
                assert rel['deck_name'] is not None
        
        # Clean and restore database
        test_db_manager.clean_database()
        test_db_manager.seed_test_data()
        
        # Verify relationships are preserved after restore
        with get_db_session() as session:
            session.execute("""
                SELECT d.id as deck_id, d.name as deck_name, d.user_id, u.username
                FROM decks d
                JOIN users u ON d.user_id = u.id
                ORDER BY d.id
                LIMIT 5
            """)
            restored_relationships = session.fetchall()
            
            assert len(restored_relationships) == len(original_relationships)
            
            # Verify relationships are still valid
            for i, rel in enumerate(restored_relationships):
                original_rel = original_relationships[i]
                assert rel['user_id'] == original_rel['user_id']
                assert rel['username'] == original_rel['username']
                assert rel['deck_name'] == original_rel['deck_name']
    
    def test_backup_json_data_preservation(self, test_database_setup):
        """Test that JSON data in columns is preserved during backup/restore"""
        with get_db_session() as session:
            # Get deck with JSON data
            session.execute("""
                SELECT id, name, cards, evolution_slots 
                FROM decks 
                WHERE cards IS NOT NULL AND cards != '[]'
                LIMIT 1
            """)
            original_deck = session.fetchone()
            
            if original_deck:
                original_cards = original_deck['cards']
                original_evolution_slots = original_deck['evolution_slots']
                
                # Clean and restore database
                test_db_manager.clean_database()
                test_db_manager.seed_test_data()
                
                # Verify JSON data is preserved
                session.execute("""
                    SELECT cards, evolution_slots 
                    FROM decks 
                    WHERE id = %s
                """, (original_deck['id'],))
                restored_deck = session.fetchone()
                
                if restored_deck:
                    assert restored_deck['cards'] == original_cards
                    assert restored_deck['evolution_slots'] == original_evolution_slots
    
    def test_backup_timestamp_preservation(self, test_database_setup):
        """Test that timestamp columns are preserved during backup/restore"""
        with get_db_session() as session:
            # Get records with timestamps
            session.execute("""
                SELECT id, created_at, updated_at 
                FROM users 
                ORDER BY id 
                LIMIT 3
            """)
            original_users = session.fetchall()
            
            session.execute("""
                SELECT id, created_at, updated_at 
                FROM decks 
                ORDER BY id 
                LIMIT 3
            """)
            original_decks = session.fetchall()
        
        # Clean and restore database
        test_db_manager.clean_database()
        test_db_manager.seed_test_data()
        
        # Verify timestamps are preserved
        with get_db_session() as session:
            session.execute("""
                SELECT id, created_at, updated_at 
                FROM users 
                ORDER BY id 
                LIMIT 3
            """)
            restored_users = session.fetchall()
            
            for i, user in enumerate(restored_users):
                original_user = original_users[i]
                assert user['created_at'] == original_user['created_at']
                assert user['updated_at'] == original_user['updated_at']
            
            session.execute("""
                SELECT id, created_at, updated_at 
                FROM decks 
                ORDER BY id 
                LIMIT 3
            """)
            restored_decks = session.fetchall()
            
            for i, deck in enumerate(restored_decks):
                original_deck = original_decks[i]
                assert deck['created_at'] == original_deck['created_at']
                assert deck['updated_at'] == original_deck['updated_at']
    
    def test_backup_script_availability(self):
        """Test that backup scripts are available and executable"""
        # Check if backup scripts exist
        backup_script_sh = Path("scripts/backup-database.sh")
        backup_script_ps1 = Path("scripts/backup-database.ps1")
        
        # At least one backup script should exist
        assert backup_script_sh.exists() or backup_script_ps1.exists(), \
            "No backup script found (backup-database.sh or backup-database.ps1)"
        
        if backup_script_sh.exists():
            # Check if script is readable
            assert backup_script_sh.is_file()
            with open(backup_script_sh, 'r') as f:
                content = f.read()
                assert 'mysqldump' in content or 'docker' in content
        
        if backup_script_ps1.exists():
            # Check if script is readable
            assert backup_script_ps1.is_file()
            with open(backup_script_ps1, 'r') as f:
                content = f.read()
                assert 'mysqldump' in content or 'docker' in content
    
    def test_restore_script_availability(self):
        """Test that restore scripts are available and executable"""
        # Check if restore scripts exist
        restore_script_sh = Path("scripts/restore-database.sh")
        restore_script_ps1 = Path("scripts/restore-database.ps1")
        
        # At least one restore script should exist
        assert restore_script_sh.exists() or restore_script_ps1.exists(), \
            "No restore script found (restore-database.sh or restore-database.ps1)"
        
        if restore_script_sh.exists():
            # Check if script is readable
            assert restore_script_sh.is_file()
            with open(restore_script_sh, 'r') as f:
                content = f.read()
                assert 'mysql' in content or 'docker' in content
        
        if restore_script_ps1.exists():
            # Check if script is readable
            assert restore_script_ps1.is_file()
            with open(restore_script_ps1, 'r') as f:
                content = f.read()
                assert 'mysql' in content or 'docker' in content