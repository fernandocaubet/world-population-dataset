#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el scraping funciona correctamente
"""

import sys
sys.path.insert(0, 'src')

from scraping import get_country_data

# Probar con Argentina
print("TEST: Iniciando prueba de scraping para Argentina...\n")

try:
    get_country_data(
        'argentina',
        'https://www.worldometers.info/world-population/argentina-population/'
    )
    print("\nSUCCESS: Prueba completada exitosamente")
except Exception as e:
    print(f"\nERROR: Error durante la prueba: {str(e)}")
    import traceback
    traceback.print_exc()
