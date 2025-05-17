"""
Client-Plugin für ClientC.
Dieses Plugin konvertiert Daten des ClientC im SQL- und FDK-Format in das kanonische Datenmodell.
"""

import logging
import os
import sys
import json
import re

# Use a simplified plugin implementation for testing
from .simplified import SimplifiedClientCPlugin

log = logging.getLogger(__name__)

# Re-export the simplified implementation
__all__ = ['SimplifiedClientCPlugin']