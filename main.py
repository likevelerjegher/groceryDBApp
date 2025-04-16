from database import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import ttkthemes
import sv_ttk
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    renameTable
    logging.info("renameTable function is available")
except NameError:
    logging.error("renameTable function is not imported from database")

mainBgColor = "#eaeaea"

QUERIES = {
"Lab 4": [
    ("Вывести всех сотрудников с опытом работы больше 10 лет", 'SELECT * FROM grocery."Сотрудник" WHERE experience > 10'),
    ("Вывести всех сотрудников с опытом работы больше 5 лет, отсортированных по ФИО", 'SELECT * FROM grocery."Сотрудник" WHERE experience > 5 ORDER BY full_name'),
    ("Вывести все товары, отсортированные по цене", 'SELECT * FROM grocery."Товар" ORDER BY price'),
    ("Вывести все данные из таблицы Поставщик", 'SELECT * FROM grocery."Поставщик"'),
    ("Вывести все склады, которые имеют расположение “Мясной склад”", 'SELECT * FROM grocery."Склад" WHERE storage_location = \'Мясной склад\''),
    ("Перекрёстное соединение таблиц Заказ и Товар с полной стоимостью заказа более 430 и стоимостью продукта более 12", 'SELECT * FROM grocery."Заказ" CROSS JOIN grocery."Товар" WHERE grocery."Заказ".total_cost > 430 AND grocery."Товар".price > 12'),
    ("Перекрёстное соединение таблиц Заказ и Товар с полной стоимостью заказа более 430 или стоимостью продукта более 12", '''
        SELECT grocery."Заказ".order_number,
               grocery."Товар".name AS product_name
        FROM grocery."Заказ"
        FULL OUTER JOIN grocery."Заказ_Товар" ON grocery."Заказ".id = grocery."Заказ_Товар".order_id
        FULL OUTER JOIN grocery."Товар" ON grocery."Заказ_Товар".product_id = grocery."Товар".id
        WHERE grocery."Заказ".total_cost > 430 OR grocery."Товар".price > 12
    '''),
    ("Внутреннее соединение таблиц Товар и Поставщик", 'SELECT * FROM grocery."Товар" INNER JOIN grocery."Поставщик" ON grocery."Товар".supplier_id = grocery."Поставщик".id'),
    ("Внутреннее соединение таблиц Клиент и Заказ с условием, что сумма заказа от 200 до 400", 'SELECT grocery."Клиент".full_name, grocery."Заказ".total_cost, grocery."Заказ".order_date FROM grocery."Клиент" INNER JOIN grocery."Заказ" ON grocery."Клиент".id = grocery."Заказ".client_id WHERE grocery."Заказ".total_cost > 200 AND grocery."Заказ".total_cost < 400'),
    ("Левое внешнее соединение таблиц Товар и Поставщик с ценой продукта более 20", 'SELECT * FROM grocery."Товар" LEFT OUTER JOIN grocery."Поставщик" ON grocery."Товар".supplier_id = grocery."Поставщик".id WHERE grocery."Товар".price > 20'),
    ("Левое внешнее соединение таблиц Платеж и Заказ", '''
        SELECT grocery."Заказ".order_number,
               grocery."Заказ".total_cost,
               grocery."Заказ".order_date,
               grocery."Заказ".client_id,
               grocery."Заказ".employee_id,
               grocery."Платеж".payment_number,
               grocery."Платеж".payment_date,
               grocery."Платеж".payment_time,
               grocery."Платеж".payment_method,
               grocery."Платеж".payment_status
        FROM grocery."Заказ"
        LEFT OUTER JOIN grocery."Платеж" ON grocery."Заказ".payment_id = grocery."Платеж".id
    '''),
    ("Правое внешнее соединение таблиц Товар и Заказ", '''
        SELECT grocery."Товар".id AS product_id,
               grocery."Товар".name AS product_name,
               grocery."Товар".country,
               grocery."Товар".category,
               grocery."Товар".price,
               grocery."Заказ_Товар".order_id,
               grocery."Заказ".order_number,
               grocery."Заказ".total_cost,
               grocery."Заказ".order_date
        FROM grocery."Товар"
        RIGHT OUTER JOIN grocery."Заказ_Товар"
            ON grocery."Товар".id = grocery."Заказ_Товар".product_id
        LEFT JOIN grocery."Заказ"
            ON grocery."Заказ_Товар".order_id = grocery."Заказ".id
    '''),
    ("Правое внешнее соединение таблиц Склад и Товар с условием, что количество товара на складе больше 100", '''
        SELECT grocery."Склад".id,
               grocery."Склад".storage_location,
               grocery."Склад".product_quantity,
               grocery."Товар".name,
               grocery."Товар".price
        FROM grocery."Склад"
        RIGHT OUTER JOIN grocery."Товар"
            ON grocery."Склад".product_id = grocery."Товар".id
        WHERE grocery."Склад".product_quantity > 100
    '''),
    ("Полное внешнее соединение таблиц Товар и Заказ", 'SELECT grocery."Заказ".*, grocery."Заказ_Товар".* FROM grocery."Заказ" FULL OUTER JOIN grocery."Заказ_Товар" ON grocery."Заказ".id = grocery."Заказ_Товар".order_id'),
    ("Полное внешнее соединение таблиц Сотрудник и Заказ", 'SELECT * FROM grocery."Сотрудник" FULL OUTER JOIN grocery."Заказ" ON grocery."Сотрудник".id = grocery."Заказ".employee_id'),
    ("Вывести сотрудников, в названии должности которых есть “Старший”", 'SELECT * FROM grocery."Сотрудник" WHERE position LIKE \'%Старший%\'')
],

"Lab 5": [
    ("Вывести среднюю арифметическую цену всех товаров", 'SELECT AVG(price) AS Average_salary FROM grocery."Товар"'),
    ("Вывести количество строк, где должность сотрудника заканчивается на “продавец”", 'SELECT COUNT(position) FROM grocery."Сотрудник" WHERE position LIKE \'%продавец\''),
    ("Вывести максимальную температуру склада", 'SELECT MAX(temperature) AS Max_Temperature FROM grocery."Склад"'),
    ("Вывести минимальную сумму заказа", 'SELECT MIN(total_cost) AS mininal_total_cost FROM grocery."Заказ"'),
    ("Вывести общее количество товаров на складах", 'SELECT SUM(product_quantity) AS total_product_quantity FROM grocery."Склад"'),
    ("Вычислить количество товаров в каждой категории", 'SELECT COUNT(name) AS product_amount, category AS product_category FROM grocery."Товар" GROUP BY category'),
    ("Вывести список всех ФИО из таблиц Сотрудник и Клиент, отсортированных в алфавитном порядке", 'SELECT full_name AS ФИО FROM grocery."Клиент" UNION SELECT full_name AS ФИО FROM grocery."Сотрудник" ORDER BY ФИО'),
    ("Объединить таблицы Сотрудник и Клиент в одну по типу", 'SELECT \'Сотрудник\' AS Тип, id AS Идентификатор, full_name FROM grocery."Сотрудник" UNION ALL SELECT \'Клиент\' AS Тип, grocery."Клиент".id AS Идентификатор, full_name FROM grocery."Клиент"'),
    ("Вывести склады, где количество продуктов выше среднего по всем складам", '''
        WITH temporaryTable (averageQuantity) AS (
            SELECT AVG(product_quantity) FROM grocery."Склад"
        )
        SELECT storage_location, address, product_quantity
        FROM grocery."Склад", temporaryTable
        WHERE grocery."Склад".product_quantity > temporaryTable.averageQuantity
    '''),
    ("Вывести id клиентов, которые сделали хотя бы один заказ", 'SELECT id FROM grocery."Клиент" INTERSECT SELECT client_id FROM grocery."Заказ"'),
    ("Вывести всех поставщиков, которые находятся в Гомеле", 'SELECT * FROM (SELECT * FROM grocery."Поставщик" WHERE address LIKE \'Гомель%\') AS подзапрос'),
    ("Вывести клиентов, у которых совершено более одного заказа", '''
        SELECT client_id, order_count
        FROM (
            SELECT client_id, COUNT(*) AS order_count
            FROM grocery."Заказ"
            GROUP BY client_id
        ) AS OrderStats
        WHERE order_count > 1
    '''),
    ("Вывести данные о платежах, статус которых «Оплачен» или «Отменен»", '''
        SELECT * FROM grocery."Платеж"
        WHERE payment_status IN (
            SELECT payment_status FROM grocery."Платеж"
            WHERE payment_status LIKE '%Оплачен%' OR payment_status LIKE '%Отменен%'
        )
    '''),
    ("Вывести товары, которые произведены не в Беларуси", '''
        SELECT name, category, country, price FROM grocery."Товар"
        EXCEPT
        SELECT name, category, country, price FROM grocery."Товар" WHERE country LIKE '%Беларусь%'
    '''),
    ("Вывести склады, средняя температура которых превышает 7 градусов", '''
        SELECT * FROM grocery."Склад"
        WHERE storage_location IN (
            SELECT storage_location FROM grocery."Склад"
            GROUP BY storage_location
            HAVING AVG(temperature) >= 7
        )
    ''')
],

    "Custom": []
}


