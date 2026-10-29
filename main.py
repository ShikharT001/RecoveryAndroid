"""
RecoveryAndroid — Android & WhatsApp Data Recovery
Desktop Application Entry Point
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.config import config
from app.core.logging_config import setup_logging
from app.storage.database import DatabaseManager
from app.storage.repository import StorageRepository


def parse_args():
    parser = argparse.ArgumentParser(description="RecoveryAndroid — Android & WhatsApp Data Recovery")
    parser.add_argument("--cli-check", action="store_true", help="Perform system & database integrity check and exit")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    return parser.parse_args()


def main():
    args = parse_args()
    log_level = 10 if args.debug else 20  # DEBUG or INFO
    logger = setup_logging(log_file=config.log_file, log_level=log_level)
    logger.info("Initializing RecoveryAndroid...")

    # Initialize Database & Repository
    db_mgr = DatabaseManager(config.db_path)
    repository = StorageRepository(db_mgr)
    stats = repository.get_dashboard_stats()
    logger.info(f"Database initialized. Total previous scans: {stats['total_scans']}")

    if args.cli_check:
        print("[RecoveryAndroid] System environment check passed:")
        print(f"  - App Data Dir: {config.data_dir}")
        print(f"  - Database: {config.db_path}")
        print(f"  - Log File: {config.log_file}")
        print(f"  - Historical Scans: {stats['total_scans']}")
        return 0

    # Launch PySide6 Desktop Application
    from PySide6.QtWidgets import QApplication
    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("RecoveryAndroid")
    app.setApplicationDisplayName("RecoveryAndroid — Android & WhatsApp Data Recovery")
    app.setOrganizationName("RecoveryAndroid")

    window = MainWindow(config=config, repository=repository)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
