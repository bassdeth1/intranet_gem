import os

def listar_directorio_completo(directorio_raiz, archivo_salida, prefijo='', ignorar=None):
    """
    Lista recursivamente directorios, subdirectorios y archivos,
    escribiendo la estructura y el contenido completo de los archivos de texto en archivo_salida.
    """
    if ignorar is None:
        # Añadido z.txt para no listarse a sí mismo si se ejecuta múltiples veces en el mismo dir.
        # También he añadido listar_proyecto.py para que no se incluya si el script se llama así.
        ignorar = [
            '.git', '__pycache__', '.vscode', 'node_modules', 'venv', '.env', 
            'db.sqlite3', 'listar_proyecto.py', 'z.txt'
        ] 
    
    try:
        # Ordenar para una visualización consistente
        archivos_y_carpetas = sorted(os.listdir(directorio_raiz))
    except FileNotFoundError:
        archivo_salida.write(f"{prefijo}└── ERROR: No se pudo acceder a {directorio_raiz} (No encontrado)\n")
        return
    except PermissionError:
        archivo_salida.write(f"{prefijo}└── ERROR: Permiso denegado para acceder a {directorio_raiz}\n")
        return

    for i, nombre_item in enumerate(archivos_y_carpetas):
        ruta_completa = os.path.join(directorio_raiz, nombre_item)
        
        # Ignorar carpetas y archivos especificados
        # Comprobar también si el nombre del script actual está en la lista de ignorados
        if nombre_item in ignorar or nombre_item == os.path.basename(__file__):
            continue

        # Determinar conector para la estructura de árbol
        if i == len(archivos_y_carpetas) - 1: # Último elemento
            conector = '└── '
            nuevo_prefijo_para_sub = prefijo + '    ' # Espacios para el siguiente nivel
        else:
            conector = '├── '
            nuevo_prefijo_para_sub = prefijo + '│   ' # Barra vertical y espacios
            
        archivo_salida.write(f"{prefijo}{conector}{nombre_item}\n")
        
        if os.path.isdir(ruta_completa):
            # Llamada recursiva, pasando el objeto archivo_salida
            listar_directorio_completo(ruta_completa, archivo_salida, nuevo_prefijo_para_sub, ignorar)
        elif os.path.isfile(ruta_completa):
            mostrar_contenido = False
            # Extensiones de archivo cuyo contenido se intentará mostrar
            extensiones_permitidas = ('.py', '.html', '.css', '.js', '.txt', '.md', '.json', '.yml', '.yaml', '.sql', '.rst', '.ini', '.cfg', '.toml', '.sh', '.bat', '.ps1')
            if nombre_item.endswith(extensiones_permitidas):
                mostrar_contenido = True
            
            if mostrar_contenido:
                try:
                    # Usar 'errors='ignore'' para evitar problemas con archivos que puedan tener caracteres no decodificables en UTF-8
                    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                        # Leer todo el contenido
                        contenido = f.read() 
                        # No hacer strip() aquí para mantener indentación original si el archivo empieza/termina con espacios/saltos
                        lineas_contenido = contenido.splitlines()
                        
                        if lineas_contenido: # Solo muestra si hay contenido
                            archivo_salida.write(f"{nuevo_prefijo_para_sub}📄 CONTENIDO DEL ARCHIVO ({nombre_item}):\n")
                            # MODIFICACIÓN: Iterar sobre todas las líneas del archivo
                            for linea_de_contenido in lineas_contenido:
                                archivo_salida.write(f"{nuevo_prefijo_para_sub}  {linea_de_contenido}\n")
                            # MODIFICACIÓN: Fin del contenido siempre se muestra después de todas las líneas
                            archivo_salida.write(f"{nuevo_prefijo_para_sub}--- FIN CONTENIDO ({nombre_item}) ---\n")
                        else:
                            archivo_salida.write(f"{nuevo_prefijo_para_sub}📄 (Archivo vacío)\n")
                except Exception as e:
                    archivo_salida.write(f"{nuevo_prefijo_para_sub}📄 (No se pudo leer el contenido: {e})\n")
        
        # Añadir una línea en blanco después de cada elemento principal (carpeta o archivo con/sin contenido)
        # para mejorar la legibilidad, excepto si es el último elemento de una carpeta muy anidada.
        # Esto es opcional y se puede ajustar.
        if prefijo.count('│') < 3 : # Menos separación en niveles muy profundos
             archivo_salida.write("\n")


if __name__ == "__main__":
    # Obtiene el directorio donde se está ejecutando el script
    directorio_proyecto = os.getcwd() 
    nombre_archivo_salida = "z.txt"

    # Abrimos el archivo z.txt en modo escritura ('w')
    # Usamos 'with' para asegurar que el archivo se cierre automáticamente
    try:
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as archivo_z:
            archivo_z.write(f"Listado del proyecto en: {directorio_proyecto}\n")
            archivo_z.write(f"Generado el: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n") # Fecha y hora de generación
            archivo_z.write("============================================\n\n")
            
            # Llamamos a la función principal, pasándole el objeto archivo abierto
            listar_directorio_completo(directorio_proyecto, archivo_z)
            
            archivo_z.write("\n============================================\n")
            archivo_z.write("Fin del listado.\n")
        
        print(f"El listado del proyecto se ha guardado en {os.path.join(directorio_proyecto, nombre_archivo_salida)}")
    except Exception as e:
        print(f"Error al generar el archivo de listado: {e}")