def initWindow():
    root = tk.Tk()
    root.title('Grocery Store Manager')
    root.geometry("1000x700+100+80")
    root.resizable(True, True)
    root.configure(background=mainBgColor)

    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=0)
    root.grid_columnconfigure(0, weight=1)

    selectedTable = addTableChoice(root)
    newTable = addTable(root)
    addButtons(root)

    sv_ttk.use_light_theme()
    return root, newTable, selectedTable


def addTable(parent):
    table_frame = tk.Frame(parent, bg=mainBgColor)
    table_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    table = ttk.Treeview(table_frame, show='headings', selectmode='browse')
    table.grid(row=0, column=0, sticky='nsew')

    v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    v_scroll.grid(row=0, column=1, sticky='ns')
    table.configure(yscrollcommand=v_scroll.set)

    h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
    h_scroll.grid(row=1, column=0, sticky='ew')
    table.configure(xscrollcommand=h_scroll.set)

    style = ttk.Style()
    style.configure("TScrollbar", troughcolor="#E8E8E8", background=mainBgColor, borderwidth=0, width=10)
    style.configure("Treeview", rowheight=25)
    table.tag_configure('evenrow', background='#f3f3f3')

    table.bind('<ButtonRelease-1>', lambda e: onSelectElement(e))
    return table


