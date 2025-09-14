#!/usr/bin/env python3
"""
CORTEX v2.1 Production-Ready Migration Script
С логированием, бэкапом и параллельной обработкой
"""

import os
import re
import json
import shutil
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'cortex_migration.log',
            maxBytes=1024 * 1024,  # 1 MB
            backupCount=5
        ),
        logging.StreamHandler()  # Вывод в консоль
    ]
)
logger = logging.getLogger(__name__)

class CortexProductionMigrator:
    def __init__(self, dry_run=True, create_backup=True):
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.start_time = time.time()
        self.migration_log = []
        self.stats = {
            'files_analyzed': 0,
            'files_migrated': 0,
            'errors': 0,
            'distribution': {}
        }
        
        self.ROUTING_RULES = {
            r'autosave.*\.md$': 'cortex-memory',
            r'session.*\.md$': 'cortex-memory', 
            r'brain-index.*\.md$': 'cortex-memory',
            r'claude-.*\.md$': 'cortex-memory',
            r'userPreferences.*': 'KEEP_IN_EYES',
            r'README\.md$': 'KEEP_IN_EYES',
            r'\.gitignore$': 'KEEP_IN_EYES',
            r'CORTEX.*\.md$': 'KEEP_IN_EYES'
        }
        
        logger.info("=" * 60)
        logger.info("CORTEX v2.1 Production Migrator initialized")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
        logger.info(f"Backup: {'ENABLED' if create_backup else 'DISABLED'}")
        logger.info("=" * 60)
    
    def backup_repository(self, repo_path: str) -> str:
        """Создаёт полный бэкап репозитория"""
        if not self.create_backup:
            logger.warning("Backup disabled, skipping...")
            return None
            
        backup_name = f"{repo_path}-BACKUP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            logger.info(f"Creating backup: {backup_name}")
            shutil.copytree(repo_path, backup_name, ignore=shutil.ignore_patterns('.git'))
            logger.info(f"✅ Backup created successfully: {backup_name}")
            return backup_name
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            raise
    
    def analyze_file(self, file_path: str) -> str:
        """Определяет целевой репозиторий для файла"""
        filename = os.path.basename(file_path)
        
        for pattern, target in self.ROUTING_RULES.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return target
        
        # По умолчанию - в память
        return 'cortex-memory'
    
    def migrate_file(self, source_path: str, target_repo: str) -> bool:
        """Безопасная миграция файла"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would migrate: {source_path} → {target_repo}")
                return True
            
            # Создание целевой директории
            target_base = f"../{target_repo}"
            os.makedirs(target_base, exist_ok=True)
            
            # Определение целевого пути
            relative_path = os.path.relpath(source_path, ".")
            target_path = os.path.join(target_base, relative_path)
            
            # Создание директорий
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Копирование файла (безопаснее чем move)
            shutil.copy2(source_path, target_path)
            
            # Удаление оригинала только после успешного копирования
            os.remove(source_path)
            
            logger.info(f"✅ Migrated: {relative_path} → {target_repo}")
            self.stats['files_migrated'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrating {source_path}: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_migration(self):
        """Запуск полной миграции с параллельной обработкой"""
        eyes_path = "."
        
        logger.info("Starting CORTEX v2.1 Migration...")
        
        # Создание бэкапа
        if self.create_backup and not self.dry_run:
            backup_path = self.backup_repository(eyes_path)
            if not backup_path:
                logger.error("Backup failed, aborting migration")
                return
        
        # Сбор файлов для миграции
        migration_tasks = []
        
        for root, dirs, files in os.walk(eyes_path):
            # Пропускаем .git и бэкапы
            if '.git' in root or 'BACKUP' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                self.stats['files_analyzed'] += 1
                
                # Определяем целевой репозиторий
                target_repo = self.analyze_file(file_path)
                
                if target_repo != 'KEEP_IN_EYES':
                    migration_tasks.append((file_path, target_repo))
                    
                    # Статистика распределения
                    if target_repo not in self.stats['distribution']:
                        self.stats['distribution'][target_repo] = 0
                    self.stats['distribution'][target_repo] += 1
        
        # Параллельная миграция
        if migration_tasks and not self.dry_run:
            logger.info(f"Migrating {len(migration_tasks)} files using 4 threads...")
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for file_path, target_repo in migration_tasks:
                    futures.append(
                        executor.submit(self.migrate_file, file_path, target_repo)
                    )
                
                # Ожидание завершения
                for future in futures:
                    future.result()
        
        # Генерация отчёта
        self.generate_report()
        
        # Финальная статистика
        elapsed_time = time.time() - self.start_time
        logger.info("=" * 60)
        logger.info("MIGRATION COMPLETED!")
        logger.info(f"⏱️  Time elapsed: {elapsed_time:.2f} seconds")
        logger.info(f"📊 Files analyzed: {self.stats['files_analyzed']}")
        logger.info(f"📊 Files migrated: {self.stats['files_migrated']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info("=" * 60)
    
    def generate_report(self):
        """Генерация JSON отчёта"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry_run' if self.dry_run else 'production',
            'stats': self.stats,
            'cortex_version': '2.1',
            'elapsed_time': time.time() - self.start_time
        }
        
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📋 Report saved: {report_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX v2.1 Migration Tool')
    parser.add_argument('--production', action='store_true', 
                       help='Run in production mode (actually move files)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Disable backup creation')
    
    args = parser.parse_args()
    
    migrator = CortexProductionMigrator(
        dry_run=not args.production,
        create_backup=not args.no_backup
    )
    
    migrator.run_migration()