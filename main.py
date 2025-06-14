import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QScrollArea, QFrame,
                               QPushButton, QGridLayout, QSizePolicy,
                               QMessageBox, QLineEdit, QComboBox, QDialog,
                               QDialogButtonBox, QFormLayout, QDoubleSpinBox, QStackedWidget, QSpinBox)
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPalette
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления «Наш декор» - Главная")
        self.setWindowIcon(QIcon("logo.ico"))
        self.setMinimumSize(1000, 700)

        self.setup_colors()

        # Подключение к базе данных
        self.db_connection = self.connect_to_db()

        # Создаем стек виджетов для навигации
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_page = MainPage(self)
        self.products_page = ProductsPage(self)
        self.materials_page = MaterialsPage(self)

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.products_page)
        self.stacked_widget.addWidget(self.materials_page)

        self.show_main_page()

    def setup_colors(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        palette.setColor(QPalette.WindowText, QColor("#000000"))
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.AlternateBase, QColor("#E8F4E5"))
        palette.setColor(QPalette.Button, QColor("#2D6033"))
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Highlight, QColor("#3E8043"))
        self.setPalette(palette)

    def connect_to_db(self):
        #Установка соединения с PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="toor",
                host="localhost",
                port="5432"
            )
            return conn
        except Exception as e:
            self.show_error_message(
                "Ошибка подключения к базе данных",
                f"Не удалось подключиться к базе данных: {str(e)}"
            )
            return None

    # Методы навигации
    def show_main_page(self):
        self.setWindowTitle("Система управления «Наш декор» - Главная")
        self.stacked_widget.setCurrentWidget(self.main_page)

    def show_products_page(self):
        self.setWindowTitle("Система управления «Наш декор» - Продукция")
        self.products_page.load_products()
        self.stacked_widget.setCurrentWidget(self.products_page)

    def show_materials_page(self):
        self.setWindowTitle("Система управления «Наш декор» - Материалы")
        self.materials_page.load_materials()
        self.stacked_widget.setCurrentWidget(self.materials_page)

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_warning_message(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_info_message(self, title, message):
        QMessageBox.information(self, title, message)

    def closeEvent(self, event):
        if self.db_connection:
            self.db_connection.close()
        event.accept()


class MainPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок с логотипом
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png").scaled(120, 120, Qt.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label)

        title_label = QLabel("Главное меню")
        title_label.setFont(QFont("Gabriola", 28, QFont.Bold))
        title_label.setStyleSheet("color: #2D6033;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Кнопки навигации
        products_btn = QPushButton("Управление продукцией")
        products_btn.setFont(QFont("Gabriola", 14))
        products_btn.setStyleSheet(self.get_button_style())
        products_btn.clicked.connect(self.main_window.show_products_page)

        materials_btn = QPushButton("Управление материалами")
        materials_btn.setFont(QFont("Gabriola", 14))
        materials_btn.setStyleSheet(self.get_button_style())
        materials_btn.clicked.connect(self.main_window.show_materials_page)

        layout.addWidget(products_btn)
        layout.addWidget(materials_btn)
        layout.addStretch()

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 150px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3E8043;
            }
            QPushButton:pressed {
                background-color: #1D4023;
            }
        """


class ProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        back_btn = QPushButton("Назад")
        back_btn.setFont(QFont("Gabriola", 12))
        back_btn.setStyleSheet(self.get_button_style())
        back_btn.clicked.connect(self.main_window.show_main_page)
        header_layout.addWidget(back_btn)

        title_label = QLabel("Управление продукцией")
        title_label.setFont(QFont("Gabriola", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2D6033;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Область с продукцией (скроллинг)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #BBD9B2;
            }
            QScrollBar::handle:vertical {
                background: #2D6033;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(20)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить продукт")
        self.add_button.setFont(QFont("Gabriola", 12))
        self.add_button.setStyleSheet(self.get_button_style())
        self.add_button.clicked.connect(self.show_add_product_dialog)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setFont(QFont("Gabriola", 12))
        self.refresh_button.setStyleSheet(self.get_button_style())
        self.refresh_button.clicked.connect(self.load_products)

        self.calculate_button = QPushButton("Пересчитать стоимость")
        self.calculate_button.setFont(QFont("Gabriola", 12))
        self.calculate_button.setStyleSheet(self.get_button_style())
        self.calculate_button.clicked.connect(self.recalculate_all_prices)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.calculate_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

    def load_products(self):
        #Загрузка списка продукции из базы данных
        if not self.main_window.db_connection:
            return

        # Очищаем предыдущие данные
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        try:
            cursor = self.main_window.db_connection.cursor()

            # Получаем данные о продукции
            query = """SELECT 
                    p.id_product,
                    tp.type_product,
                    p.product_name,
                    p.min_cost,
                    p.articul,
                    p.width
                FROM products p
                JOIN type_product tp ON p.id_type_product = tp.id_type_product
                ORDER BY p.product_name"""

            cursor.execute(query)
            products = cursor.fetchall()

            if not products:
                self.main_window.show_info_message("Информация", "В базе данных нет продукции.")
                return

            for product in products:
                self.add_product_card(*product)

        except Exception as e:
            self.main_window.show_error_message(
                "Ошибка загрузки продукции",
                f"Произошла ошибка при загрузке продукции: {str(e)}"
            )
        finally:
            if 'cursor' in locals():
                cursor.close()

    def add_product_card(self, product_id, product_type, product_name, min_cost, articul, width):
        # Добавляет карточку продукта в интерфейс
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #E8F4E5;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #BBD9B2;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QGridLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        card.setLayout(layout)

        type_label = QLabel(product_type)
        type_label.setFont(QFont("Gabriola", 14, QFont.Bold))
        type_label.setStyleSheet("color: #2D6033;")

        name_label = QLabel(product_name)
        name_label.setFont(QFont("Gabriola", 16, QFont.Bold))
        name_label.setStyleSheet("color: #1D4023;")

        row1_layout = QHBoxLayout()
        row1_layout.addWidget(type_label)
        row1_layout.addWidget(name_label)
        row1_layout.addStretch()

        cost_label = QLabel(f"{min_cost:.2f} ₽")
        cost_label.setFont(QFont("Gabriola", 14, QFont.Bold))
        cost_label.setStyleSheet("color: #2D6033;")
        row1_layout.addWidget(cost_label)

        layout.addLayout(row1_layout, 0, 0)

        articul_label = QLabel(f"Артикул: {articul}")
        articul_label.setFont(QFont("Gabriola", 13))
        articul_label.setStyleSheet("color: #555555;")
        layout.addWidget(articul_label, 1, 0)

        details_layout = QHBoxLayout()
        details_layout.setSpacing(30)

        min_cost_label = QLabel(f"Мин. стоимость партнера: {min_cost:.2f} ₽")
        min_cost_label.setFont(QFont("Gabriola", 13))
        min_cost_label.setStyleSheet("color: #555555;")
        details_layout.addWidget(min_cost_label)

        width_label = QLabel(f"Ширина: {width} м")
        width_label.setFont(QFont("Gabriola", 13))
        width_label.setStyleSheet("color: #555555;")
        details_layout.addWidget(width_label)

        details_layout.addStretch()
        layout.addLayout(details_layout, 2, 0)

        edit_button = QPushButton("Редактировать")
        edit_button.setFont(QFont("Gabriola", 12))
        edit_button.setStyleSheet(self.get_button_style())
        edit_button.clicked.connect(lambda: self.show_edit_product_dialog(product_id))
        layout.addWidget(edit_button, 3, 0, alignment=Qt.AlignRight)

        # Сохраняем ID продукта в карточке
        card.product_id = product_id

        self.scroll_layout.addWidget(card)

    def show_add_product_dialog(self):
        # Показывает диалог добавления нового продукта
        dialog = ProductDialog(self.main_window, self.main_window.db_connection)
        if dialog.exec() == QDialog.Accepted:
            self.load_products()
            self.main_window.show_info_message("Успех", "Продукт успешно добавлен.")

    def show_edit_product_dialog(self, product_id):
        # Показывает диалог редактирования продукта
        dialog = ProductDialog(self.main_window, self.main_window.db_connection, product_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_products()
            self.main_window.show_info_message("Успех", "Продукт успешно обновлен.")

    def recalculate_all_prices(self):
        # Пересчет стоимости для всей продукции
        if not self.main_window.db_connection:
            return

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите пересчитать стоимость для всей продукции?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            cursor = self.main_window.db_connection.cursor()

            # Получаем список всех продуктов
            cursor.execute("SELECT id_product FROM products")
            product_ids = [row[0] for row in cursor.fetchall()]

            if not product_ids:
                self.main_window.show_info_message("Информация", "Нет продукции для пересчета.")
                return

            # Пересчитываем стоимость для каждого продукта
            updated_count = 0
            for product_id in product_ids:
                new_price = self.calculate_product_cost(product_id)

                if new_price is not None:
                    # Обновляем стоимость в базе данных
                    update_query = """UPDATE products 
                                    SET min_cost = %s 
                                    WHERE id_product = %s"""
                    cursor.execute(update_query, (new_price, product_id))
                    updated_count += 1

            self.main_window.db_connection.commit()
            self.load_products()

            self.main_window.show_info_message(
                "Пересчет завершен",
                f"Стоимость пересчитана для {updated_count} продуктов."
            )

        except Exception as e:
            self.main_window.db_connection.rollback()
            self.main_window.show_error_message(
                "Ошибка пересчета стоимости",
                f"Произошла ошибка при пересчете стоимости: {str(e)}"
            )
        finally:
            if 'cursor' in locals():
                cursor.close()

    def calculate_product_cost(self, product_id):
        # Рассчитывает стоимость продукта на основе типа продукта и его ширины
        if not self.main_window.db_connection:
            return None

        try:
            cursor = self.main_window.db_connection.cursor()

            # Получаем данные о продукте: ширину и коэффициент типа продукта
            cursor.execute("""
                SELECT p.width, tp.coefficient_type_product 
                FROM products p
                JOIN type_product tp ON p.id_type_product = tp.id_type_product
                WHERE p.id_product = %s
            """, (product_id,))

            product_data = cursor.fetchone()

            if not product_data:
                self.main_window.show_warning_message(
                    "Предупреждение",
                    f"Для продукта ID {product_id} не найдены данные. Стоимость не будет пересчитана."
                )
                return None

            width, coefficient = product_data

            BASE_COST_PER_METER = 100.0

            # Рассчитываем стоимость: ширина * базовая стоимость * коэффициент типа
            total_cost = width * BASE_COST_PER_METER * coefficient

            return round(total_cost, 2)

        except Exception as e:
            self.main_window.show_error_message(
                "Ошибка расчета стоимости",
                f"Не удалось рассчитать стоимость для продукта ID {product_id}: {str(e)}"
            )
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 150px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3E8043;
            }
            QPushButton:pressed {
                background-color: #1D4023;
            }
        """


class MaterialsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        back_btn = QPushButton("Назад")
        back_btn.setFont(QFont("Gabriola", 12))
        back_btn.setStyleSheet(self.get_button_style())
        back_btn.clicked.connect(self.main_window.show_main_page)
        header_layout.addWidget(back_btn)

        title_label = QLabel("Управление материалами")
        title_label.setFont(QFont("Gabriola", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2D6033;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Область с материалами (скроллинг)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #BBD9B2;
            }
            QScrollBar::handle:vertical {
                background: #2D6033;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(20)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить материал")
        self.add_button.setFont(QFont("Gabriola", 12))
        self.add_button.setStyleSheet(self.get_button_style())
        self.add_button.clicked.connect(self.show_add_material_dialog)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setFont(QFont("Gabriola", 12))
        self.refresh_button.setStyleSheet(self.get_button_style())
        self.refresh_button.clicked.connect(self.load_materials)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

    def load_materials(self):
        # Загрузка списка материалов из базы данных
        if not self.main_window.db_connection:
            return

        # Очищаем предыдущие данные
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        try:
            cursor = self.main_window.db_connection.cursor()

            # Получаем данные о материалах
            query = """SELECT 
                    m.id_material,
                    tm.type_material,
                    m.material_name,
                    m.unit_price,
                    m.stock_quantity,
                    m.min_quantity,
                    m.package_quantity,
                    m.unit
                FROM materials m
                JOIN type_material tm ON m.id_type_material = tm.id_type_material
                ORDER BY m.material_name"""

            cursor.execute(query)
            materials = cursor.fetchall()

            if not materials:
                self.main_window.show_info_message("Информация", "В базе данных нет материалов.")
                return

            for material in materials:
                self.add_material_card(*material)

        except Exception as e:
            self.main_window.show_error_message(
                "Ошибка загрузки материалов",
                f"Произошла ошибка при загрузке материалов: {str(e)}"
            )
        finally:
            if 'cursor' in locals():
                cursor.close()

    def add_material_card(self, material_id, material_type, material_name, unit_price, stock_quantity, min_quantity, package_quantity, unit):
        # Добавляет карточку материала в интерфейс
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #E8F4E5;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #BBD9B2;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QGridLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        card.setLayout(layout)

        type_label = QLabel(material_type)
        type_label.setFont(QFont("Gabriola", 14, QFont.Bold))
        type_label.setStyleSheet("color: #2D6033;")

        name_label = QLabel(material_name)
        name_label.setFont(QFont("Gabriola", 16, QFont.Bold))
        name_label.setStyleSheet("color: #1D4023;")

        row1_layout = QHBoxLayout()
        row1_layout.addWidget(type_label)
        row1_layout.addWidget(name_label)
        row1_layout.addStretch()

        price_label = QLabel(f"{unit_price:.2f} ₽/{unit}")
        price_label.setFont(QFont("Gabriola", 14, QFont.Bold))
        price_label.setStyleSheet("color: #2D6033;")
        row1_layout.addWidget(price_label)

        layout.addLayout(row1_layout, 0, 0)

        stock_label = QLabel(f"На складе: {stock_quantity} {unit}")
        stock_label.setFont(QFont("Gabriola", 13))
        stock_label.setStyleSheet("color: #555555;")
        layout.addWidget(stock_label, 1, 0)

        details_layout = QHBoxLayout()
        details_layout.setSpacing(30)

        min_qty_label = QLabel(f"Мин. заказ: {min_quantity} {unit}")
        min_qty_label.setFont(QFont("Gabriola", 13))
        min_qty_label.setStyleSheet("color: #555555;")
        details_layout.addWidget(min_qty_label)

        package_label = QLabel(f"Упаковка: {package_quantity} {unit}")
        package_label.setFont(QFont("Gabriola", 13))
        package_label.setStyleSheet("color: #555555;")
        details_layout.addWidget(package_label)

        details_layout.addStretch()
        layout.addLayout(details_layout, 2, 0)

        edit_button = QPushButton("Редактировать")
        edit_button.setFont(QFont("Gabriola", 12))
        edit_button.setStyleSheet(self.get_button_style())
        edit_button.clicked.connect(lambda: self.show_edit_material_dialog(material_id))
        layout.addWidget(edit_button, 3, 0, alignment=Qt.AlignRight)

        # Сохраняем ID материала в карточке
        card.material_id = material_id

        self.scroll_layout.addWidget(card)

    def show_add_material_dialog(self):
        # Показывает диалог добавления нового материала
        dialog = MaterialDialog(self.main_window, self.main_window.db_connection)
        if dialog.exec() == QDialog.Accepted:
            self.load_materials()
            self.main_window.show_info_message("Успех", "Материал успешно добавлен.")

    def show_edit_material_dialog(self, material_id):
        # Показывает диалог редактирования материала
        dialog = MaterialDialog(self.main_window, self.main_window.db_connection, material_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_materials()
            self.main_window.show_info_message("Успех", "Материал успешно обновлен.")

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 150px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3E8043;
            }
            QPushButton:pressed {
                background-color: #1D4023;
            }
        """


class ProductDialog(QDialog):
    # Диалог для добавления/редактирования продукта

    def __init__(self, parent=None, db_connection=None, product_id=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.product_id = product_id
        self.setModal(True)

        if product_id:
            self.setWindowTitle("Редактирование продукта")
            self.is_edit = True
        else:
            self.setWindowTitle("Добавление продукта")
            self.is_edit = False

        self.setMinimumSize(500, 400)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # Инициализация интерфейса диалога
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Форма с полями
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)

        self.articul_edit = QLineEdit()
        self.articul_edit.setFont(QFont("Gabriola", 12))
        self.form_layout.addRow("Артикул:", self.articul_edit)

        self.type_combo = QComboBox()
        self.type_combo.setFont(QFont("Gabriola", 12))
        self.form_layout.addRow("Тип продукта:", self.type_combo)

        self.name_edit = QLineEdit()
        self.name_edit.setFont(QFont("Gabriola", 12))
        self.form_layout.addRow("Наименование:", self.name_edit)

        self.min_cost_spin = QDoubleSpinBox()
        self.min_cost_spin.setFont(QFont("Gabriola", 12))
        self.min_cost_spin.setRange(0, 999999.99)
        self.min_cost_spin.setDecimals(2)
        self.min_cost_spin.setPrefix("₽ ")
        self.form_layout.addRow("Мин. стоимость:", self.min_cost_spin)

        self.width_spin = QDoubleSpinBox()
        self.width_spin.setFont(QFont("Gabriola", 12))
        self.width_spin.setRange(0.01, 10.0)
        self.width_spin.setDecimals(2)
        self.width_spin.setSuffix(" м")
        self.form_layout.addRow("Ширина:", self.width_spin)

        layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def load_data(self):
        # Загрузка данных в форму
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Загружаем типы продуктов
            cursor.execute("SELECT id_type_product, type_product FROM type_product ORDER BY type_product")
            types = cursor.fetchall()

            self.type_combo.clear()
            for type_id, type_name in types:
                self.type_combo.addItem(type_name, type_id)

            # Если это редактирование, загружаем данные продукта
            if self.is_edit and self.product_id:
                cursor.execute("""
                    SELECT articul, id_type_product, product_name, min_cost, width 
                    FROM products 
                    WHERE id_product = %s
                """, (self.product_id,))

                product_data = cursor.fetchone()
                if product_data:
                    self.articul_edit.setText(product_data[0])
                    self.name_edit.setText(product_data[2])
                    self.min_cost_spin.setValue(float(product_data[3]))
                    self.width_spin.setValue(float(product_data[4]))

                    # Устанавливаем правильный тип продукта
                    type_index = self.type_combo.findData(product_data[1])
                    if type_index >= 0:
                        self.type_combo.setCurrentIndex(type_index)

        except Exception as e:
            self.parent().show_error_message(
                "Ошибка загрузки данных",
                f"Не удалось загрузить данные: {str(e)}"
            )
            self.reject()
        finally:
            if 'cursor' in locals():
                cursor.close()

    def validate_and_accept(self):
        # Проверка данных и сохранение
        try:
            articul = self.articul_edit.text().strip()
            product_name = self.name_edit.text().strip()
            min_cost = self.min_cost_spin.value()
            width = self.width_spin.value()
            type_id = self.type_combo.currentData()

            # Проверка обязательных полей
            if not articul:
                raise ValueError("Артикул не может быть пустым")
            if not product_name:
                raise ValueError("Наименование не может быть пустым")
            if type_id is None:
                raise ValueError("Не выбран тип продукта")
            if min_cost <= 0:
                raise ValueError("Стоимость должна быть положительной")
            if width <= 0:
                raise ValueError("Ширина должна быть положительной")

            # Сохранение данных
            if self.save_product(articul, type_id, product_name, min_cost, width):
                self.accept()

        except ValueError as e:
            self.parent().show_warning_message("Проверка данных", str(e))
        except Exception as e:
            self.parent().show_error_message(
                "Ошибка сохранения",
                f"Не удалось сохранить продукт: {str(e)}"
            )

    def save_product(self, articul, type_id, product_name, min_cost, width):
        # Сохранение продукта в базу данных
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            if self.is_edit and self.product_id:
                # Обновление существующего продукта
                query = """
                    UPDATE products 
                    SET articul = %s, 
                        id_type_product = %s, 
                        product_name = %s, 
                        min_cost = %s, 
                        width = %s
                    WHERE id_product = %s
                """
                cursor.execute(query, (articul, type_id, product_name, min_cost, width, self.product_id))
            else:
                # Добавление нового продукта
                query = """
                    INSERT INTO products 
                    (articul, id_type_product, product_name, min_cost, width)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (articul, type_id, product_name, min_cost, width))

            self.db_connection.commit()
            return True

        except Exception as e:
            self.db_connection.rollback()
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()


class MaterialDialog(QDialog):
    # Диалог для добавления/редактирования материала

    def __init__(self, parent=None, db_connection=None, material_id=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.material_id = material_id
        self.setModal(True)

        if material_id:
            self.setWindowTitle("Редактирование материала")
            self.is_edit = True
        else:
            self.setWindowTitle("Добавление материала")
            self.is_edit = False

        self.setMinimumSize(500, 500)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # Инициализация интерфейса диалога
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)

        self.name_edit = QLineEdit()
        self.name_edit.setFont(QFont("Gabriola", 12))
        self.form_layout.addRow("Наименование:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.setFont(QFont("Gabriola", 12))
        self.form_layout.addRow("Тип материала:", self.type_combo)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setFont(QFont("Gabriola", 12))
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("₽ ")
        self.form_layout.addRow("Цена за единицу:", self.price_spin)

        self.stock_spin = QSpinBox()
        self.stock_spin.setFont(QFont("Gabriola", 12))
        self.stock_spin.setRange(0, 999999)
        self.form_layout.addRow("Количество на складе:", self.stock_spin)

        self.min_qty_spin = QSpinBox()
        self.min_qty_spin.setFont(QFont("Gabriola", 12))
        self.min_qty_spin.setRange(0, 999999)
        self.form_layout.addRow("Минимальное количество:", self.min_qty_spin)

        self.package_spin = QSpinBox()
        self.package_spin.setFont(QFont("Gabriola", 12))
        self.package_spin.setRange(0, 999999)
        self.form_layout.addRow("Количество в упаковке:", self.package_spin)

        self.unit_combo = QComboBox()
        self.unit_combo.setFont(QFont("Gabriola", 12))
        self.unit_combo.addItems(["шт", "м", "кг", "л", "упак"])
        self.form_layout.addRow("Единица измерения:", self.unit_combo)

        layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def load_data(self):
        # Загрузка данных в форму
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Загружаем типы материалов
            cursor.execute("SELECT id_type_material, type_material FROM type_material ORDER BY type_material")
            types = cursor.fetchall()

            self.type_combo.clear()
            for type_id, type_name in types:
                self.type_combo.addItem(type_name, type_id)

            # Если это редактирование, загружаем данные материала
            if self.is_edit and self.material_id:
                cursor.execute("""
                    SELECT material_name, id_type_material, unit_price, 
                           stock_quantity, min_quantity, package_quantity, unit 
                    FROM materials 
                    WHERE id_material = %s
                """, (self.material_id,))

                material_data = cursor.fetchone()
                if material_data:
                    self.name_edit.setText(material_data[0])
                    self.price_spin.setValue(float(material_data[2]))
                    self.stock_spin.setValue(material_data[3])
                    self.min_qty_spin.setValue(material_data[4])
                    self.package_spin.setValue(material_data[5])

                    # Устанавливаем правильный тип материала
                    type_index = self.type_combo.findData(material_data[1])
                    if type_index >= 0:
                        self.type_combo.setCurrentIndex(type_index)

                    # Устанавливаем правильную единицу измерения
                    unit_index = self.unit_combo.findText(material_data[6])
                    if unit_index >= 0:
                        self.unit_combo.setCurrentIndex(unit_index)

        except Exception as e:
            self.parent().show_error_message(
                "Ошибка загрузки данных",
                f"Не удалось загрузить данные: {str(e)}"
            )
            self.reject()
        finally:
            if 'cursor' in locals():
                cursor.close()

    def validate_and_accept(self):
        # Проверка данных и сохранение
        try:
            material_name = self.name_edit.text().strip()
            unit_price = self.price_spin.value()
            stock_quantity = self.stock_spin.value()
            min_quantity = self.min_qty_spin.value()
            package_quantity = self.package_spin.value()
            unit = self.unit_combo.currentText()
            type_id = self.type_combo.currentData()

            # Проверка обязательных полей
            if not material_name:
                raise ValueError("Наименование не может быть пустым")
            if type_id is None:
                raise ValueError("Не выбран тип материала")
            if unit_price <= 0:
                raise ValueError("Цена должна быть положительной")
            if min_quantity <= 0:
                raise ValueError("Минимальное количество должно быть положительным")
            if package_quantity <= 0:
                raise ValueError("Количество в упаковке должно быть положительным")

            # Сохранение данных
            if self.save_material(material_name, type_id, unit_price, stock_quantity, min_quantity, package_quantity, unit):
                self.accept()

        except ValueError as e:
            self.parent().show_warning_message("Проверка данных", str(e))
        except Exception as e:
            self.parent().show_error_message(
                "Ошибка сохранения",
                f"Не удалось сохранить материал: {str(e)}"
            )

    def save_material(self, material_name, type_id, unit_price, stock_quantity, min_quantity, package_quantity, unit):
        # Сохранение материала в базу данных
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            if self.is_edit and self.material_id:
                # Обновление существующего материала
                query = """
                    UPDATE materials 
                    SET material_name = %s, 
                        id_type_material = %s, 
                        unit_price = %s, 
                        stock_quantity = %s, 
                        min_quantity = %s, 
                        package_quantity = %s, 
                        unit = %s
                    WHERE id_material = %s
                """
                cursor.execute(query, (material_name, type_id, unit_price, stock_quantity, min_quantity, package_quantity, unit, self.material_id))
            else:
                # Добавление нового материала
                query = """
                    INSERT INTO materials 
                    (material_name, id_type_material, unit_price, 
                     stock_quantity, min_quantity, package_quantity, unit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (material_name, type_id, unit_price, stock_quantity, min_quantity, package_quantity, unit))

            self.db_connection.commit()
            return True

        except Exception as e:
            self.db_connection.rollback()
            raise e
        finally:
            if 'cursor' in locals():
                cursor.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Gabriola", 12))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())