def addTableChoice(parent):
    def onSelect(event):
        global colnames
        if selectedTable.get() != "---":
            data, colnames = getTableData(conn, selectedTable.get())
            updateTable(data, colnames)
            blockCRUD(False)

    frame = tk.Frame(parent, bg=mainBgColor)
    frame.grid(row=0, column=0, sticky='ne', padx=5, pady=5)

    selectedTable = tk.StringVar(parent)
    options = getAllTables(conn)
    options.append("---")

    drop = ttk.Combobox(frame, textvariable=selectedTable, values=options, state='readonly')
    drop.current(0)
    drop.bind("<<ComboboxSelected>>", onSelect)

    tk.Label(frame, text='Таблица:', bg=mainBgColor, font=('Helvetica', 12)).pack(side=tk.LEFT)
    drop.pack(side=tk.LEFT, padx=5)

    return selectedTable


def addButtons(parent):
    global CRUDbuttons
    frame = tk.Frame(parent, bg=mainBgColor)
    frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

    for i in range(10):
        frame.grid_columnconfigure(i, weight=1)

    button_configs = [
        ("Add", lambda: createAddWindow(parent), tk.DISABLED),
        ("Delete", lambda: createRemoveWindow(parent), tk.DISABLED),
        ("Update", lambda: createUpdateWindow(parent), tk.DISABLED),
        ("New Table", lambda: createTableWindow(parent), tk.NORMAL),
        ("Drop Table", lambda: dropTableWindow(parent), tk.NORMAL),
        ("Modify", lambda: modifyTableWindow(parent), tk.NORMAL),
        ("Backup", lambda: backupAndNotify(parent), tk.NORMAL),
        ("Restore", lambda: restoreTableWindow(parent), tk.NORMAL),
        ("Export", lambda: exportTableWindow(parent), tk.NORMAL),
        ("Queries", lambda: queryChoiceWindow(parent), tk.NORMAL),
    ]

    buttons = []
    for i, (text, cmd, state) in enumerate(button_configs):
        btn = tk.Button(frame, text=text, command=cmd, state=state, bg='#666666', fg='#333333',
                        font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10)
        btn.grid(row=0, column=i, sticky='ew')
        buttons.append(btn)

    CRUDbuttons = buttons[:3]


def backupAndNotify(parent):
    window = tk.Toplevel(parent)
    window.title("Backup Options")
    window.geometry("300x200")
    window.configure(bg=mainBgColor)

    tk.Label(window, text="Choose backup type:", bg=mainBgColor, font=('Arial', 12)).pack(pady=10)
    backup_type = tk.StringVar(value="full")

    tk.Radiobutton(window, text="Full Database", variable=backup_type, value="full", bg=mainBgColor).pack(anchor='w',
                                                                                                          padx=10)
    tk.Radiobutton(window, text="Single Table", variable=backup_type, value="single", bg=mainBgColor).pack(anchor='w',
                                                                                                           padx=10)

    table_var = tk.StringVar(window)
    tables = getAllTables(conn)
    table_menu = ttk.OptionMenu(window, table_var, None, *tables)
    table_menu.pack(pady=5)
    table_menu.config(state='disabled')

    def toggle_table_menu():
        table_menu.config(state='normal' if backup_type.get() == "single" else 'disabled')

    backup_type.trace('w', lambda *args: toggle_table_menu())

    def perform_backup():
        if backup_type.get() == "full":
            backup_path = backupDatabase(conn)
        else:
            if not table_var.get():
                messagebox.showerror("Error", "Please select a table")
                return
            backup_path = backupDatabase(conn, table_var.get())
        window.destroy()
        if isinstance(backup_path, str):
            showBackupInfo(parent, backup_path)
        else:
            messagebox.showerror("Error", backup_path or "Backup failed")

    tk.Button(window, text="Backup", command=perform_backup, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10).pack(pady=10)


def showBackupInfo(parent, backup_path):
    window = tk.Toplevel(parent)
    window.title("Backup Created")
    window.geometry("400x150")
    window.configure(bg=mainBgColor)

    tk.Label(window, text="Backup successfully created!", bg=mainBgColor, font=('Arial', 12, 'bold')).pack(pady=10)
    tk.Label(window, text=f"Location: {backup_path}", bg=mainBgColor, font=('Arial', 10)).pack(pady=5)
    tk.Button(window, text="OK", command=window.destroy, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10).pack(pady=10)


