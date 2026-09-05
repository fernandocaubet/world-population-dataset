# ============================================================================
# WEB SCRAPING MODULE - Descarga datos de población de worldometers.info
# ============================================================================

from selenium import webdriver  # Automatización de navegador web
from selenium.webdriver.common.by import By  # Selectores para encontrar elementos
import csv  # Escritura de archivos CSV
import re  # Expresiones regulares para limpiar texto
import time  # Para esperar que cargue la página

def get_country_data(country, url):
    """
    Extrae datos históricos y proyecciones de población para un país específico.
    
    Args:
        country (str): Nombre del país (ej: 'argentina', 'china', 'india')
        url (str): URL de worldometers.info para ese país
    
    Proceso:
        1. Abre el navegador y carga la URL
        2. Identifica dinámicamente las tablas de datos históricos y proyecciones
        3. Extrae datos de ambas tablas
        4. Guarda ambos en archivos CSV separados
    """
    # ========== FASE 1: INICIALIZAR NAVEGADOR Y CARGAR PÁGINA ==========
    print(f"[DOWNLOAD] Descargando datos de {country}...")
    driver = webdriver.Chrome()
    driver.get(url)
    
    # Esperar a que las tablas carguen
    time.sleep(3)
    
    try:
        # ========== FASE 2: ENCONTRAR TABLAS DINÁMICAMENTE ==========
        tables = driver.find_elements(By.TAG_NAME, 'table')
        print(f"[OK] Encontradas {len(tables)} tablas en la página")
        
        # Buscar las tablas correctas por sus encabezados
        historical_table = None
        forecast_table = None
        
        for idx, table in enumerate(tables):
            try:
                headers = table.find_elements(By.TAG_NAME, 'th')
                header_texts = [h.text.strip() for h in headers]
                
                # Debe tener "Year" y "Population" para ser tabla de población
                if 'Year' in header_texts and 'Population' in header_texts:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    if len(rows) > 1:
                        first_row_cells = rows[1].find_elements(By.TAG_NAME, 'td')
                        if first_row_cells:
                            first_year = first_row_cells[0].text.strip()
                            
                            # Convertir a entero para comparar
                            try:
                                year_int = int(first_year)
                            except ValueError:
                                continue
                            
                            # Si primer año es 2024-2029: tabla histórica
                            if 2024 <= year_int < 2030 and not historical_table:
                                historical_table = (table, header_texts, idx, year_int)
                                print(f"[OK] Tabla histórica encontrada en índice {idx} (primer año: {year_int})")
                            
                            # Si primer año es 2030+: tabla forecast
                            elif year_int >= 2030 and not forecast_table:
                                forecast_table = (table, header_texts, idx, year_int)
                                print(f"[OK] Tabla forecast encontrada en índice {idx} (primer año: {year_int})")
            except:
                continue
        
        # ========== FASE 3: EXTRAER DATOS HISTÓRICOS ==========
        if historical_table:
            print("\n[HISTORICAL] Extrayendo datos históricos...")
            historical_data = extract_table_data(historical_table[0], country, historical_table[1])
            save_to_csv(historical_data, f'./data/population/countries/{country}-population.csv')
            print(f"[OK] Datos históricos guardados ({len(historical_data)} filas)")
        else:
            print("[WARNING] No se encontró tabla de datos históricos")
        
        # ========== FASE 4: EXTRAER DATOS DE PROYECCIÓN ==========
        if forecast_table:
            print("\n[FORECAST] Extrayendo datos de proyección...")
            forecast_data = extract_table_data(forecast_table[0], country, forecast_table[1])
            save_to_csv(forecast_data, f'./data/forecast/countries/{country}-forecast.csv')
            print(f"[OK] Datos de proyección guardados ({len(forecast_data)} filas)")
        else:
            print("[WARNING] No se encontró tabla de datos de proyección")
        
    finally:
        # ========== FASE 5: CERRAR NAVEGADOR ==========
        driver.quit()
        print("[OK] Navegador cerrado")
    
    # ========== FASE 6: MOSTRAR DATOS SI ES ARGENTINA ==========
    if country.lower() == 'argentina':
        display_country_data(country)


def extract_table_data(table_element, country, headers, min_year=1950):
    """
    Extrae datos de una tabla HTML.
    
    Args:
        table_element: Elemento de tabla de Selenium
        country (str): Nombre del país para la primera columna
        headers (list): Lista de nombres de encabezados
        min_year (int): Año mínimo a incluir en los datos (default: 2000)
    
    Returns:
        list: Lista de listas con los datos (incluyendo encabezados como primera fila)
    """
    data = []
    
    # Agregar encabezados con 'country' como primera columna
    data.append(['country'] + headers)
    
    # Extraer filas del cuerpo de la tabla
    tbody = table_element.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            # Obtener el año de la primera celda
            year_text = cells[0].text.strip()
            try:
                year = int(year_text)
                # Filtrar solo años >= min_year
                if year < min_year:
                    continue
            except ValueError:
                # Si no es un número, saltarlo
                continue
            
            row_data = [country.title().replace('-', ' ')]  # Primera columna: país
            
            for cell in cells:
                # Limpiar texto: remover comas de números
                text = cell.text.strip()
                text = re.sub(',', '', text)
                row_data.append(text)
            
            data.append(row_data)
    
    return data


def save_to_csv(data, filepath):
    """
    Guarda datos en un archivo CSV.
    
    Args:
        data (list): Lista de listas con datos
        filepath (str): Ruta donde guardar el archivo
    """
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
    except FileNotFoundError:
        print(f"[ERROR] Directorio no existe: {filepath}")
    except Exception as e:
        print(f"[ERROR] Error al guardar CSV: {str(e)}")


def display_country_data(country):
    """
    Muestra en consola los datos históricos y de proyección para un país específico.
    
    Args:
        country (str): Nombre del país (debe existir en los archivos CSV generados)
    
    Muestra:
        - Datos históricos de población
        - Datos de proyecciones futuras
        - Ambas tablas en formato legible
    """
    import pandas as pd
    
    print("\n" + "="*80)
    print(f"[DATA] DATOS DE POBLACIÓN PARA {country.upper()}")
    print("="*80)
    
    # ========== MOSTRAR DATOS HISTÓRICOS ==========
    population_file = f'./data/population/countries/{country}-population.csv'
    try:
        df_population = pd.read_csv(population_file)
        print(f"\n[OK] DATOS HISTÓRICOS ({population_file}):")
        print("-" * 80)
        print(df_population.to_string(index=False))
    except FileNotFoundError:
        print(f"\n[ERROR] No se encontró el archivo {population_file}")
    except Exception as e:
        print(f"\n[ERROR] Error al leer {population_file}: {str(e)}")
    
    # ========== MOSTRAR DATOS DE PROYECCIÓN ==========
    forecast_file = f'./data/forecast/countries/{country}-forecast.csv'
    try:
        df_forecast = pd.read_csv(forecast_file)
        print(f"\n[OK] DATOS DE PROYECCIÓN ({forecast_file}):")
        print("-" * 80)
        print(df_forecast.to_string(index=False))
    except FileNotFoundError:
        print(f"\n[ERROR] No se encontró el archivo {forecast_file}")
    except Exception as e:
        print(f"\n[ERROR] Error al leer {forecast_file}: {str(e)}")
    
    print("\n" + "="*80 + "\n")