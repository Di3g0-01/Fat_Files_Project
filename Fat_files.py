import json
import os
import datetime
from typing import Dict, List, Optional

# Directorio base para el sistema de archivos simulado
FS_DIR = "filesystem"
FAT_FILE = os.path.join(FS_DIR, "fat_table.json")
BLOCK_PREFIX = "block_"

# Crear directorio si no existe
os.makedirs(FS_DIR, exist_ok=True)

# Función para cargar la tabla FAT
def load_fat() -> Dict:
    if os.path.exists(FAT_FILE):
        with open(FAT_FILE, 'r') as f:
            return json.load(f)
    return {"files": {}}

# Función para guardar la tabla FAT
def save_fat(fat: Dict):
    with open(FAT_FILE, 'w') as f:
        json.dump(fat, f, indent=4)

# Función para crear un bloque de datos
def create_block(data: str, block_id: str) -> str:
    block_file = os.path.join(FS_DIR, f"{BLOCK_PREFIX}{block_id}.json")
    block = {
        "datos": data,
        "siguiente": None,
        "eof": True
    }
    with open(block_file, 'w') as f:
        json.dump(block, f, indent=4)
    return block_file

# Función para enlazar bloques (crear cadena)
def create_blocks(content: str, file_name: str, start_index: int = 0) -> List[str]:
    blocks = []
    i = 0
    block_id = f"{file_name}_{start_index}"
    while i < len(content):
        chunk = content[i:i+20]
        prev_block = None if not blocks else blocks[-1]
        block_file = create_block(chunk, block_id)
        
        # Enlazar al siguiente si no es el último
        if i + 20 < len(content):
            block_data = {"datos": chunk, "siguiente": f"{BLOCK_PREFIX}{block_id}_next.json", "eof": False}
            with open(block_file, 'w') as f:
                json.dump(block_data, f, indent=4)
            block_id = f"{file_name}_{start_index + len(blocks) + 1}"
        else:
            block_data = {"datos": chunk, "siguiente": None, "eof": True}
            with open(block_file, 'w') as f:
                json.dump(block_data, f, indent=4)
        
        blocks.append(block_file)
        i += 20
    return blocks

# Función para eliminar bloques físicos
def delete_blocks(first_block: str):
    current = first_block
    while current:
        if os.path.exists(current):
            with open(current, 'r') as f:
                block = json.load(f)
            os.remove(current)
            current = block.get("siguiente")
        else:
            break

# Función para leer contenido concatenado de bloques
def read_file_content(first_block: str) -> str:
    content = ""
    current = first_block
    while current:
        if os.path.exists(current):
            with open(current, 'r') as f:
                block = json.load(f)
            content += block["datos"]
            if block["eof"]:
                break
            current = block["siguiente"]
        else:
            break
    return content

# Función para verificar permisos
def has_permission(fat_entry: Dict, current_user: str, action: str) -> bool:
    if fat_entry["owner"] == current_user:
        return True
    perms = fat_entry.get("permissions", {})
    user_perms = perms.get(current_user, [])
    if action == "read" and "lectura" in user_perms:
        return True
    if action == "write" and "escritura" in user_perms:
        return True
    return False

# Función para asignar/revocar permisos (solo owner)
def manage_permissions(fat_entry: Dict, current_user: str, target_user: str, perm_type: str, add: bool):
    if fat_entry["owner"] != current_user:
        print("Error: Solo el owner puede gestionar permisos.")
        return
    perms = fat_entry.setdefault("permissions", {})
    user_perms = perms.setdefault(target_user, [])
    if add:
        if perm_type not in user_perms:
            user_perms.append(perm_type)
    else:
        if perm_type in user_perms:
            user_perms.remove(perm_type)
    print(f"Permiso {perm_type} {'agregado' if add else 'revocado'} para {target_user}.")

# Operación: Crear archivo
def create_file(current_user: str):
    name = input("Nombre del archivo: ").strip()
    fat = load_fat()
    if name in fat["files"]:
        print("Error: Archivo ya existe.")
        return
    
    content = input("Contenido del archivo: ").strip()
    if not content:
        print("Error: Contenido vacío.")
        return
    
    now = datetime.datetime.now().isoformat()
    first_block = None
    blocks = create_blocks(content, name)
    if blocks:
        first_block = blocks[0]
    
    entry = {
        "nombre": name,
        "ruta_datos_inicial": first_block,
        "papelera": False,
        "total_caracteres": len(content),
        "fecha_creacion": now,
        "fecha_modificacion": now,
        "fecha_eliminacion": None,
        "owner": current_user,
        "permissions": {}
    }
    fat["files"][name] = entry
    save_fat(fat)
    print(f"Archivo '{name}' creado exitosamente.")

# Operación: Listar archivos (no eliminados)
def list_files():
    fat = load_fat()
    print("\nArchivos disponibles:")
    for name, entry in fat["files"].items():
        if not entry["papelera"]:
            print(f"- {name} (Owner: {entry['owner']}, Size: {entry['total_caracteres']})")

# Operación: Mostrar papelera
def list_trash():
    fat = load_fat()
    print("\nArchivos en papelera:")
    for name, entry in fat["files"].items():
        if entry["papelera"]:
            print(f"- {name} (Eliminado: {entry.get('fecha_eliminacion', 'N/A')})")