def restoreTableWindow(parent):
    window = tk.Toplevel(parent)
    window.title("Restore Options")
    window.geometry("400x250")
    window.configure(bg=mainBgColor)

    tk.Label(window, text="Choose restore type:", bg=mainBgColor, font=('Arial', 12)).pack(pady=10)
    restore_type = tk.StringVar(value="single")

    tk.Radiobutton(window, text="Single Table", variable=restore_type, value="single", bg=mainBgColor).pack(anchor='w',
                                                                                                            padx=10)
    tk.Radiobutton(window, text="Full Database", variable=restore_type, value="full", bg=mainBgColor).pack(anchor='w',
                                                                                                           padx=10)

    tk.Label(window, text="Select a table (for single restore):", bg=mainBgColor, font=('Arial', 12)).pack(pady=5)
    table_var = tk.StringVar(window)
    tables = getAllTables(conn)
    table_menu = ttk.OptionMenu(window, table_var, None, *tables)
    table_menu.pack(pady=5)

    def select_and_restore():
        global colnames
        if restore_type.get() == "single":
            filename = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql"), ("All files", "*.*")])
            if filename and table_var.get():
                result = restoreTable(conn, table_var.get(), filename)
                if result:
                    messagebox.showerror("Error", result)
                else:
                    refreshTableList()
                    if selectedTable.get() == table_var.get():
                        data, colnames = getTableData(conn, table_var.get())
                        updateTable(data, colnames)
            else:
                messagebox.showerror("Error", "Please select a table and SQL file")
        else:
            dirname = filedialog.askdirectory(title="Select Backup Directory")
            if dirname:
                result = restoreDatabase(conn, dirname)
                if result:
                    messagebox.showerror("Error", result)
                else:
                    refreshTableList()
                    if selectedTable.get() in getAllTables(conn):
                        data, colnames = getTableData(conn, selectedTable.get())
                        updateTable(data, colnames)
            else:
                messagebox.showerror("Error", "Please select a backup directory")
        window.destroy()

    tk.Button(window, text="Restore", command=select_and_restore, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10).pack(pady=10)


def createTableWindow(parent):
    window = tk.Toplevel(parent)
    window.title("Add New Table")
    window.geometry("400x400")
    window.configure(bg=mainBgColor)

    # Table name input
    ttk.Label(window, text="Enter the name for the table:", background=mainBgColor).pack(pady=5)
    table_name_entry = ttk.Entry(window)
    table_name_entry.pack(pady=5)

    # Column count input
    ttk.Label(window, text="How many columns will be in the table?", background=mainBgColor).pack(pady=5)
    column_count_entry = ttk.Entry(window)
    column_count_entry.pack(pady=5)

    # Frame for column entries
    columns_frame = tk.Frame(window, bg=mainBgColor)
    columns_frame.pack(pady=10)
    column_entries = []

    def update_column_fields(event=None):
        for widget in columns_frame.winfo_children():
            widget.destroy()
        try:
            column_count = int(column_count_entry.get())
            if column_count <= 0:
                messagebox.showwarning("Input Error", "Please enter a positive number for columns.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for columns.")
            return
        column_entries.clear()
        for i in range(column_count):
            ttk.Label(columns_frame, text=f"Column {i+1} (e.g., 'id SERIAL'):", background=mainBgColor).pack(pady=2)
            entry = ttk.Entry(columns_frame)
            entry.pack(pady=2)
            column_entries.append(entry)

    column_count_entry.bind("<Return>", update_column_fields)
    tk.Button(window, text="Generate Column Fields", command=update_column_fields, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)

    def create_table():
        table_name = table_name_entry.get().strip()
        if not table_name:
            messagebox.showwarning("Input Error", "Please enter a table name.")
            return
        try:
            column_count = int(column_count_entry.get())
            if column_count <= 0:
                messagebox.showwarning("Input Error", "Please enter a positive number for columns.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for columns.")
            return
        columns = []
        for entry in column_entries:
            col_def = entry.get().strip()
            if not col_def:
                messagebox.showwarning("Input Error", "Please enter names and types for all columns.")
                return
            # Split column definition into name and type
            parts = col_def.split()
            if len(parts) < 2:
                messagebox.showwarning("Input Error", f"Invalid column definition: '{col_def}'. Use format 'name type'.")
                return
            col_name = parts[0]
            col_type = ' '.join(parts[1:])
            columns.append((col_name, col_type))
        result = createTable(conn, table_name, columns)
        if result:
            messagebox.showerror("Error", result)
        else:
            messagebox.showinfo("Success", f"Table '{table_name}' created successfully!")
            refreshTableList(parent)
            selectedTable.set(table_name)
            data, new_colnames = getTableData(conn, table_name)
            updateTable(data, new_colnames)
            logging.debug(f"Created and selected new table '{table_name}' with columns: {new_colnames}")
            window.destroy()

    tk.Button(window, text="Create Table", command=create_table, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=10)


def createTableAction(table_name, columns, window):
    global selectedTable, colnames
    if not table_name or not columns:
        messagebox.showerror("Error", "Please provide a table name and at least one column")
        return
    result = createTable(conn, table_name, columns)
    if result:
        messagebox.showerror("Error", result)
    else:
        window.destroy()
        refreshTableList()
        if table_name in getTables(conn):
            selectedTable.set(table_name)
            data, colnames = getTableData(conn, table_name)
            updateTable(data, colnames)
            logging.debug(f"Selected new table {table_name} with columns: {colnames}")


def dropTableWindow(parent):
    if not selectedTable.get() or selectedTable.get() == "---":
        messagebox.showerror("Error", "Please select a table first")
        return

    # Use tkinter.messagebox.askyesno for confirmation
    if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to drop the table '{selectedTable.get()}'?"):
        return

    # Call dropTableAction
    dropTableAction(selectedTable.get(), parent)

