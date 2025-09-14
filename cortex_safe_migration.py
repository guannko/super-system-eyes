#!/usr/bin/env python3
"""
CORTEX v2.1 Safe Migration Script
Безопасная миграция с dry-run и backup
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class CortexSafeMigrator:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.migration_log = []
        self.stats = {
            'files_analyzed': 0,
            'would_migrate': 0,
            'distribution': {}
        }
        
        self.ROUTING_RULES = {
            r'autosave.*\.md$': 'autosaves',
            r'session.*\.md$': 'autosaves', 
            r'brain-index.*\.md$': 'autosaves',
            r'userPreferences.*': 'KEEP_IN_EYES',  # Оставляем в eyes
            r'README\.md$': 'KEEP_IN_EYES',
            r'\.gitignore$': 'KEEP_IN_EYES'
        }
    
    def analyze_file(self, file_path: str) -> str:
        """Определяет что делать с файлом"""
        filename = os.path.basename(file_path)
        
        # Проверка по паттернам
        for pattern, action in self.ROUTING_RULES.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return action
        
        # По умолчанию оставляем в eyes
        return 'KEEP_IN_EYES'
    
    def scan_repository(self):
        """Сканирует super-system-eyes и показывает что будет перемещено"""
        eyes_path = "."  # Мы уже в super-system-eyes
        
        print("🔍 CORTEX v2.1 - Анализ репозитория super-system-eyes")
        print("=" * 60)
        
        for root, dirs, files in os.walk(eyes_path):
            # Пропускаем .git
            if '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, eyes_path)
                
                self.stats['files_analyzed'] += 1
                
                # Определяем действие
                action = self.analyze_file(file_path)
                
                if action != 'KEEP_IN_EYES':
                    self.stats['would_migrate'] += 1
                    
                    if action not in self.stats['distribution']:
                        self.stats['distribution'][action] = []
                    
                    self.stats['distribution'][action].append(relative_path)
                    
                    if self.dry_run:
                        print(f"  📄 {relative_path}")
                        print(f"     → Would move to: {action}/")
        
        # Отчёт
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ ЗАВЕРШЁН:")
        print(f"  Всего файлов: {self.stats['files_analyzed']}")
        print(f"  Будет перемещено: {self.stats['would_migrate']}")
        print(f"  Останется в eyes: {self.stats['files_analyzed'] - self.stats['would_migrate']}")
        
        if self.stats['distribution']:
            print("\n📦 РАСПРЕДЕЛЕНИЕ:")
            for target, files in self.stats['distribution'].items():
                print(f"  {target}: {len(files)} файлов")
                if len(files) <= 5:
                    for f in files:
                        print(f"    - {f}")
                else:
                    for f in files[:3]:
                        print(f"    - {f}")
                    print(f"    ... и ещё {len(files) - 3} файлов")
        
        return self.stats

if __name__ == "__main__":
    print("🧠 CORTEX v2.1 - Safe Migration Scanner")
    print("Mode: DRY RUN (безопасный режим)")
    print("")
    
    migrator = CortexSafeMigrator(dry_run=True)
    stats = migrator.scan_repository()
    
    # Сохраняем отчёт
    report = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'dry_run',
        'stats': stats
    }
    
    with open('migration_dry_run_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Отчёт сохранён в migration_dry_run_report.json")
    print("🔒 Это был DRY RUN - никакие файлы не были перемещены")