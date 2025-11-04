#!/usr/bin/env python3
"""
AutoFire AI Debug Logger - Attempt #3
=====================================
Setting up comprehensive logging BEFORE any operations to catch real issues.
"""

import sys
import logging
import traceback
from datetime import datetime
import os

# Set up comprehensive logging
log_file = f"autofire_debug_attempt3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging with multiple levels
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("AutoFireDebug")

def safe_operation_with_logging(operation_name, operation_func, *args, **kwargs):
    """Execute any operation with comprehensive logging"""
    logger.info(f"🔍 STARTING: {operation_name}")
    logger.info(f"   Args: {args}")
    logger.info(f"   Kwargs: {kwargs}")
    
    try:
        logger.info(f"   Executing operation...")
        result = operation_func(*args, **kwargs)
        logger.info(f"✅ SUCCESS: {operation_name}")
        logger.info(f"   Result type: {type(result)}")
        logger.info(f"   Result: {str(result)[:200]}...")
        return result, None
        
    except Exception as e:
        logger.error(f"❌ CRASH: {operation_name}")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Full traceback:")
        logger.error(traceback.format_exc())
        return None, e

def test_rfi_engine_with_logging():
    """Test RFI engine with comprehensive logging"""
    logger.info("🚀 STARTING RFI ENGINE DEBUG TEST - ATTEMPT #3")
    logger.info("=" * 60)
    
    # Step 1: Import test
    def import_rfi():
        sys.path.append('C:/Dev/Autofire')
        from cad_core.intelligence.rfi_engine import RFIIntelligenceEngine
        return RFIIntelligenceEngine
    
    RFIClass, error = safe_operation_with_logging("Import RFI Engine", import_rfi)
    if error:
        logger.error("🚫 FAILED AT IMPORT STAGE")
        return False
    
    # Step 2: Instantiation test
    def create_engine():
        return RFIClass()
    
    engine, error = safe_operation_with_logging("Create RFI Engine Instance", create_engine)
    if error:
        logger.error("🚫 FAILED AT INSTANTIATION STAGE")
        return False
    
    # Step 3: Method discovery
    def get_methods():
        methods = [m for m in dir(engine) if not m.startswith('_')]
        logger.info(f"Available methods: {methods}")
        return methods
    
    methods, error = safe_operation_with_logging("Get Available Methods", get_methods)
    if error:
        logger.error("🚫 FAILED AT METHOD DISCOVERY STAGE")
        return False
    
    # Step 4: Test each method that looks like analysis
    analysis_methods = [m for m in methods if 'analyze' in m.lower()]
    logger.info(f"Found analysis methods: {analysis_methods}")
    
    for method_name in analysis_methods:
        logger.info(f"🧪 TESTING METHOD: {method_name}")
        
        def test_method():
            method = getattr(engine, method_name)
            logger.info(f"   Method signature: {method}")
            # Try with minimal args first
            try:
                result = method("test_project")
                return result
            except TypeError as te:
                logger.warning(f"   TypeError with simple args: {te}")
                # Try with no args
                try:
                    result = method()
                    return result
                except Exception as e2:
                    logger.warning(f"   Also failed with no args: {e2}")
                    raise te  # Re-raise original error
        
        result, error = safe_operation_with_logging(f"Test Method: {method_name}", test_method)
        
        if not error and result:
            logger.info(f"✅ METHOD {method_name} WORKS!")
            logger.info(f"   Result type: {type(result)}")
            
            # Inspect result attributes safely
            def inspect_result():
                attrs = [attr for attr in dir(result) if not attr.startswith('_')]
                logger.info(f"   Result attributes: {attrs}")
                
                # Check for common RFI attributes
                for attr in ['rfi_items', 'issues', 'items', 'results']:
                    if hasattr(result, attr):
                        value = getattr(result, attr)
                        logger.info(f"   {attr}: {type(value)} = {value}")
                        
                        if isinstance(value, list) and value:
                            first_item = value[0]
                            item_attrs = [a for a in dir(first_item) if not a.startswith('_')]
                            logger.info(f"   First {attr} item attributes: {item_attrs}")
                
                return attrs
            
            attrs, inspect_error = safe_operation_with_logging(f"Inspect {method_name} Result", inspect_result)
            
            if inspect_error:
                logger.error(f"⚠️  Failed to inspect result of {method_name}")
            else:
                logger.info(f"✅ Successfully inspected {method_name} result")
                
        else:
            logger.warning(f"⚠️  METHOD {method_name} failed or returned None")
    
    logger.info("🏁 RFI ENGINE DEBUG TEST COMPLETE")
    return True

if __name__ == "__main__":
    logger.info("🔥 AutoFire AI Debug Session - Attempt #3")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    success = test_rfi_engine_with_logging()
    
    if success:
        logger.info("🎉 DEBUG SESSION COMPLETED SUCCESSFULLY")
    else:
        logger.error("💥 DEBUG SESSION FAILED")
    
    logger.info(f"📄 Full log saved to: {log_file}")
    print(f"\n📄 Complete log saved to: {log_file}")