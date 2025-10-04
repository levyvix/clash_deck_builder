#!/usr/bin/env python3
"""
Environment Migration Script
Helps migrate from scattered environment files to centralized configuration.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import argparse


class EnvironmentMigrator:
    """Migrates environment variables from scattered files to centralized configuration."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.backup_dir = self.project_root / "env-backup"
        
    def find_env_files(self) -> List[Path]:
        """Find all existing environment files in the project."""
        env_files = []
        
        # Root level env files
        for pattern in [".env", ".env.*"]:
            env_files.extend(self.project_root.glob(pattern))
            
        # Backend env files
        backend_dir = self.project_root / "backend"
        if backend_dir.exists():
            for pattern in [".env", ".env.*"]:
                env_files.extend(backend_dir.glob(pattern))
                
        # Frontend env files
        frontend_dir = self.project_root / "frontend"
        if frontend_dir.exists():
            for pattern in [".env", ".env.*"]:
                env_files.extend(frontend_dir.glob(pattern))
                
        # Filter out template and example files from migration
        filtered_files = []
        for file in env_files:
            if not any(suffix in file.name for suffix in [".template", ".example"]):
                filtered_files.append(file)
                
        return filtered_files
    
    def parse_env_file(self, file_path: Path) -> Dict[str, str]:
        """Parse environment variables from a file."""
        env_vars = {}
        
        if not file_path.exists():
            return env_vars
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                        
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                            
                        env_vars[key] = value
                        
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")
            
        return env_vars
    
    def merge_env_vars(self, env_files: List[Path]) -> Dict[str, str]:
        """Merge environment variables from multiple files."""
        merged_vars = {}
        conflicts = {}
        
        for file_path in env_files:
            print(f"Processing: {file_path}")
            file_vars = self.parse_env_file(file_path)
            
            for key, value in file_vars.items():
                if key in merged_vars and merged_vars[key] != value:
                    # Track conflicts
                    if key not in conflicts:
                        conflicts[key] = []
                    conflicts[key].append((file_path, value))
                else:
                    merged_vars[key] = value
                    
        # Report conflicts
        if conflicts:
            print("\n⚠️  Conflicts detected:")
            for key, sources in conflicts.items():
                print(f"   {key}:")
                for source, value in sources:
                    print(f"     {source}: {value}")
                print(f"     Using: {merged_vars.get(key, 'UNKNOWN')}")
                
        return merged_vars
    
    def backup_files(self, env_files: List[Path]) -> None:
        """Backup existing environment files."""
        self.backup_dir.mkdir(exist_ok=True)
        
        print(f"\n📦 Backing up files to: {self.backup_dir}")
        
        for file_path in env_files:
            # Create relative path for backup
            rel_path = file_path.relative_to(self.project_root)
            backup_path = self.backup_dir / rel_path
            
            # Create parent directories
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ {rel_path} -> {backup_path}")
    
    def create_centralized_env(self, merged_vars: Dict[str, str]) -> None:
        """Create centralized .env file from merged variables."""
        env_file = self.project_root / ".env"
        
        print(f"\n📝 Creating centralized environment file: {env_file}")
        
        # Load template for structure and comments
        template_file = self.project_root / ".env.template"
        template_vars = {}
        template_structure = []
        
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                for line in f:
                    template_structure.append(line.rstrip())
                    if '=' in line and not line.strip().startswith('#'):
                        key = line.split('=')[0].strip()
                        template_vars[key] = True
        
        # Write new .env file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# =============================================================================\n")
            f.write("# CENTRALIZED ENVIRONMENT CONFIGURATION\n")
            f.write("# Generated by migration script\n")
            f.write("# =============================================================================\n\n")
            
            # Use template structure if available
            if template_structure:
                for line in template_structure:
                    if '=' in line and not line.strip().startswith('#'):
                        key = line.split('=')[0].strip()
                        if key in merged_vars:
                            f.write(f"{key}={merged_vars[key]}\n")
                            del merged_vars[key]  # Remove from remaining vars
                        else:
                            f.write(f"{line}\n")
                    else:
                        f.write(f"{line}\n")
                        
                # Add any remaining variables not in template
                if merged_vars:
                    f.write("\n# Additional variables from migration\n")
                    for key, value in sorted(merged_vars.items()):
                        f.write(f"{key}={value}\n")
            else:
                # No template, just write all variables
                for key, value in sorted(merged_vars.items()):
                    f.write(f"{key}={value}\n")
                    
        print(f"   ✅ Created {env_file} with {len(merged_vars)} variables")
    
    def validate_migration(self) -> bool:
        """Validate the migrated configuration."""
        print("\n🔍 Validating migrated configuration...")
        
        # Try to load the new configuration
        try:
            from pathlib import Path
            import sys
            
            # Add project root to path for imports
            sys.path.insert(0, str(self.project_root))
            
            # Try to import and validate backend config
            backend_src = self.project_root / "backend" / "src"
            if backend_src.exists():
                sys.path.insert(0, str(backend_src))
                try:
                    from utils.config import settings
                    settings.validate_configuration()
                    print("   ✅ Backend configuration valid")
                except Exception as e:
                    print(f"   ❌ Backend configuration error: {e}")
                    return False
                    
        except ImportError:
            print("   ⚠️  Could not validate backend configuration (dependencies not installed)")
            
        return True
    
    def cleanup_old_files(self, env_files: List[Path], confirm: bool = True) -> None:
        """Remove old environment files after successful migration."""
        if confirm:
            response = input("\n🗑️  Remove old environment files? (y/N): ")
            if response.lower() != 'y':
                print("Keeping old files. You can remove them manually after testing.")
                return
                
        print("\n🧹 Cleaning up old environment files...")
        
        for file_path in env_files:
            try:
                file_path.unlink()
                print(f"   ✅ Removed {file_path}")
            except Exception as e:
                print(f"   ❌ Could not remove {file_path}: {e}")
    
    def migrate(self, cleanup: bool = False, backup: bool = True) -> None:
        """Perform the complete migration process."""
        print("🚀 Starting environment migration...")
        
        # Find existing environment files
        env_files = self.find_env_files()
        if not env_files:
            print("No environment files found to migrate.")
            return
            
        print(f"Found {len(env_files)} environment files:")
        for file_path in env_files:
            print(f"   - {file_path}")
            
        # Backup existing files
        if backup:
            self.backup_files(env_files)
            
        # Merge environment variables
        merged_vars = self.merge_env_vars(env_files)
        print(f"\n📊 Merged {len(merged_vars)} unique environment variables")
        
        # Create centralized configuration
        self.create_centralized_env(merged_vars)
        
        # Validate migration
        if self.validate_migration():
            print("\n✅ Migration completed successfully!")
            
            # Cleanup old files if requested
            if cleanup:
                self.cleanup_old_files(env_files, confirm=True)
                
            print("\n📋 Next steps:")
            print("1. Review the generated .env file")
            print("2. Test your application with the new configuration")
            print("3. Update your documentation and deployment scripts")
            print("4. Remove old environment files when ready")
            
        else:
            print("\n❌ Migration validation failed. Please review the configuration.")


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description="Migrate scattered environment files to centralized configuration")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove old environment files after successful migration"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backing up existing files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )
    
    args = parser.parse_args()
    
    migrator = EnvironmentMigrator()
    
    if args.dry_run:
        print("🔍 Dry run mode - showing what would be migrated:")
        env_files = migrator.find_env_files()
        if env_files:
            print(f"Found {len(env_files)} files to migrate:")
            for file_path in env_files:
                vars_count = len(migrator.parse_env_file(file_path))
                print(f"   - {file_path} ({vars_count} variables)")
        else:
            print("No environment files found to migrate.")
    else:
        migrator.migrate(
            cleanup=args.cleanup,
            backup=not args.no_backup
        )


if __name__ == "__main__":
    main()