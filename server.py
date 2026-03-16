#!/usr/bin/env python3
"""
AutomotoraGV - Sistema de Gestion de Vehiculos
"""
import http.server
import json
import sqlite3
import hashlib
import os
import urllib.parse
from datetime import datetime

PORT = int(os.environ.get('PORT', 8765))
DB_PATH = os.path.join('/data', 'automotora.db') if os.path.exists('/data') else 'automotora.db'
