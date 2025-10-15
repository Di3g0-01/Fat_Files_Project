import json
import os
import datetime
from typing import Dict, List, Optional

FS_DIR = "filesystem"
FAT_FILE = os.path.join(FS_DIR, "fat_table.json")
USERS_FILE = os.path.join(FS_DIR, "users.json") 
BLOCK_PREFIX = "block_"
BLOCK_SIZE = 20 

os.makedirs(FS_DIR, exist_ok=True)

def load_fat() -> Dict:
    if os.path.exists(FAT_FILE):
        with open(FAT_FILE, 'r') as f:
            return json.load(f)
    return {"files": {}}

def save_fat(fat: Dict):
    with open(FAT_FILE, 'w') as f:
        json.dump(fat, f, indent=4)

def load_users() -> Dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users: Dict):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

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

def create_blocks(content: str, file_name: str, start_index: int = 0) -> List[str]:
    blocks = []
    i = 0
    while i < len(content):
        chunk = content[i:i + BLOCK_SIZE]
        block_num = start_index + len(blocks)
        block_id = f"{file_name}_{block_num}"
        block_file = os.path.join(FS_DIR, f"{BLOCK_PREFIX}{block_id}.json")
        is_eof = (i + BLOCK_SIZE >= len(content))
        
        next_block_path = None
        if not is_eof:
            next_block_id = f"{file_name}_{block_num + 1}"
            next_block_path = os.path.join(FS_DIR, f"{BLOCK_PREFIX}{next_block_id}.json")

        block_data = {
            "datos": chunk,
            "siguiente": next_block_path,
            "eof": is_eof
        }
        
        with open(block_file, 'w') as f:
            json.dump(block_data, f, indent=4)
        
        blocks.append(block_file)
        i += BLOCK_SIZE
        
    return blocks

def delete_blocks(first_block_path: str):
    current = first_block_path
    while current:
        if os.path.exists(current):
            try:
                with open(current, 'r') as f:
                    block = json.load(f)
                next_block = block.get("siguiente")
                os.remove(current)
                current = next_block
            except Exception:
                break
        else:
            break

def read_file_content(first_block_path: str) -> str:
    content = ""
    current = first_block_path
    while current:
        if os.path.exists(current):
            try:
                with open(current, 'r') as f:
                    block = json.load(f)
                content += block["datos"]
                if block["eof"]:
                    break
                current = block.get("siguiente")
            except Exception:
                break
        else:
            break
    return content

def has_permission(fat_entry: Dict, current_user: str, action: str) -> bool:
    if fat_entry["owner"] == current_user:
        return True
    if action == "admin" and current_user == "admin":
        return True
        
    perms = fat_entry.get("permissions", {})
    user_perms = perms.get(current_user, [])
    if action == "read" and "lectura" in user_perms:
        return True
    if action == "write" and "escritura" in user_perms:
        return True
    return False

