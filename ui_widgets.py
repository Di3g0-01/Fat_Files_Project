from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, 
    QListWidget, QTextEdit, QComboBox, QFrame, QGridLayout, QListWidgetItem,
    QDesktopWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

COLOR_MAIN_BG = "#1e1e1e"  
COLOR_PANEL_BG = "#2f2f2f" 
COLOR_TEXT = "#ffffff"     
COLOR_HIGHLIGHT = "#3a3a3a"
COLOR_BORDER = "#505050"   

class ContentBlock(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("ContentBlock")
        self.setStyleSheet(f"""
            #ContentBlock {{
                background-color: {COLOR_PANEL_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 5px;
            }}
            QLabel {{
                color: {COLOR_TEXT};
                font-size: 16px;
                font-weight: bold;
                background-color: transparent;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        self.title_label = QLabel(title)
        self.layout.addWidget(self.title_label)
        
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background-color: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addWidget(self.content_frame)

class AuthWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Autenticación del Sistema FAT")
        self.setGeometry(100, 100, 400, 250)
        self.setStyleSheet(f"background-color: {COLOR_MAIN_BG}; color: {COLOR_TEXT};")
        
        self.main_layout = QVBoxLayout(self)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self._init_setup_admin_ui()
        self._init_login_ui()
        
        if not self.controller.get_admin_status():
            self.stacked_widget.setCurrentWidget(self.setup_admin_page)
        else:
            self.stacked_widget.setCurrentWidget(self.login_page)
            
        self.center_window() # Centrado

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _init_setup_admin_ui(self):
        self.setup_admin_page = QWidget()
        layout = QGridLayout(self.setup_admin_page)
        
        label = QLabel("CREAR ADMIN INICIAL")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label, 0, 0, 1, 2, Qt.AlignCenter)
        
        layout.addWidget(QLabel("Usuario:"), 1, 0)
        self.setup_user_input = QLineEdit()
        self.setup_user_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.setup_user_input, 1, 1)
        
        layout.addWidget(QLabel("Contraseña:"), 2, 0)
        self.setup_pass_input = QLineEdit()
        self.setup_pass_input.setEchoMode(QLineEdit.Password)
        self.setup_pass_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.setup_pass_input, 2, 1)
        
        self.btn_create_admin = QPushButton("Crear Admin")
        self.btn_create_admin.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_create_admin, 3, 0, 1, 2)
        
        self.stacked_widget.addWidget(self.setup_admin_page)

    def _init_login_ui(self):
        self.login_page = QWidget()
        layout = QGridLayout(self.login_page)
        
        label = QLabel("INICIAR SESIÓN")
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label, 0, 0, 1, 2, Qt.AlignCenter)
        
        layout.addWidget(QLabel("Usuario:"), 1, 0)
        self.login_user_input = QLineEdit()
        self.login_user_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.login_user_input, 1, 1)
        
        layout.addWidget(QLabel("Contraseña:"), 2, 0)
        self.login_pass_input = QLineEdit()
        self.login_pass_input.setEchoMode(QLineEdit.Password)
        self.login_pass_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.login_pass_input, 2, 1)
        
        self.btn_login = QPushButton("Entrar")
        self.btn_login.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_login, 3, 0, 1, 2)
        
        self.stacked_widget.addWidget(self.login_page)

class MainWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle(f"Simulador FAT - Usuario: {controller.current_user} ({controller.user_role})")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(f"background-color: {COLOR_MAIN_BG}; color: {COLOR_TEXT};")
        
        self.create_name_input = QLineEdit()
        self.create_name_input.setObjectName('create_name_input')
        self.create_content_input = QTextEdit()
        self.btn_create = QPushButton()
        
        self.open_name_input = QLineEdit()
        self.open_name_input.setObjectName('open_name_input')
        self.open_output = QTextEdit()
        self.btn_open = QPushButton()
        
        self.modify_name_input = QLineEdit()
        self.modify_name_input.setObjectName('modify_name_input')
        self.modify_content_input = QTextEdit()
        self.btn_load_content = QPushButton()
        self.btn_modify = QPushButton()
        
        self.delete_name_input = QLineEdit()
        self.delete_name_input.setObjectName('delete_name_input')
        self.btn_delete = QPushButton()
        
        self.recover_name_input = QLineEdit()
        self.recover_name_input.setObjectName('recover_name_input')
        self.btn_recover = QPushButton()
        
        self.user_list = QListWidget()
        self.user_list.setObjectName('user_list')
        self.add_user_input = QLineEdit()
        self.add_pass_input = QLineEdit()
        self.add_role_combo = QComboBox()
        self.btn_add_user = QPushButton()
        
        self.perm_file_input = QLineEdit()
        self.perm_file_input.setObjectName('perm_file_input')
        self.perm_target_user_input = QLineEdit()
        self.perm_type_combo = QComboBox()
        self.perm_action_combo = QComboBox()
        self.btn_apply_perm = QPushButton()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self._init_side_menu()
        self._init_content_area()
        
        self.show_list_files()
        
        self.center_window() # Centrado

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _init_side_menu(self):
        self.side_menu = QFrame()
        self.side_menu.setFixedWidth(250)
        self.side_menu.setStyleSheet(f"background-color: {COLOR_PANEL_BG}; border-radius: 5px;")
        
        menu_layout = QVBoxLayout(self.side_menu)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        menu_layout.setAlignment(Qt.AlignTop)

        title_label = QLabel("Sistema de Archivos FAT")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(title_label)
        menu_layout.addSpacing(10)

        self.btn_file_ops = self._create_menu_block("Operaciones de Archivo")
        menu_layout.addWidget(self.btn_file_ops)
        self.file_ops_layout = self.btn_file_ops.content_layout 
        
        self.create_btn = self._add_menu_button("Crear Archivo 💾", self.show_create_file, self.file_ops_layout)
        self._add_menu_button("Listar Archivos 📄", self.show_list_files, self.file_ops_layout)
        self._add_menu_button("Abrir Archivo 📂", self.show_open_file, self.file_ops_layout)
        self.modify_btn = self._add_menu_button("Modificar Archivo ✏️", self.show_modify_file, self.file_ops_layout)
        
        self.btn_trash_ops = self._create_menu_block("Papelera")
        menu_layout.addWidget(self.btn_trash_ops)
        self.trash_ops_layout = self.btn_trash_ops.content_layout
        self.delete_btn = self._add_menu_button("Mover a Papelera 🗑️", self.show_delete_file, self.trash_ops_layout)
        self._add_menu_button("Mostrar Papelera 🚮", self.show_list_trash, self.trash_ops_layout)
        self.recover_btn = self._add_menu_button("Recuperar Archivo ↩️", self.show_recover_file, self.trash_ops_layout)
        
        if self.controller.user_role == "admin":
            self.btn_admin_ops = self._create_menu_block("Administración ⚙️")
            menu_layout.addWidget(self.btn_admin_ops)
            self.admin_ops_layout = self.btn_admin_ops.content_layout
            self._add_menu_button("Gestión de Usuarios", self.show_manage_users, self.admin_ops_layout)
            
        self.btn_perms_ops = self._create_menu_block("Permisos")
        menu_layout.addWidget(self.btn_perms_ops)
        self.perms_ops_layout = self.btn_perms_ops.content_layout
        self.perms_btn = self._add_menu_button("Gestión de Permisos", self.show_manage_perms, self.perms_ops_layout)

        menu_layout.addStretch(1)

        self.btn_logout = QPushButton("Cerrar Sesión 🚪")
        self.btn_logout.setStyleSheet(f"background-color: #c0392b; color: {COLOR_TEXT}; padding: 10px; border: none; border-radius: 5px;")
        menu_layout.addWidget(self.btn_logout)
        
        self._apply_role_restrictions()

        self.main_layout.addWidget(self.side_menu)

    def _apply_role_restrictions(self):
        pass

    def _create_menu_block(self, title):
        frame = ContentBlock(title)
        frame.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; border-radius: 5px; margin-bottom: 10px;")
        title_label = frame.findChild(QLabel)
        if title_label:
            title_label.hide()
            
        return frame

    def _add_menu_button(self, text, command, layout: QVBoxLayout):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PANEL_BG}; 
                color: {COLOR_TEXT}; 
                padding: 8px; 
                border: none; 
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BORDER};
            }}
        """)
        btn.clicked.connect(command)
        layout.addWidget(btn)
        return btn

    def _init_content_area(self):
        self.stacked_content = QStackedWidget()
        self.main_layout.addWidget(self.stacked_content)

        welcome_page = QWidget()
        vbox = QVBoxLayout(welcome_page)
        vbox.setAlignment(Qt.AlignCenter)
        
        welcome_label = QLabel("Bienvenido al Simulador FAT 💾")
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        vbox.addWidget(welcome_label, alignment=Qt.AlignCenter)
        
        user_info_label = QLabel(f"Usuario: {self.controller.current_user} ({self.controller.user_role})")
        vbox.addWidget(user_info_label, alignment=Qt.AlignCenter)

        self.stacked_content.addWidget(welcome_page)
        self.current_page_index = 0

    def _switch_content_page(self, title, page_widget):
        block = ContentBlock(title)
        block.content_layout.addWidget(page_widget)
        
        if self.stacked_content.count() > 1:
            self.stacked_content.removeWidget(self.stacked_content.widget(self.current_page_index))
            
        self.stacked_content.addWidget(block)
        self.current_page_index = self.stacked_content.count() - 1
        self.stacked_content.setCurrentIndex(self.current_page_index)

    def show_create_file(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addWidget(QLabel("Nombre del archivo:"))
        self.create_name_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.create_name_input)
        
        layout.addWidget(QLabel("Contenido del archivo:"))
        self.create_content_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT}; min-height: 150px;")
        layout.addWidget(self.create_content_input)
        
        self.btn_create.setText("Crear Archivo")
        self.btn_create.setStyleSheet(f"background-color: #27ae60; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_create)
        
        self._switch_content_page("1. Crear Archivo", page)

    def show_list_files(self, is_trash=False):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        list_widget = QListWidget()
        list_widget.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        
        self.controller.fat = self.controller.load_fat()
        files = self.controller.get_list_files(is_trash=is_trash)
        
        header = f"{'Nombre':<20} | {'Owner':<15} | {'Tamaño (chars)' if not is_trash else 'Fecha Eliminación':<15} | {'Fecha Modificación' if not is_trash else ''}"
        QListWidgetItem(header, list_widget).setBackground(QColor(COLOR_BORDER))
        
        for file in files:
            date_info = file.get('fecha_eliminacion', 'N/A') if is_trash else file.get('fecha_modificacion', 'N/A')
            size_info = str(file['total_caracteres']) if not is_trash else ''
            
            has_read_perm = self.controller.has_read_permission_logic(file)
            
            # Se muestra si es el dueño, es admin o tiene permiso de lectura, o si está en papelera (listado de trash)
            if self.controller.is_admin() or file['owner'] == self.controller.current_user or has_read_perm or is_trash:
                line = f"{file['name']:<20} | {file['owner']:<15} | {size_info:<15} | {date_info}"
                item = QListWidgetItem(line, list_widget)
                
                # Si no tiene permiso de lectura y no es el dueño ni el admin, colorear para indicar acceso limitado
                if not self.controller.is_admin() and not has_read_perm and file['owner'] != self.controller.current_user:
                     item.setForeground(QColor("#e74c3c"))
                     
        layout.addWidget(list_widget)

        title = "3. Archivos en Papelera" if is_trash else "2. Listar Archivos Disponibles"
        self._switch_content_page(title, page)

    def show_list_trash(self):
        self.show_list_files(is_trash=True)
        
    def show_open_file(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Nombre del archivo:"))
        self.open_name_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        h_layout.addWidget(self.open_name_input)
        
        self.btn_open.setText("Abrir")
        self.btn_open.setStyleSheet(f"background-color: #2980b9; color: {COLOR_TEXT}; padding: 5px;")
        h_layout.addWidget(self.btn_open)
        layout.addLayout(h_layout)
        
        self.open_output.setReadOnly(True)
        self.open_output.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT}; min-height: 200px;")
        layout.addWidget(self.open_output)
        
        self._switch_content_page("4. Abrir Archivo", page)

    def show_modify_file(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Nombre del archivo:"))
        self.modify_name_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        h_layout.addWidget(self.modify_name_input)
        
        self.btn_load_content.setText("Cargar Contenido")
        self.btn_load_content.setStyleSheet(f"background-color: #7f8c8d; color: {COLOR_TEXT}; padding: 5px;")
        h_layout.addWidget(self.btn_load_content)
        layout.addLayout(h_layout)
        
        layout.addWidget(QLabel("Nuevo Contenido:"))
        self.modify_content_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT}; min-height: 150px;")
        layout.addWidget(self.modify_content_input)
        
        self.btn_modify.setText("Guardar Modificación")
        self.btn_modify.setStyleSheet(f"background-color: #f39c12; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_modify)
        
        self._switch_content_page("5. Modificar Archivo", page)
        
    def show_delete_file(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addWidget(QLabel("Nombre del archivo a mover a papelera:"))
        self.delete_name_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.delete_name_input)
        
        self.btn_delete.setText("Mover a Papelera")
        self.btn_delete.setStyleSheet(f"background-color: #e74c3c; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_delete)
        
        self._switch_content_page("6. Mover a Papelera", page)

    def show_recover_file(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addWidget(QLabel("Nombre del archivo a recuperar:"))
        self.recover_name_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.recover_name_input)
        
        self.btn_recover.setText("Recuperar Archivo")
        self.btn_recover.setStyleSheet(f"background-color: #3498db; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_recover)
        
        self._switch_content_page("7. Recuperar Archivo", page)
        
    def show_manage_users(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        list_block = ContentBlock("Usuarios Existentes")
        list_layout = list_block.content_layout
        
        self.user_list.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT}; min-height: 100px;")
        list_layout.addWidget(self.user_list)
        layout.addWidget(list_block)

        add_block = ContentBlock("Agregar Nuevo Usuario")
        add_frame = QFrame()
        add_frame.setStyleSheet("background-color: transparent; border: none;")
        add_layout = QGridLayout(add_frame)
        
        add_layout.addWidget(QLabel("Usuario:"), 0, 0)
        self.add_user_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        add_layout.addWidget(self.add_user_input, 0, 1)

        add_layout.addWidget(QLabel("Contraseña:"), 1, 0)
        self.add_pass_input.setEchoMode(QLineEdit.Password)
        self.add_pass_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        add_layout.addWidget(self.add_pass_input, 1, 1)

        add_layout.addWidget(QLabel("Rol:"), 2, 0)
        self.add_role_combo.clear()
        self.add_role_combo.addItems(["user", "admin"])
        self.add_role_combo.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        add_layout.addWidget(self.add_role_combo, 2, 1)

        self.btn_add_user.setText("Agregar Usuario")
        self.btn_add_user.setStyleSheet(f"background-color: #34495e; color: {COLOR_TEXT}; padding: 10px;")
        add_layout.addWidget(self.btn_add_user, 3, 0, 1, 2)
        
        add_block.content_layout.addWidget(add_frame)
        layout.addWidget(add_block)
        
        self._switch_content_page("8. Gestión de Usuarios (Admin)", page)

    def show_manage_perms(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addWidget(QLabel("Nombre del archivo:"))
        self.perm_file_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.perm_file_input)

        layout.addWidget(QLabel("Usuario objetivo:"))
        self.perm_target_user_input.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        layout.addWidget(self.perm_target_user_input)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Tipo de Permiso:"))
        self.perm_type_combo.clear()
        self.perm_type_combo.addItems(["lectura", "escritura"])
        self.perm_type_combo.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        h_layout.addWidget(self.perm_type_combo)

        h_layout.addWidget(QLabel("Acción:"))
        self.perm_action_combo.clear()
        self.perm_action_combo.addItems(["agregar", "revocar"])
        self.perm_action_combo.setStyleSheet(f"background-color: {COLOR_HIGHLIGHT}; color: {COLOR_TEXT};")
        h_layout.addWidget(self.perm_action_combo)
        layout.addLayout(h_layout)

        self.btn_apply_perm.setText("Aplicar Permiso")
        self.btn_apply_perm.setStyleSheet(f"background-color: #9b59b6; color: {COLOR_TEXT}; padding: 10px;")
        layout.addWidget(self.btn_apply_perm)

        self._switch_content_page("9. Gestión de Permisos (Owner)", page)