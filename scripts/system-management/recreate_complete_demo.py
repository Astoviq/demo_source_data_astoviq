#!/usr/bin/env python3
"""
EuroStyle Complete Demo Recreation Script
========================================

This script recreates the entire EuroStyle integrated demo environment from scratch,
including all cross-system integrations between HR, Operations, Finance, Webshop, and POS systems.

Execution Order:
1. Generate operational data (customers, orders, products, stores)
2. Build data registry for cross-system consistency
3. Generate webshop data with registry integration
4. Generate finance data with operational reconciliation
5. Generate HR data with employee/department structure
6. Generate HR-Finance payroll integration
7. Generate POS system with employee-order linkage
8. Generate POS-Finance commission integration

Total Generation Time: ~15-20 minutes
Total Data Volume: ~500MB+ across all systems
"""

import subprocess
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

class EuroStyleDemoRecreator:
    """Manages the complete recreation of the EuroStyle demo environment."""
    
    def __init__(self):
        """Initialize the demo recreator."""
        self.logger = logging.getLogger(__name__)
        self.scripts_path = Path(__file__).parent
        self.start_time = time.time()
        
        # Track completion status
        self.steps = [
            ("Operational Data Generation", "cd ../data-generator && python3 generate_data.py"),
            ("Data Registry Build", "python3 build_data_registry.py"),
            ("Webshop Data Generation", "python3 generate_webshop_with_registry.py"),
            ("Finance Data Generation", "python3 generate_finance_optimized.py"),
            ("HR Data Generation", "python3 generate_hr_data.py"),
            ("HR-Finance Integration", "python3 generate_hr_finance_integration.py"),
            ("POS System Generation", "python3 generate_pos_system.py"),
            ("POS-Finance Integration", "python3 generate_pos_finance_integration.py")
        ]
        
        self.completed_steps = []
        self.failed_steps = []
    
    def run_step(self, step_name: str, command: str) -> bool:
        """Execute a single step in the recreation process."""
        self.logger.info(f"🚀 Starting: {step_name}")
        self.logger.info(f"   Command: {command}")
        
        try:
            # Change to scripts directory for execution
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.scripts_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout per step
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ Completed: {step_name}")
                self.completed_steps.append(step_name)
                
                # Log some output for verification
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-3:]:  # Show last 3 lines
                        if line.strip():
                            self.logger.info(f"   {line}")
                
                return True
            else:
                self.logger.error(f"❌ Failed: {step_name}")
                self.logger.error(f"   Exit code: {result.returncode}")
                
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines[-5:]:  # Show last 5 error lines
                        if line.strip():
                            self.logger.error(f"   ERROR: {line}")
                
                self.failed_steps.append((step_name, result.stderr))
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Timeout: {step_name} (exceeded 30 minutes)")
            self.failed_steps.append((step_name, "Timeout after 30 minutes"))
            return False
        except Exception as e:
            self.logger.error(f"❌ Exception in {step_name}: {str(e)}")
            self.failed_steps.append((step_name, str(e)))
            return False
    
    def check_prerequisites(self) -> bool:
        """Check if all required files and directories exist."""
        self.logger.info("🔍 Checking prerequisites...")
        
        required_files = [
            "../data-generator/generate_data.py",
            "build_data_registry.py",
            "generate_webshop_with_registry.py", 
            "generate_finance_optimized.py",
            "generate_hr_data.py",
            "generate_hr_finance_integration.py",
            "generate_pos_system.py",
            "generate_pos_finance_integration.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.scripts_path / file_path
            if not full_path.exists():
                missing_files.append(str(full_path))
        
        if missing_files:
            self.logger.error("❌ Missing required files:")
            for missing in missing_files:
                self.logger.error(f"   {missing}")
            return False
        
        self.logger.info("✅ All prerequisite files found")
        return True
    
    def cleanup_previous_data(self) -> bool:
        """Clean up previous generated data."""
        self.logger.info("🧹 Cleaning up previous data...")
        
        try:
            # Remove old data files
            data_dirs = [
                self.scripts_path / "../generated_data",
                self.scripts_path / "../data-generator/generated_data"
            ]
            
            for data_dir in data_dirs:
                if data_dir.exists():
                    import shutil
                    # Instead of removing, create backup
                    backup_dir = data_dir.parent / f"{data_dir.name}_backup_{int(time.time())}"
                    if data_dir.exists() and list(data_dir.glob("*")):
                        shutil.move(str(data_dir), str(backup_dir))
                        self.logger.info(f"   Backed up existing data to: {backup_dir}")
                
                # Create fresh directory
                data_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("✅ Cleanup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {str(e)}")
            return False
    
    def verify_generation(self) -> None:
        """Verify the generated data volumes and integrity."""
        self.logger.info("🔍 Verifying generated data...")
        
        try:
            generated_data_path = self.scripts_path / "../generated_data"
            operational_data_path = self.scripts_path / "../data-generator/generated_data"
            
            # Count files and calculate sizes
            total_files = 0
            total_size = 0
            
            for data_path in [generated_data_path, operational_data_path]:
                if data_path.exists():
                    for file_path in data_path.rglob("*"):
                        if file_path.is_file():
                            total_files += 1
                            total_size += file_path.stat().st_size
            
            total_size_mb = total_size / (1024 * 1024)
            
            self.logger.info(f"📊 Generated data summary:")
            self.logger.info(f"   Total files: {total_files}")
            self.logger.info(f"   Total size: {total_size_mb:.1f} MB")
            
            # Check key files
            key_files = [
                ("Operational Orders", operational_data_path / "orders.csv"),
                ("Operational Customers", operational_data_path / "customers.csv"),
                ("Webshop Sessions", generated_data_path / "eurostyle_webshop.sessions.csv.gz"),
                ("Finance GL Headers", generated_data_path / "eurostyle_finance.gl_journal_headers.csv.gz"),
                ("HR Employees", generated_data_path / "eurostyle_hr.employees.csv.gz"),
                ("POS Transactions", generated_data_path / "eurostyle_pos.transactions.csv"),
            ]
            
            missing_key_files = []
            for name, file_path in key_files:
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    self.logger.info(f"   ✅ {name}: {size_mb:.1f} MB")
                else:
                    missing_key_files.append(name)
                    self.logger.error(f"   ❌ {name}: MISSING")
            
            if missing_key_files:
                self.logger.error("❌ Missing key data files - recreation may have failed")
            else:
                self.logger.info("✅ All key data files present")
                
        except Exception as e:
            self.logger.error(f"❌ Verification failed: {str(e)}")
    
    def recreate_demo(self) -> bool:
        """Execute the complete demo recreation process."""
        self.logger.info("🎬 EUROSTYLE COMPLETE DEMO RECREATION")
        self.logger.info("=" * 50)
        self.logger.info("This will regenerate the entire integrated demo environment")
        self.logger.info("Estimated time: 15-20 minutes")
        self.logger.info("Estimated data volume: 500+ MB")
        self.logger.info("")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Optional cleanup (commented out for safety)
        # if not self.cleanup_previous_data():
        #     return False
        
        # Execute all steps
        all_success = True
        for i, (step_name, command) in enumerate(self.steps, 1):
            step_start = time.time()
            
            self.logger.info("")
            self.logger.info(f"📍 STEP {i}/{len(self.steps)}: {step_name}")
            self.logger.info("-" * 50)
            
            success = self.run_step(step_name, command)
            
            step_duration = time.time() - step_start
            self.logger.info(f"   Duration: {step_duration:.1f} seconds")
            
            if not success:
                all_success = False
                self.logger.error(f"   Step {i} failed - stopping recreation")
                break
        
        # Final summary
        total_duration = time.time() - self.start_time
        self.logger.info("")
        self.logger.info("🏁 RECREATION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        self.logger.info(f"Completed steps: {len(self.completed_steps)}/{len(self.steps)}")
        
        if self.completed_steps:
            self.logger.info("✅ Successful steps:")
            for step in self.completed_steps:
                self.logger.info(f"   • {step}")
        
        if self.failed_steps:
            self.logger.info("❌ Failed steps:")
            for step, error in self.failed_steps:
                self.logger.info(f"   • {step}: {error[:100]}...")
        
        if all_success:
            self.logger.info("")
            self.logger.info("🎉 COMPLETE DEMO RECREATION SUCCESSFUL! 🎉")
            self.verify_generation()
        else:
            self.logger.error("")
            self.logger.error("❌ DEMO RECREATION FAILED")
        
        return all_success

def main():
    """Main function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('demo_recreation.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting EuroStyle Complete Demo Recreation")
    
    recreator = EuroStyleDemoRecreator()
    success = recreator.recreate_demo()
    
    if success:
        logger.info("Demo recreation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Demo recreation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()