def dropTableAction(table_name, parent):
    global selectedTable, colnames, table, selectedElement
    if not table_name:
        messagebox.showerror("Error", "No table selected")
        return

    result = dropTable(conn, table_name)
    if result:
        messagebox.showerror("Error", result)
        logging.error(f"Drop table failed: {result}")
    else:
        messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully!")
        # Refresh the table list
        refreshTableList(parent)
        # Clear the table display if the dropped table was selected
        if selectedTable.get() == table_name:
            selectedTable.set('---')
            colnames = None
            selectedElement = None
            table.delete(*table.get_children())
            table['columns'] = []
            logging.debug("Cleared table UI after dropping selected table")
        # Disable CRUD buttons
        blockCRUD(True)


def modifyTableWindow(parent):
    window = tk.Toplevel(parent)
    window.title("Modify Table")
    window.geometry("400x500")
    window.configure(bg=mainBgColor)

    table_var = tk.StringVar(window)
    tables = getAllTables(conn)
    logging.debug(f"Tables in modifyTableWindow: {tables}")
    ttk.OptionMenu(window, table_var, None, *tables, command=lambda _: showColumns(table_var.get(), columns_tree)).pack(
        pady=10)

    columns_tree = ttk.Treeview(window, columns=("Name", "Type"), show='headings')
    columns_tree.heading("Name", text="Column Name")
    columns_tree.heading("Type", text="Data Type")
    columns_tree.pack(pady=10)
    columns_tree.tag_configure('evenrow', background='#f3f3f3')

    tk.Button(window, text="Rename Table", command=lambda: renameTableWindow(table_var, window), bg='#666666',
              fg='#333333', font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)
    tk.Button(window, text="Add Column", command=lambda: addColumnWindow(table_var, columns_tree), bg='#666666',
              fg='#333333', font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)
    tk.Button(window, text="Drop Column", command=lambda: dropColumnAction(table_var.get(), columns_tree),
              bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)
    tk.Button(window, text="Edit Column", command=lambda: editColumnWindow(table_var.get(), columns_tree),
              bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)


def showColumns(table_name, tree):
    for item in tree.get_children():
        tree.delete(item)
    if table_name:
        columns = getColumnInfo(conn, table_name)
        for i, col in enumerate(columns):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', tk.END, values=col, tags=(tag,))


def renameTableWindow(table_var, parent):
    window = tk.Toplevel(parent)
    window.title("Rename Table")
    window.geometry("300x150")
    window.configure(bg=mainBgColor)

    new_name_entry = ttk.Entry(window)
    ttk.Label(window, text="New Table Name:", background=mainBgColor).pack(pady=5)
    new_name_entry.pack(pady=5)

    def rename_action():
        old_name = table_var.get()
        new_name = new_name_entry.get()
        if new_name:
            result = renameTable(conn, old_name, new_name)
            if result:
                messagebox.showerror("Error", result)
            else:
                refreshTableList()
                table_var.set(new_name)
                if selectedTable.get() == old_name:
                    selectedTable.set(new_name)
                    data, colnames = getTableData(conn, new_name)
                    updateTable(data, colnames)
                showColumns(new_name, parent.children['!treeview'])
                window.destroy()
        else:
            messagebox.showerror("Error", "Please enter a new table name")

    tk.Button(window, text="Rename", command=rename_action, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=10)


def addColumnWindow(table_var, tree):
    if not table_var.get():
        messagebox.showerror("Error", "Please select a table first")
        return

    window = tk.Toplevel()
    window.title("Add Column")
    window.geometry("300x200")
    window.configure(bg=mainBgColor)

    name_entry = ttk.Entry(window)
    type_entry = ttk.Entry(window)
    ttk.Label(window, text="Column Name:", background=mainBgColor).pack()
    name_entry.pack(pady=5)
    ttk.Label(window, text="Data Type:", background=mainBgColor).pack()
    type_entry.pack(pady=5)
    tk.Button(window, text="Add",
              command=lambda: addColumnAction(table_var.get(), name_entry.get(), type_entry.get(), window, tree),
              bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=10)


def addColumnAction(table_name, column_name, column_type, window, tree):
    global colnames
    if not table_name:
        messagebox.showerror("Error", "No table selected")
        return
    if not column_name or not column_type:
        messagebox.showerror("Error", "Please provide both a column name and type")
        return
    result = addColumn(conn, table_name, column_name, column_type)
    if result:
        messagebox.showerror("Error", result)
    else:
        window.destroy()
        showColumns(table_name, tree)
        selectedTable.set(table_name)
        data, colnames = getTableData(conn, table_name)
        updateTable(data, colnames)
        logging.debug(f"Updated colnames after adding column: {colnames}")


def dropColumnAction(table_name, tree):
    if not table_name:
        messagebox.showerror("Error", "No table selected")
        return
    selected = tree.selection()
    if selected:
        column_name = tree.item(selected[0])['values'][0]
        result = dropColumn(conn, table_name, column_name)
        if result:
            messagebox.showerror("Error", result)
        else:
            tree.delete(selected[0])
            if selectedTable.get() == table_name:
                data, colnames = getTableData(conn, table_name)
                updateTable(data, colnames)


