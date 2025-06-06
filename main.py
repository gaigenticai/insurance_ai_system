#!/usr/bin/env python3
"""
Main module for the Insurance AI System.

Modular, scalable entry point with full configurability and no hardcoded values.
Supports Railway.com deployment and local development.
"""

import argparse
import logging
import os
import sys
import asyncio
from typing import Dict, Any, Optional
import signal
import threading

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import modular components
from config.settings import get_settings, Settings
from core.service_bootstrap import initialize_services, shutdown_services, BootstrapConfig
from core.service_registry import get_service
from ai_services.ai_service_manager import AIServiceManager

logger = logging.getLogger(__name__)

class InsuranceAIApplication:
    """
    Main application class for the Insurance AI System
    
    Provides modular, scalable application management with full configurability.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.bootstrap = None
        self._shutdown_event = asyncio.Event()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.settings.app.log_level.upper())
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(log_dir, 'insurance_ai.log'), 'a')
            ]
        )
    
    async def initialize(self):
        """Initialize the application"""
        logger.info("Initializing Insurance AI System")
        
        try:
            # Create bootstrap configuration
            bootstrap_config = BootstrapConfig(
                enable_ai_services=self.settings.ai.enabled,
                enable_plugins=self.settings.app.enable_plugins,
                enable_monitoring=self.settings.app.enable_monitoring,
                enable_caching=self.settings.cache.enabled,
                startup_timeout=self.settings.app.startup_timeout
            )
            
            # Initialize services
            self.bootstrap = await initialize_services(bootstrap_config)

            # Initialize Sentry if DSN is provided
            if self.settings.app.sentry_dsn:
                sentry_sdk.init(
                    dsn=self.settings.app.sentry_dsn,
                    environment=self.settings.app.environment,
                    release=f"insurance-ai-system@{self.settings.app.version}",
                    traces_sample_rate=1.0,
                    profiles_sample_rate=1.0,
                )
                logger.info("Sentry initialized successfully.")

            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            logger.info("Insurance AI System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown")
            self._shutdown_event.set()

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        else:
            logger.warning("Signal handlers can only be set in the main thread; skipping")
    
    async def run_underwriting_analysis(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run underwriting analysis using AI services"""
        try:
            ai_manager = await get_service(AIServiceManager)
            response = await ai_manager.analyze_underwriting(application_data)
            
            return {
                "status": "success",
                "analysis": response.content,
                "confidence": response.confidence,
                "metadata": response.metadata
            }
            
        except Exception as e:
            logger.error(f"Underwriting analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_claims_analysis(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run claims analysis using AI services"""
        try:
            ai_manager = await get_service(AIServiceManager)
            response = await ai_manager.analyze_claims(claim_data)
            
            return {
                "status": "success",
                "analysis": response.content,
                "confidence": response.confidence,
                "metadata": response.metadata
            }
            
        except Exception as e:
            logger.error(f"Claims analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_actuarial_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run actuarial analysis using AI services"""
        try:
            ai_manager = await get_service(AIServiceManager)
            response = await ai_manager.analyze_actuarial(data)
            
            return {
                "status": "success",
                "analysis": response.content,
                "confidence": response.confidence,
                "metadata": response.metadata
            }
            
        except Exception as e:
            logger.error(f"Actuarial analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_demo_scenarios(self):
        """Run demonstration scenarios"""
        logger.info("Running demonstration scenarios")
        
        # Underwriting demo
        underwriting_data = {
            "applicant_id": "DEMO-UW-001",
            "full_name": "John Demo",
            "age": 35,
            "income": 75000,
            "credit_score": 720,
            "debt_to_income_ratio": 0.25,
            "property_value": 300000,
            "loan_amount": 240000
        }
        
        print("\n=== Underwriting Analysis Demo ===")
        uw_result = await self.run_underwriting_analysis(underwriting_data)
        print(f"Status: {uw_result['status']}")
        if uw_result['status'] == 'success':
            print(f"Analysis: {uw_result['analysis']}")
            print(f"Confidence: {uw_result['confidence']}")
        else:
            print(f"Error: {uw_result['error']}")
        
        # Claims demo
        claims_data = {
            "claim_id": "DEMO-CL-001",
            "policy_number": "POL-123456",
            "claim_type": "auto_accident",
            "incident_date": "2024-01-15",
            "description": "Rear-end collision at intersection",
            "estimated_damage": 5000,
            "claimant_statement": "I was stopped at a red light when the other vehicle hit me from behind"
        }
        
        print("\n=== Claims Analysis Demo ===")
        claims_result = await self.run_claims_analysis(claims_data)
        print(f"Status: {claims_result['status']}")
        if claims_result['status'] == 'success':
            print(f"Analysis: {claims_result['analysis']}")
            print(f"Confidence: {claims_result['confidence']}")
        else:
            print(f"Error: {claims_result['error']}")
        
        # Actuarial demo
        actuarial_data = {
            "analysis_type": "risk_assessment",
            "demographic_data": {
                "age_group": "25-35",
                "location": "urban",
                "occupation": "professional"
            },
            "historical_claims": [
                {"year": 2023, "claims": 150, "total_cost": 750000},
                {"year": 2022, "claims": 140, "total_cost": 680000}
            ]
        }
        
        print("\n=== Actuarial Analysis Demo ===")
        actuarial_result = await self.run_actuarial_analysis(actuarial_data)
        print(f"Status: {actuarial_result['status']}")
        if actuarial_result['status'] == 'success':
            print(f"Analysis: {actuarial_result['analysis']}")
            print(f"Confidence: {actuarial_result['confidence']}")
        else:
            print(f"Error: {actuarial_result['error']}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform application health check"""
        if not self.bootstrap:
            return {"status": "not_initialized"}
        
        return await self.bootstrap.health_check()
    
    async def shutdown(self):
        """Shutdown the application gracefully"""
        logger.info("Shutting down Insurance AI System")
        
        if self.bootstrap:
            await shutdown_services()
        
        logger.info("Insurance AI System shutdown complete")
    
    async def run(self):
        """Run the application"""
        try:
            await self.initialize()
            
            # Run demo scenarios if in demo mode
            if self.settings.app.demo_mode:
                await self.run_demo_scenarios()
            
            # Wait for shutdown signal
            logger.info("Insurance AI System is running. Press Ctrl+C to stop.")
            await self._shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self.shutdown()

def create_cli_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Insurance AI System - Modular, Scalable AI-Enhanced Insurance Platform'
    )
    
    parser.add_argument(
        '--mode', 
        type=str, 
        choices=['server', 'demo', 'health', 'ui'],
        default='demo',
        help='Application mode (default: demo)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port for UI server (default: 8080)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host for UI server (default: 0.0.0.0)'
    )
    
    return parser

async def main_async():
    """Async main function"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Override settings if config file provided
    if args.config:
        os.environ['CONFIG_FILE'] = args.config
    
    # Override log level if verbose
    if args.verbose:
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Create and run application
    app = InsuranceAIApplication()
    
    try:
        if args.mode == 'health':
            # Health check mode
            await app.initialize()
            health = await app.health_check()
            print(f"Health Status: {health['status']}")
            print(f"Services: {len(health.get('services', {}))}")
            for service, status in health.get('services', {}).items():
                print(f"  {service}: {status.get('status', 'unknown')}")
            return 0 if health['status'] == 'healthy' else 1
        
        elif args.mode == 'demo':
            # Demo mode - run demonstration scenarios
            await app.initialize()
            await app.run_demo_scenarios()
            return 0
        
        elif args.mode == 'server':
            # Server mode - run as service
            await app.run()
            return 0
        
        elif args.mode == 'ui':
            # UI mode - launch Streamlit interface
            print("Launching Streamlit UI...")
            streamlit_app_path = os.path.join(project_root, "ui", "streamlit_app.py")
            
            if os.path.exists(streamlit_app_path):
                import subprocess
                subprocess.run([
                    "streamlit",
                    "run",
                    streamlit_app_path,
                    "--server.port", str(args.port),
                    "--server.address", args.host
                ])
            else:
                print("Streamlit UI not available")
                return 1
            return 0
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    finally:
        await app.shutdown()

def main():
    """Main entry point"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


import sentry_sdk



