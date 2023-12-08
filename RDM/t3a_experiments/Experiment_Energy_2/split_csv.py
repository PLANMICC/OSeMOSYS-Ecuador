import os
import pandas as pd

def split_csv(file_path, max_size_mb=2048):  # 2048 MB = 2 GB
    # Establecer el tamaño máximo del archivo en bytes
    max_size = max_size_mb * 1024 * 1024

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        print(f"El archivo {file_path} no existe.")
        return

    # Obtener y mostrar el tamaño del archivo
    file_size = os.path.getsize(file_path)
    print(f"Tamaño del archivo {file_path}: {file_size / 1024 / 1024:.2f} MB")

    # Inicializar el contador de partes y el tamaño acumulado
    part_num = 1
    accumulated_size = 0
    header_saved = False

    # Nombre base para los archivos divididos
    base_name = os.path.splitext(file_path)[0]

    # Crear un dataframe vacío para guardar la cabecera
    header_df = pd.DataFrame()

    # Leer el archivo grande en trozos
    for chunk in pd.read_csv(file_path, chunksize=100000):  # Ajustar el chunksize según sea necesario
        # Si aún no se ha guardado la cabecera, guardarla en un dataframe aparte
        if not header_saved:
            header_df = pd.DataFrame(columns=chunk.columns)
            header_saved = True

        # Tamaño del chunk actual
        chunk_size = chunk.memory_usage(index=True, deep=True).sum()

        # Si el tamaño acumulado más el del chunk actual excede el máximo, resetear
        if accumulated_size + chunk_size > max_size:
            part_num += 1
            accumulated_size = 0

        # Nombre del archivo dividido
        output_file = f"{base_name}_part{part_num}.csv"

        # Guardar el chunk actual
        if accumulated_size == 0:
            # Escribir la cabecera si es el primer chunk de un archivo nuevo
            header_df.to_csv(output_file, index=False)
        chunk.to_csv(output_file, mode='a', header=False, index=False)

        # Actualizar el tamaño acumulado
        accumulated_size += chunk_size

        print(f"Parte {part_num}, tamaño acumulado: {accumulated_size / 1024 / 1024:.2f} MB")

    print(f"División completada. {part_num} partes creadas.")

# Rutas de los archivos
file_paths = [
    r"C:\Users\ucr\Dropbox\4_Proyectos\1_Consultoria\PLANMICC2050_compartido_con_equipo\Producto_7\GitHub\RDM\t3a_experiments\Experiment_Energy_2\OSEMOSYS_ECU_Energy_Output.csv",
    r"C:\Users\ucr\Dropbox\4_Proyectos\1_Consultoria\PLANMICC2050_compartido_con_equipo\Producto_7\GitHub\RDM\t3a_experiments\Experiment_Energy_2\OSEMOSYS_ECU_Energy_Input.csv"
]

for file_path in file_paths:
    split_csv(file_path)