def editColumnWindow(table_name, tree):
    if not table_name:
        messagebox.showerror("Error", "No table selected")
        return
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a column to edit")
        return

    window = tk.Toplevel()
    window.title("Edit Column")
    window.geometry("300x200")
    window.configure(bg=mainBgColor)

    old_name = tree.item(selected[0])['values'][0]
    old_type = tree.item(selected[0])['values'][1]
    new_name_entry = ttk.Entry(window)
    new_type_entry = ttk.Entry(window)

    ttk.Label(window, text="Column Name:", background=mainBgColor).pack(pady=5)
    new_name_entry.insert(0, old_name)
    new_name_entry.pack(pady=5)
    ttk.Label(window, text="Data Type:", background=mainBgColor).pack(pady=5)
    new_type_entry.insert(0, old_type)
    new_type_entry.pack(pady=5)

    def edit_action():
        new_name = new_name_entry.get()
        new_type = new_type_entry.get()
        if not new_name or not new_type:
            messagebox.showerror("Error", "Please enter both a name and type")
            return
        if new_name != old_name:
            result = renameColumn(conn, table_name, old_name, new_name)
            if result:
                messagebox.showerror("Error", result)
                return
        if new_type != old_type:
            result = changeColumnType(conn, table_name, new_name, new_type)
            if result:
                messagebox.showerror("Error", result)
                return
        tree.item(selected[0], values=(new_name, new_type))
        if selectedTable.get() == table_name:
            data, colnames = getTableData(conn, table_name)
            updateTable(data, colnames)
        window.destroy()

    tk.Button(window, text="Save", command=edit_action, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=10)


def exportTableWindow(parent):
    data, colnames = getTableData(conn, selectedTable.get())
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filename:
        exportToCSV(data, colnames, filename)


def createAddWindow(parent):
    global colnames
    if selectedTable.get() == "---" or not selectedTable.get():
        messagebox.showerror("Error", "Please select a valid table first")
        return

    window = tk.Toplevel(parent)
    window.title("Add Record")
    height = len(colnames) * 80 + 50
    window.geometry(f'300x{height}')
    window.configure(bg=mainBgColor)

    def addValues():
        values = [textField.get() for textField in textFields]
        keyString = f"({', '.join(colnames)})"
        result = addRecord(conn, selectedTable.get(), keyString, values)
        if result is None:
            table.insert('', tk.END, values=values)
            window.destroy()
        else:
            messagebox.showerror("Error", result)

    textFields = []
    mainFrame = tk.Frame(window, bg=mainBgColor)
    mainFrame.pack()
    for field in colnames:
        frame = tk.Frame(mainFrame, bg=mainBgColor)
        frame.pack()
        ttk.Label(frame, text=f'{field}:', background=mainBgColor).pack()
        textField = ttk.Entry(frame)
        textField.pack(pady=5)
        textFields.append(textField)

    tk.Button(window, text="Add", command=addValues, bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), pady=8,
              padx=10).pack(pady=5)


def createRemoveWindow(parent):
    global selectedElement
    if selectedElement is None or not table.exists(selectedElement):
        messagebox.showerror("Error", "Please select a row first")
        return

    values = table.item(selectedElement, 'values')
    paramString = ' AND '.join(f"{col} = '{val}'" for col, val in zip(colnames, values))
    result = deleteRecord(conn, selectedTable.get(), paramString)
    if result is None:
        table.delete(selectedElement)
        selectedElement = None
    else:
        messagebox.showerror("Error", result)


def createUpdateWindow(parent):
    global selectedElement, colnames
    if selectedElement is None or not table.exists(selectedElement):
        messagebox.showerror("Error", "Please select a row first")
        return

    logging.debug(f"Opening update window with colnames: {colnames}")
    window = tk.Toplevel(parent)
    window.title("Update Record")
    height = len(colnames) * 80 + 50
    window.geometry(f'300x{height}')
    window.configure(bg=mainBgColor)

    values = table.item(selectedElement, 'values')
    values = [None if str(val).lower() == "none" or val == "" else val for val in values]

    whereConditions = []
    whereValues = []
    for col, val in zip(colnames, values):
        if val is not None:
            whereConditions.append(f'"{col}" = %s')
            whereValues.append(val)

    if not whereConditions:
        messagebox.showwarning("Warning", "All columns are NULL. Update may affect multiple rows or fail.")
        whereConditions = [f'"{col}" IS NULL' for col in colnames]
        whereValues = []
        whereClause = ' AND '.join(whereConditions)
    else:
        whereClause = ' AND '.join(whereConditions)

    def updateValues():
        global selectedElement
        newValues = [textField.get() or None for textField in textFields]
        result, rowcount = updateRecord(conn, selectedTable.get(), colnames, newValues, whereClause, whereValues)
        if result is None:
            if rowcount > 1:
                messagebox.showwarning("Warning", f"Updated {rowcount} rows. Multiple rows matched the condition.")
            table.item(selectedElement, values=newValues)
            window.destroy()
            data, new_colnames = getTableData(conn, selectedTable.get())
            updateTable(data, new_colnames)
        else:
            messagebox.showerror("Error", result)

    textFields = []
    mainFrame = tk.Frame(window, bg=mainBgColor)
    mainFrame.pack()
    for field, value in zip(colnames, values):
        frame = tk.Frame(mainFrame, bg=mainBgColor)
        frame.pack()
        ttk.Label(frame, text=f'{field}:', background=mainBgColor).pack()
        textField = ttk.Entry(frame)
        textField.insert(0, value if value is not None else '')
        textField.pack(pady=5)
        textFields.append(textField)

    tk.Button(window, text="Update", command=updateValues, bg='#666666', fg='#333333', font=('Arial', 12, 'bold'),
              pady=8, padx=10).pack(pady=5)


