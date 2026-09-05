# Script para analizar la estructura de la página de worldometers
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

output = []

try:
    # Abrir la página
    driver = webdriver.Chrome()
    driver.get('https://www.worldometers.info/world-population/argentina-population/')
    
    # Esperar a que cargue
    time.sleep(5)
    
    # Buscar todas las tablas en la página
    tables = driver.find_elements(By.TAG_NAME, 'table')
    output.append(f"Total de tablas encontradas: {len(tables)}\n")
    
    # Analizar cada tabla
    for idx, table in enumerate(tables):
        output.append(f"\n{'='*80}")
        output.append(f"TABLA {idx}")
        output.append(f"{'='*80}")
        
        # Obtener encabezados
        headers = table.find_elements(By.TAG_NAME, 'th')
        output.append(f"Encabezados ({len(headers)}):")
        for i, header in enumerate(headers):
            output.append(f"  {i}: {header.text[:50]}")
        
        # Obtener TODAS las filas para ver el rango
        rows = table.find_elements(By.TAG_NAME, 'tr')
        output.append(f"\nTotal de filas: {len(rows)}")
        
        if rows:
            output.append("\nPrimeras 5 filas:")
            for row_idx in range(min(5, len(rows))):
                cells = rows[row_idx].find_elements(By.TAG_NAME, 'td')
                if cells:
                    first_cell = cells[0].text.strip()
                    output.append(f"  Fila {row_idx}: Primer valor = '{first_cell}'")
            
            output.append("\nUltimas 3 filas:")
            for row_idx in range(max(0, len(rows)-3), len(rows)):
                cells = rows[row_idx].find_elements(By.TAG_NAME, 'td')
                if cells:
                    first_cell = cells[0].text.strip()
                    output.append(f"  Fila {row_idx}: Primer valor = '{first_cell}'")
    
    driver.quit()
    output.append("\n\nAnalisis completado")
    
except Exception as e:
    output.append(f"ERROR: {str(e)}")
    import traceback
    output.append(traceback.format_exc())

# Guardar resultado
with open('analysis_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Analisis guardado en analysis_result.txt")
