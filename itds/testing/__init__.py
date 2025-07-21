"""
Itds Testing Module

This module provides a comprehensive framework for running tests in Itds applications.
It includes functionality for test discovery, execution, result reporting, and environment setup.

Key components:
- TestConfig: Configuration class for customizing test execution
- TestRunner: Main class for running test suites with additional Itds-specific functionality
- TestResult: Custom test result class for improved output formatting and logging
- discover_all_tests: Function to discover all tests in specified Itds apps
- discover_doctype_tests: Function to discover tests for specific DocTypes
- discover_module_tests: Function to discover tests in specific modules

The module also includes:
- Logging configuration for the testing framework
- Environment setup and teardown utilities
- Integration with Itds's hooks and test record creation system

Usage:
This module is typically used by Itds's CLI commands for running tests, but can also
be used programmatically for custom test execution scenarios.

Example:
    from itds.testing import TestConfig, TestRunner, discover_all_tests

    config = TestConfig(failfast=True, verbose=2)
    runner = TestRunner(cfg=config)
    discover_all_tests(['my_app'], runner)
    runner.run()
"""

import logging
import logging.config

from .config import TestConfig
from .discovery import discover_all_tests, discover_doctype_tests, discover_module_tests
from .result import TestResult
from .runner import TestRunner

logger = logging.getLogger(__name__)

from itds.utils.logger import create_handler as createItdsFileHandler

LOGGING_CONFIG = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {},
	"loggers": {
		f"{__name__}": {
			"handlers": [],  # only log to the itds handler
			"propagate": False,
		},
	},
}

logging.config.dictConfig(LOGGING_CONFIG)
handlers = createItdsFileHandler(__name__)
for handler in handlers:
	logger.addHandler(handler)