def queryChoiceWindow(parent):
    window = tk.Toplevel(parent)
    window.title("Queries")
    window.geometry("400x600")
    window.configure(bg=mainBgColor)

    message_frame = tk.Frame(window, bg=mainBgColor)
    message_frame.pack(fill='x', pady=5)
    message_label = tk.Label(message_frame, text="", bg=mainBgColor, font=('Arial', 10))
    message_label.pack()

    notebook = ttk.Notebook(window)
    notebook.pack(fill='both', expand=True)

    tab_frames = {}

    for category in QUERIES:
        frame = tk.Frame(notebook, bg=mainBgColor)
        notebook.add(frame, text=category)
        tab_frames[category] = frame

        canvas = tk.Canvas(frame, bg=mainBgColor, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=mainBgColor)

        scrollable_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )

        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def resize_canvas(event, canvas=canvas, window_id=canvas_frame):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame.canvas = canvas
        frame.scrollable_frame = scrollable_frame

        populate_tab(category, frame)

    tk.Button(window, text="Add Custom Query",
              command=lambda: addCustomQueryWindow(window, notebook, tab_frames["Custom"], message_label),
              bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)
    tk.Button(window, text="Export Results", command=exportQueryResults, bg='#666666', fg='#333333',
              font=('Arial', 12, 'bold'), pady=8, padx=10).pack(pady=5)


def addCustomQueryWindow(parent, notebook, custom_frame, message_label):
    logging.debug("Opening addCustomQueryWindow")
    window = tk.Toplevel(parent)
    window.title("Add Custom Query")
    window.geometry("400x300")
    window.configure(bg=mainBgColor)

    ttk.Label(window, text="Query Name:", background=mainBgColor).pack(pady=5)
    name_entry = ttk.Entry(window, width=40)
    name_entry.pack(pady=5)

    ttk.Label(window, text="SQL Query:", background=mainBgColor).pack(pady=5)
    query_text = tk.Text(window, height=5, width=40)
    query_text.pack(pady=5)

    tk.Button(window, text="Save",
              command=lambda: saveCustomQuery(name_entry.get(), query_text.get("1.0", tk.END).strip(), window, notebook,
                                              custom_frame, message_label, parent),
              bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10).pack(pady=10)


def editCustomQueryWindow(parent, name, query, notebook, custom_frame, message_label):
    logging.debug(f"Opening editCustomQueryWindow for query: {name}")
    window = tk.Toplevel(parent)
    window.title(f"Edit Query: {name}")
    window.geometry("400x350")
    window.configure(bg=mainBgColor)

    ttk.Label(window, text="Query Name:", background=mainBgColor).pack(pady=5)
    name_entry = ttk.Entry(window, width=40)
    name_entry.insert(0, name)
    name_entry.pack(pady=5)

    ttk.Label(window, text="SQL Query:", background=mainBgColor).pack(pady=5)
    query_text = tk.Text(window, height=5, width=40)
    query_text.insert("1.0", query)
    query_text.pack(pady=5)

    button_frame = tk.Frame(window, bg=mainBgColor)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Save",
              command=lambda: updateCustomQuery(name, name_entry.get(), query_text.get("1.0", tk.END).strip(), window,
                                                notebook, custom_frame, message_label, parent),
              bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10).pack(side=tk.LEFT,
                                                                                                           padx=5)
    tk.Button(button_frame, text="Execute",
              command=lambda: [executeQuery(query_text.get("1.0", tk.END).strip()), window.destroy()],
              bg='#66cc66', fg='#333333', font=('Arial', 12, 'bold'), relief='flat', pady=8, padx=10).pack(side=tk.LEFT,
                                                                                                           padx=5)


def saveCustomQuery(name, query, window, notebook, custom_frame, message_label, root):
    logging.debug(f"saveCustomQuery called with name: {name}, query: {query}")
    if not name or not query:
        messagebox.showerror("Error", "Please provide both a name and a query")
        return
    QUERIES["Custom"].append((name, query))
    try:
        with open('custom_queries.json', 'w', encoding='utf-8') as f:
            json.dump(QUERIES["Custom"], f)
    except Exception as e:
        logging.error(f"Error writing custom_queries.json: {str(e)}")
        messagebox.showerror("Error", f"Failed to save query: {str(e)}")
        return

    def after_destroy():
        logging.debug("Executing after_destroy for saveCustomQuery")
        try:
            populate_tab("Custom", custom_frame)
            message_label.config(text=f"Custom query '{name}' added successfully!")
            root.after(2000, lambda: message_label.config(text=""))
        except Exception as e:
            logging.error(f"Error in after_destroy: {str(e)}")

    window.destroy()
    root.after(300, after_destroy)  # Use root.after and 300ms delay


