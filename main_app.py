import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QLineEdit, QListWidget
from PyQt5.QtCore import Qt
from main_logic import FileSystemController 
from ui_widgets import AuthWindow, MainWindow 

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.controller = FileSystemController()
        self.auth_window = None
        self.main_window = None

    def start_auth(self):
        self.auth_window = AuthWindow(self.controller)
        
        self.auth_window.btn_create_admin.clicked.connect(self._handle_create_admin)
        self.auth_window.btn_login.clicked.connect(self._handle_login)
        self.auth_window.login_pass_input.returnPressed.connect(self._handle_login) 
        
        self.auth_window.show()
        sys.exit(self.app.exec_())

    def _handle_create_admin(self):
        username = self.auth_window.setup_user_input.text().strip()
        password = self.auth_window.setup_pass_input.text()
        
        if self.controller.register_admin(username, password):
            QMessageBox.information(self.auth_window, "Éxito", "Admin creado. Por favor, inicie sesión.")
            self.auth_window.setup_user_input.clear()
            self.auth_window.setup_pass_input.clear()
            self.auth_window.stacked_widget.setCurrentWidget(self.auth_window.login_page)
        else:
            QMessageBox.critical(self.auth_window, "Error", "Error al crear admin. El usuario podría ya existir o los campos están vacíos.")

    def _handle_login(self):
        username = self.auth_window.login_user_input.text().strip()
        password = self.auth_window.login_pass_input.text()
        
        if self.controller.authenticate(username, password):
            self.auth_window.hide()
            self._start_main_app()
        else:
            QMessageBox.critical(self.auth_window, "Error de Login", "Usuario o contraseña incorrectos.")

    def _start_main_app(self):
        self.main_window = MainWindow(self.controller)
        
        self.main_window.btn_logout.clicked.connect(self._handle_logout)
        
        self.main_window.stacked_content.currentChanged.connect(self._setup_current_page_connections)
        
        self._setup_current_page_connections(self.main_window.current_page_index)
        
        self.main_window.show()

    def _setup_current_page_connections(self, index):
        
        try: self.main_window.btn_create.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_open.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_load_content.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_modify.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_delete.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_recover.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_add_user.clicked.disconnect()
        except (TypeError, RuntimeError): pass
        try: self.main_window.btn_apply_perm.clicked.disconnect()
        except (TypeError, RuntimeError): pass

        current_block = self.main_window.stacked_content.widget(index)
        
        # 1. Crear Archivo
        if current_block.findChild(QLineEdit, 'create_name_input'): 
            self.main_window.btn_create.clicked.connect(self._handle_create_file)
        
        # 2. Abrir Archivo
        elif current_block.findChild(QLineEdit, 'open_name_input'):
            self.main_window.btn_open.clicked.connect(self._handle_open_file)
        
        # 3. Modificar Archivo
        elif current_block.findChild(QLineEdit, 'modify_name_input'):
            self.main_window.btn_load_content.clicked.connect(self._handle_load_content_for_modify)
            self.main_window.btn_modify.clicked.connect(self._handle_modify_file)

        # 4. Mover a Papelera
        elif current_block.findChild(QLineEdit, 'delete_name_input'):
            self.main_window.btn_delete.clicked.connect(self._handle_delete_file)

        # 5. Recuperar Archivo
        elif current_block.findChild(QLineEdit, 'recover_name_input'):
            self.main_window.btn_recover.clicked.connect(self._handle_recover_file)

        # 6. Gestión de Usuarios
        elif current_block.findChild(QListWidget, 'user_list'):
            self._refresh_user_list()
            self.main_window.btn_add_user.clicked.connect(self._handle_add_user)
            
        # 7. Gestión de Permisos
        elif current_block.findChild(QLineEdit, 'perm_file_input'):
            self.main_window.btn_apply_perm.clicked.connect(self._handle_manage_perms)
            
    def _handle_logout(self):
        self.controller.save_all()
        self.main_window.close()
        self.controller.current_user = None
        self.controller.user_role = None
        # Vuelve a iniciar la autenticación en el mismo proceso
        self.start_auth()

    def _handle_create_file(self):
        name = self.main_window.create_name_input.text().strip()
        content = self.main_window.create_content_input.toPlainText().strip()
        result = self.controller.create_file(name, content)
        
        if result.startswith("Éxito"):
            QMessageBox.information(self.main_window, "Creación Exitosa", result)
            self.main_window.create_name_input.clear()
            self.main_window.create_content_input.clear()
            self.main_window.show_list_files() 
        else:
            QMessageBox.critical(self.main_window, "Error al Crear", result)

    def _handle_open_file(self):
        name = self.main_window.open_name_input.text().strip()
        result = self.controller.open_file(name)
        self.main_window.open_output.clear()

        if "error" in result:
            self.main_window.open_output.setText(f"Error: {result['error']}")
            QMessageBox.critical(self.main_window, "Error de Apertura", result['error'])
        else:
            entry = result['entry']
            content = result['content']
            metadata = (
                f"Metadatos de '{name}':\n"
                f"Owner: {entry['owner']}\n"
                f"Fecha creación: {entry['fecha_creacion']}\n"
                f"Fecha modificación: {entry['fecha_modificacion']}\n"
                f"Tamaño: {entry['total_caracteres']} caracteres\n"
                f"Permisos: {entry.get('permissions', {})}\n\n"
                f"Contenido:\n"
            )
            self.main_window.open_output.setText(metadata + content)

    def _handle_load_content_for_modify(self):
        name = self.main_window.modify_name_input.text().strip()
        
        if name not in self.controller.fat['files']:
             QMessageBox.critical(self.main_window, "Error de Carga", "El archivo no existe.")
             return

        entry = self.controller.fat['files'][name]
        
        # ⚠️ Verificación de permisos para cargar contenido (necesita permiso de escritura)
        if not self.controller.has_write_permission_logic(entry):
             QMessageBox.critical(self.main_window, "Error de Permisos", "No tienes permisos de escritura para cargar/modificar este archivo.")
             self.main_window.modify_content_input.clear()
             return

        result = self.controller.open_file(name)
        self.main_window.modify_content_input.clear()

        if "error" in result:
            QMessageBox.critical(self.main_window, "Error de Carga", result['error'])
        else:
            self.main_window.modify_content_input.setText(result['content'])


    def _handle_modify_file(self):
        name = self.main_window.modify_name_input.text().strip()
        new_content = self.main_window.modify_content_input.toPlainText().strip()
        result = self.controller.modify_file(name, new_content)

        if result.startswith("Éxito"):
            QMessageBox.information(self.main_window, "Modificación Exitosa", result)
            self.main_window.show_list_files()
        else:
            QMessageBox.critical(self.main_window, "Error al Modificar", result)

    def _handle_delete_file(self):
        name = self.main_window.delete_name_input.text().strip()
        result = self.controller.delete_file(name)

        if result.startswith("Éxito"):
            QMessageBox.information(self.main_window, "Eliminación Exitosa", result)
            self.main_window.delete_name_input.clear()
            self.main_window.show_list_files()
        else:
            QMessageBox.critical(self.main_window, "Error al Eliminar", result)

    def _handle_recover_file(self):
        name = self.main_window.recover_name_input.text().strip()
        result = self.controller.recover_file(name)

        if result.startswith("Éxito"):
            QMessageBox.information(self.main_window, "Recuperación Exitosa", result)
            self.main_window.recover_name_input.clear()
            self.main_window.show_list_trash()
        else:
            QMessageBox.critical(self.main_window, "Error al Recuperar", result)
            
    def _handle_add_user(self):
        username = self.main_window.add_user_input.text().strip()
        password = self.main_window.add_pass_input.text()
        role = self.main_window.add_role_combo.currentText()
        result = self.controller.add_user(username, password, role)
        
        if result.startswith("Éxito"):
            QMessageBox.information(self.main_window, "Usuario Agregado", result)
            self.main_window.add_user_input.clear()
            self.main_window.add_pass_input.clear()
            self._refresh_user_list()
        else:
            QMessageBox.critical(self.main_window, "Error de Usuario", result)

    def _handle_manage_perms(self):
        name = self.main_window.perm_file_input.text().strip()
        target_user = self.main_window.perm_target_user_input.text().strip()
        perm_type = self.main_window.perm_type_combo.currentText()
        add = self.main_window.perm_action_combo.currentText() == "agregar"
        
        result = self.controller.manage_permissions(name, target_user, perm_type, add)
        
        if result.startswith("Éxito"):
            QMessageBox.information(self.main_window, "Permiso Aplicado", result)
        else:
            QMessageBox.critical(self.main_window, "Error de Permiso", result)
            
    def _refresh_user_list(self):
        self.main_window.user_list.clear()
        
        # Solo Admin debe ver la gestión de usuarios, pero si no se refresca, 
        # el listado podría estar vacío si entra un admin y luego un user.
        if self.controller.is_admin():
            for user, data in self.controller.users.items():
                self.main_window.user_list.addItem(f"{user} (Rol: {data['role']})")
    
if __name__ == "__main__":
    MainApplication().start_auth()