class FileSystemController:
    def __init__(self):
        self.fat = self.load_fat()
        self.users = self.load_users()
        self.current_user = None
        self.user_role = None

    def load_fat(self) -> Dict:
        return load_fat()
    
    def save_fat(self, fat: Dict):
        save_fat(fat)

    def load_users(self) -> Dict:
        return load_users()

    def save_users(self, users: Dict):
        save_users(users)

    def save_all(self):
        self.save_fat(self.fat)
        self.save_users(self.users)
        
    def is_admin(self) -> bool:
        return self.user_role == "admin"

    def get_admin_status(self) -> bool:
        return any(u.get("role") == "admin" for u in self.users.values())

    def register_admin(self, username, password) -> bool:
        if self.get_admin_status() or username in self.users:
            return False
        self.users[username] = {"password": password, "role": "admin"}
        self.save_all()
        return True

    def authenticate(self, username, password) -> bool:
        user_data = self.users.get(username)
        if user_data and user_data["password"] == password:
            self.current_user = username
            self.user_role = user_data["role"]
            return True
        return False

    def add_user(self, username, password, role) -> str:
        if not self.is_admin(): return "Error: Solo el admin puede agregar usuarios."
        if username in self.users: return "Error: El usuario ya existe."
        if not username or not password: return "Error: Usuario y contraseña no pueden estar vacíos."
        
        self.users[username] = {"password": password, "role": role}
        self.save_all()
        return f"Éxito: Usuario '{username}' creado como {role}."
        
    def has_read_permission_logic(self, fat_entry: Dict) -> bool:
        # Lógica para la GUI: si es admin, dueño o tiene permiso de lectura
        return self.is_admin() or has_permission(fat_entry, self.current_user, "read")
    
    def has_write_permission_logic(self, fat_entry: Dict) -> bool:
        # Lógica para la GUI: si es admin, dueño o tiene permiso de escritura
        return self.is_admin() or has_permission(fat_entry, self.current_user, "write")

    def create_file(self, name: str, content: str) -> str:
        # Permiso de creación: Solo Admin o User
        if not self.current_user: return "Error: Debe estar logueado."
        
        if not name or not content: return "Error: Nombre y contenido no pueden estar vacíos."
        if name in self.fat["files"] and not self.fat["files"][name]["papelera"]: 
            return "Error: Archivo ya existe."
        
        now = datetime.datetime.now().isoformat()
        blocks = create_blocks(content, name)
        first_block = blocks[0] if blocks else None
        
        entry = {
            "nombre": name,
            "ruta_datos_inicial": first_block,
            "papelera": False,
            "total_caracteres": len(content),
            "fecha_creacion": now,
            "fecha_modificacion": now,
            "fecha_eliminacion": None,
            "owner": self.current_user,
            "permissions": {}
        }
        self.fat["files"][name] = entry
        self.save_all()
        return f"Éxito: Archivo '{name}' creado exitosamente."

    def get_list_files(self, is_trash=False) -> List[Dict]:
        self.fat = self.load_fat()
        return [
            {"name": name, **entry} 
            for name, entry in self.fat["files"].items() 
            if entry["papelera"] == is_trash
        ]

    def open_file(self, name: str) -> Dict:
        if name not in self.fat["files"]: 
            return {"error": "Archivo no existe."}
        entry = self.fat["files"][name]
        if entry["papelera"]: 
            return {"error": "Archivo en papelera."}
        
        # VALIDACIÓN DE PERMISO DE LECTURA
        if not self.is_admin() and not has_permission(entry, self.current_user, "read"): 
            return {"error": "Sin permisos de lectura."}
        
        content = read_file_content(entry["ruta_datos_inicial"])
        return {"entry": entry, "content": content}

    def modify_file(self, name: str, new_content: str) -> str:
        if not name or not new_content: return "Error: Nombre y contenido no pueden estar vacíos."
        if name not in self.fat["files"]: return "Error: Archivo no existe."
        
        entry = self.fat["files"][name]
        if entry["papelera"]: return "Error: Archivo en papelera."
        
        # VALIDACIÓN DE PERMISO DE ESCRITURA
        if not self.is_admin() and not has_permission(entry, self.current_user, "write"): return "Error: Sin permisos de escritura."
        
        if entry["ruta_datos_inicial"]: delete_blocks(entry["ruta_datos_inicial"])
        blocks = create_blocks(new_content, name, 0)
        first_block = blocks[0] if blocks else None
        
        now = datetime.datetime.now().isoformat()
        entry["ruta_datos_inicial"] = first_block
        entry["total_caracteres"] = len(new_content)
        entry["fecha_modificacion"] = now
        self.save_all()
        return f"Éxito: Archivo '{name}' modificado exitosamente."

    def delete_file(self, name: str) -> str:
        if name not in self.fat["files"]: return "Error: Archivo no existe."
        entry = self.fat["files"][name]
        if entry["papelera"]: return "Error: Ya está en papelera."
        
        # VALIDACIÓN DE OWNER / ADMIN para eliminar
        if not self.is_admin() and entry["owner"] != self.current_user: return "Error: Solo el owner o admin puede eliminar."
        
        now = datetime.datetime.now().isoformat()
        entry["papelera"] = True
        entry["fecha_eliminacion"] = now
        self.save_all()
        return f"Éxito: Archivo '{name}' movido a papelera."

    def recover_file(self, name: str) -> str:
        if name not in self.fat["files"]: return "Error: Archivo no existe."
        entry = self.fat["files"][name]
        if not entry["papelera"]: return "Error: No está en papelera."
        
        # VALIDACIÓN DE OWNER / ADMIN para recuperar
        if not self.is_admin() and entry["owner"] != self.current_user: return "Error: Solo el owner o admin puede recuperar."
        
        entry["papelera"] = False
        entry["fecha_eliminacion"] = None
        self.save_all()
        return f"Éxito: Archivo '{name}' recuperado."
    
    def manage_permissions(self, name: str, target_user: str, perm_type: str, add: bool) -> str:
        if name not in self.fat["files"]: return "Error: Archivo no existe."
        entry = self.fat["files"][name]
        
        # VALIDACIÓN DE OWNER / ADMIN para gestionar permisos
        if not self.is_admin() and entry["owner"] != self.current_user: return "Error: Solo el owner o admin puede gestionar permisos."
        
        if entry["papelera"]: return "Error: Archivo en papelera."
        if target_user not in self.users: return "Error: Usuario objetivo no existe."
        if perm_type not in ["lectura", "escritura"]: return "Error: Tipo de permiso inválido."

        perms = entry.setdefault("permissions", {})
        user_perms = perms.setdefault(target_user, [])
        
        if add:
            if perm_type not in user_perms:
                user_perms.append(perm_type)
                message = f"Permiso {perm_type} agregado para {target_user}."
            else:
                message = f"Permiso {perm_type} ya existía para {target_user}."
        else:
            if perm_type in user_perms:
                user_perms.remove(perm_type)
                message = f"Permiso {perm_type} revocado para {target_user}."
            else:
                message = f"Permiso {perm_type} no existía para {target_user}."

        self.save_all()
        return f"Éxito: {message}"