def updateCustomQuery(old_name, new_name, new_query, window, notebook, custom_frame, message_label, root):
    logging.debug(f"updateCustomQuery called with old_name: {old_name}, new_name: {new_name}, new_query: {new_query}")
    if not new_name or not new_query:
        messagebox.showerror("Error", "Please provide both a name and a query")
        return
    QUERIES["Custom"] = [(n, q) for n, q in QUERIES["Custom"] if n != old_name]
    QUERIES["Custom"].append((new_name, new_query))
    try:
        with open('custom_queries.json', 'w', encoding='utf-8') as f:
            json.dump(QUERIES["Custom"], f)
    except Exception as e:
        logging.error(f"Error writing custom_queries.json: {str(e)}")
        messagebox.showerror("Error", f"Failed to save query: {str(e)}")
        return

    def after_destroy():
        logging.debug("Executing after_destroy for updateCustomQuery")
        try:
            populate_tab("Custom", custom_frame)
            message_label.config(text=f"Custom query '{new_name}' updated successfully!")
            root.after(2000, lambda: message_label.config(text=""))
        except Exception as e:
            logging.error(f"Error in after_destroy: {str(e)}")

    window.destroy()
    root.after(300, after_destroy)  # Use root.after and 300ms delay


def deleteCustomQuery(name, notebook, custom_frame):
    logging.debug(f"deleteCustomQuery called for name: {name}")
    QUERIES["Custom"] = [(n, q) for n, q in QUERIES["Custom"] if n != name]
    with open('custom_queries.json', 'w', encoding='utf-8') as f:
        json.dump(QUERIES["Custom"], f)
    populate_tab("Custom", custom_frame)
    messagebox.showinfo("Success", f"Custom query '{name}' deleted successfully!")


def executeQuery(query):
    global colnames
    data, colnames = runQuery(conn, query)
    updateTable(data, colnames)
    blockCRUD(True)
    selectedTable.set('Query Result')


def exportQueryResults():
    if colnames:
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            data = [table.item(item)['values'] for item in table.get_children()]
            exportToCSV(data, colnames, filename)


def updateTable(data, columns):
    global table, selectedElement
    table.delete(*table.get_children())
    selectedElement = None
    table['columns'] = list(range(len(columns)))

    for i, col in enumerate(columns):
        table.column(str(i), width=150, minwidth=100, stretch=tk.NO)
        table.heading(str(i), text=col)

    for i, record in enumerate(data):
        record = [val if val is not None else "" for val in record]
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        table.insert('', tk.END, values=record, tags=(tag,))


def blockCRUD(block):
    for button in CRUDbuttons:
        button.config(state=tk.DISABLED if block else tk.NORMAL)


def refreshTableList(parent):
    global selectedTable
    try:
        tables = getTables(conn)
        # Find the Combobox widget in the table choice frame
        for widget in parent.grid_slaves(row=0, column=0):
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        child['values'] = tables + ['---']
                        if selectedTable.get() not in tables and selectedTable.get() != '---':
                            selectedTable.set('---')
                        break
        logging.debug(f"Updated combobox values: {tables}")
    except Exception as e:
        logging.error(f"Error refreshing table list: {str(e)}")
        messagebox.showerror("Error", f"Failed to refresh table list: {str(e)}")


def onSelectElement(event):
    global selectedElement
    if selectedTable.get() != 'Query Result' and table.selection():
        selectedElement = table.selection()[0]
        logging.debug(f"Selected element: {selectedElement}")


def populate_tab(category, frame):
    scrollable_frame = frame.scrollable_frame
    canvas = frame.canvas

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    for name, query in QUERIES[category]:
        query_frame = tk.Frame(scrollable_frame, bg=mainBgColor)
        query_frame.pack(pady=2, fill='x')

        if category == "Custom":
            btn = tk.Button(query_frame, text=name,
                            command=lambda n=name, q=query: editCustomQueryWindow(frame.winfo_toplevel(), n, q,
                                                                                  frame.master, frame,
                                                                                  frame.winfo_toplevel().nametowidget(
                                                                                      '!frame').winfo_children()[0]),
                            bg='#666666', fg='#333333', font=('Arial', 12, 'bold'), width=30, anchor='w', pady=8,
                            padx=10)
            btn.pack(side=tk.LEFT)

            delete_btn = tk.Button(query_frame, text="Delete",
                                   command=lambda n=name: deleteCustomQuery(n, frame.master, frame),
                                   bg='#ff6666', fg='#333333', font=('Arial', 10), relief='flat', pady=4, padx=6)
            delete_btn.pack(side=tk.RIGHT)
        else:
            btn = tk.Button(query_frame, text=name, command=lambda q=query: executeQuery(q), bg='#666666',
                            fg='#333333', font=('Arial', 12, 'bold'), width=30, anchor='w', pady=8, padx=10)
            btn.pack(side=tk.LEFT)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


selectedElement = None
CRUDbuttons = []
conn = initConnection()
root, table, selectedTable = initWindow()
colnames = None

if os.path.exists('custom_queries.json'):
    with open('custom_queries.json', 'r', encoding='utf-8') as f:
        QUERIES["Custom"] = json.load(f)

root.mainloop()