# Operación: Abrir archivo
def open_file(current_user: str):
    name = input("Nombre del archivo: ").strip()
    fat = load_fat()
    if name not in fat["files"]:
        print("Error: Archivo no existe.")
        return
    
    entry = fat["files"][name]
    if entry["papelera"]:
        print("Error: Archivo en papelera.")
        return
    
    if not has_permission(entry, current_user, "read"):
        print("Error: Sin permisos de lectura.")
        return
    
    # Mostrar metadatos
    print(f"\nMetadatos de '{name}':")
    print(f"Owner: {entry['owner']}")
    print(f"Fecha creación: {entry['fecha_creacion']}")
    print(f"Fecha modificación: {entry['fecha_modificacion']}")
    print(f"Tamaño: {entry['total_caracteres']} caracteres")
    perms = entry.get("permissions", {})
    print(f"Permisos: {perms}")
    
    # Contenido
    content = read_file_content(entry["ruta_datos_inicial"])
    print(f"\nContenido:\n{content}")

# Operación: Modificar archivo
def modify_file(current_user: str):
    name = input("Nombre del archivo: ").strip()
    fat = load_fat()
    if name not in fat["files"]:
        print("Error: Archivo no existe.")
        return
    
    entry = fat["files"][name]
    if entry["papelera"]:
        print("Error: Archivo en papelera.")
        return
    
    if not has_permission(entry, current_user, "write"):
        print("Error: Sin permisos de escritura.")
        return
    
    # Mostrar contenido actual
    current_content = read_file_content(entry["ruta_datos_inicial"])
    print(f"\nContenido actual:\n{current_content}")
    
    new_content = input("Nuevo contenido: ").strip()
    if not new_content:
        print("Error: Contenido vacío.")
        return
    
    # Eliminar bloques viejos
    if entry["ruta_datos_inicial"]:
        delete_blocks(entry["ruta_datos_inicial"])
    
    # Crear nuevos bloques
    blocks = create_blocks(new_content, name, 0)  # Reiniciar índice
    first_block = blocks[0] if blocks else None
    
    # Actualizar FAT
    now = datetime.datetime.now().isoformat()
    entry["ruta_datos_inicial"] = first_block
    entry["total_caracteres"] = len(new_content)
    entry["fecha_modificacion"] = now
    save_fat(fat)
    print(f"Archivo '{name}' modificado exitosamente.")

# Operación: Eliminar archivo (a papelera)
def delete_file(current_user: str):
    name = input("Nombre del archivo: ").strip()
    fat = load_fat()
    if name not in fat["files"]:
        print("Error: Archivo no existe.")
        return
    
    entry = fat["files"][name]
    if entry["papelera"]:
        print("Error: Ya está en papelera.")
        return
    
    # Verificar permiso (asumir que cualquiera puede eliminar si tiene read, o solo owner para simplicidad)
    if not has_permission(entry, current_user, "read"):  # Simplificado: read implica delete
        print("Error: Sin permisos.")
        return
    
    now = datetime.datetime.now().isoformat()
    entry["papelera"] = True
    entry["fecha_eliminacion"] = now
    save_fat(fat)
    print(f"Archivo '{name}' movido a papelera.")

# Operación: Recuperar archivo
def recover_file(current_user: str):
    name = input("Nombre del archivo: ").strip()
    fat = load_fat()
    if name not in fat["files"]:
        print("Error: Archivo no existe.")
        return
    
    entry = fat["files"][name]
    if not entry["papelera"]:
        print("Error: No está en papelera.")
        return
    
    # Solo owner puede recuperar
    if entry["owner"] != current_user:
        print("Error: Solo el owner puede recuperar.")
        return
    
    entry["papelera"] = False
    entry["fecha_eliminacion"] = None
    save_fat(fat)
    print(f"Archivo '{name}' recuperado.")

# Operación: Gestionar permisos
def manage_perms(current_user: str):
    name = input("Nombre del archivo: ").strip()
    fat = load_fat()
    if name not in fat["files"]:
        print("Error: Archivo no existe.")
        return
    
    entry = fat["files"][name]
    if entry["papelera"]:
        print("Error: Archivo en papelera.")
        return
    
    if entry["owner"] != current_user:
        print("Error: Solo el owner puede gestionar permisos.")
        return
    
    target_user = input("Usuario objetivo: ").strip()
    perm_type = input("Tipo de permiso (lectura/escritura): ").strip().lower()
    action = input("Acción (agregar/revocar): ").strip().lower()
    
    if perm_type not in ["lectura", "escritura"]:
        print("Error: Permiso inválido.")
        return
    
    add = action == "agregar"
    manage_permissions(entry, current_user, target_user, perm_type, add)
    save_fat(fat)

# Menú principal
def main():
    current_user = input("Ingrese su usuario (owner inicial: admin): ").strip()
    if not current_user:
        current_user = "admin"
    
    while True:
        print("\n=== Simulador de Sistema de Archivos FAT ===")
        print("1. Crear archivo")
        print("2. Listar archivos")
        print("3. Mostrar papelera")
        print("4. Abrir archivo")
        print("5. Modificar archivo")
        print("6. Eliminar archivo")
        print("7. Recuperar archivo")
        print("8. Gestionar permisos")
        print("0. Salir")
        
        choice = input("Seleccione opción: ").strip()
        
        if choice == "1":
            create_file(current_user)
        elif choice == "2":
            list_files()
        elif choice == "3":
            list_trash()
        elif choice == "4":
            open_file(current_user)
        elif choice == "5":
            modify_file(current_user)
        elif choice == "6":
            delete_file(current_user)
        elif choice == "7":
            recover_file(current_user)
        elif choice == "8":
            manage_perms(current_user)
        elif choice == "0":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
