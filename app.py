import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

class OrderHistory:
    def __init__(self, root,customer_id,customer_name,customer_database):
        self.root = root
        self.customer_id=customer_id
        self.customer_name=customer_name
        self.customer_database=customer_database
        self.conn = sqlite3.connect('customer_database.db')  
        self.cursor = self.conn.cursor()
        self.orders=self.customer_database.orders 
        
        self.root.title("Order History of "+customer_name)
        self.root.geometry("1400x800")
        self.root.wm_state("zoomed")
        self.create_treeview()
        self.load_order_history()
        
    def on_closing(self):
        self.customer_database.reset_treeview()
        self.root.destroy()
    def create_treeview(self):
        self.treeview_frame = tk.Frame(self.root, bg="#FFECA1")
        self.treeview_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.treeview = ttk.Treeview(self.treeview_frame, columns=("Order ID","Name","Date", "Order", "Total amount","Paid"), show="headings")
        
        self.treeview.pack(fill="both", expand=True)
        self.treeview.bind("<Double-1>", self.update_order)

        self.treeview.heading("Order ID", text="Order ID")
        self.treeview.heading("Name", text="Name")
        self.treeview.heading("Date", text="Date")
        self.treeview.heading("Order", text="Order")
        self.treeview.heading("Total amount", text="Total amount")
        self.treeview.heading("Paid", text="Paid")

        self.treeview.column("Order ID", width=50, anchor="center")
        self.treeview.column("Name", width=50, anchor="center")
        self.treeview.column("Date", width=100, anchor="center")
        self.treeview.column("Order", width=900, anchor="w")
        self.treeview.column("Total amount", width=50, anchor="center")
        self.treeview.column("Paid", width=50, anchor="center")

        self.bottom = tk.Frame(self.root,bg="#FFECA1")
        self.bottom.pack(side="top",fill="both",expand=True,padx=10,pady=10)
        
        self.add_order_button = tk.Button(self.bottom,text="ADD ORDER",command=self.add_order_window,bg="#41EC03",fg="#FCFEFF",font=("Arial",10,"bold"))
        self.add_order_button.pack(side="top",padx=10,pady=10)
        self.add_order_button.focus_set()
        self.add_order_button.bind("<Return>",self.add_order_window)
        
        self.update_order_button = tk.Button(self.bottom,text="UPDATE ORDER",command=self.update_order,bg="#039EEC",fg="#FCFEFF",font=("Arial",10,"bold"))
        self.update_order_button.pack(side="top",padx=10,pady=10)
        
        self.search_name_entry = tk.Entry(self.bottom,font=("Arial",10,"bold"))
        self.search_name_entry.pack(fill="x",pady=10,padx=10)
        self.search_name_entry.bind("<Return>",self.search_name)
        
        self.reset_button = tk.Button(self.bottom,text="RESET",command=self.reset,bg="#039EEC",fg="#FCFEFF",font=("Arial",10,"bold"))
        self.reset_button.pack(side="top",padx=10,pady=10)
        
        self.delete_button = tk.Button(self.bottom,text="DELETE ORDER",command=self.delete_order,bg="#EC0303",fg="#FCFEFF",font=("Arial",10,"bold"))
        self.delete_button.pack(side="top",padx=10,pady=10)

        balance = self.customer_database.customers[int(self.customer_id)]["net_balance"]
        if balance < 0:
            color = "#41EC03"
        else:
            color = "#EC0303"
        self.balance_label = tk.Label(self.bottom, text=str(balance), bg=color, fg="#FCFEFF", font=("Arial", 14, "bold"))
        self.balance_label.pack(side="top", padx=10, pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.load_order_history()
    def update_balance_label(self):
        balance = self.customer_database.customers[int(self.customer_id)]["net_balance"]
        if balance < 0:
            color = "#41EC03"
        else:
            color = "#EC0303"
        self.balance_label.config(text=str(balance), bg=color)
    def add_order_window(self,event=True):
        self.order_details_window = tk.Toplevel(self.root)
        self.order_details_window.title("Add Order")
        self.order_details_window.geometry("800x300") 
        self.order_details_window.transient(self.root)
        self.order_details_window.grab_set()
        
        tk.Label(self.order_details_window, text="Name:",font=("Arial",14,"bold")).grid(row=0, column=0,padx=5,pady=5)
        
        self.name_entry = tk.Entry(self.order_details_window,font=("Arial",14,"bold"),width=50)
        self.name_entry.grid(row=0, column=1,padx=5,pady=5)
        self.name_entry.focus_set()
        
        tk.Label(self.order_details_window, text="Order String:",font=("Arial",14,"bold")).grid(row=1, column=0,padx=5,pady=5)
        self.order_string_entry = tk.Entry(self.order_details_window,font=("Arial",14,"bold"),width=50)
        self.order_string_entry.grid(row=1, column=1,padx=5,pady=5)

        tk.Label(self.order_details_window, text="Total Amount:",font=("Arial",14,"bold")).grid(row=2, column=0,padx=5,pady=5)
        self.total_amount_entry = tk.Entry(self.order_details_window,font=("Arial",14,"bold"),width=50)
        self.total_amount_entry.grid(row=2, column=1,padx=5,pady=5)
        
        tk.Label(self.order_details_window, text="Paid Amount:",font=("Arial",14,"bold")).grid(row=3, column=0,padx=5,pady=5)
        self.amount_paid_entry = tk.Entry(self.order_details_window,font=("Arial",14,"bold"),width=50)
        self.amount_paid_entry.grid(row=3, column=1,padx=5,pady=5)
        self.amount_paid_entry.bind("<Return>",lambda event: self.save_button.focus_set())
        
        self.save_button = tk.Button(self.order_details_window, text="Save", command=self.add_order_db,width=10,font=("Arial",14,"bold"))
        self.save_button.grid(row=4, column=0, columnspan=2,padx=5,pady=5)
        self.save_button.bind("<KeyRelease-Return>",lambda event: self.save_button.invoke())

    def add_order_db(self):
        # Create a new order
        name = self.name_entry.get()
        order_date = datetime.date.today()
        order_date = order_date.strftime("%d-%m-%Y")
        total_amount = self.total_amount_entry.get()
        amount_paid = self.amount_paid_entry.get()
        order_string = self.order_string_entry.get()
            
        # Insert the new order into the database
        self.cursor.execute("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            last_order_id = result[0]
            self.orderid = last_order_id + 1
        else:
            self.orderid = 1
        self.cursor.execute("INSERT INTO orders (order_id, name,order_date, customer_id,order_string,total,paid) VALUES (?,?,?,?,?,?,?)", (self.orderid,name,order_date,self.customer_id,order_string,int(total_amount),int(amount_paid)))
        self.conn.commit()
        
        self.cursor.execute("UPDATE customers SET net_balance = net_balance +? WHERE customer_id =?", (float(total_amount)-float(amount_paid), self.customer_id))        
        self.conn.commit()
        
        self.orders[self.orderid] = {"name":name, "order_date":order_date,"order_string":order_string,"total":int(total_amount),"paid":int(amount_paid)}
        self.customer_database.customers[int(self.customer_id)]["net_balance"] += float(total_amount)-float(amount_paid)
        print("Order added successfully!")
        # Refresh the order history treeview
        self.order_details_window.destroy()
        self.load_order_history()
        self.update_balance_label()

    def update_order(self,event=True):
        selected_order = self.treeview.selection()[0]
        self.order_id = self.treeview.item(selected_order,"values")[0]
        if self.treeview.item(selected_order,"values")[1]:
            self.cust_name = self.treeview.item(selected_order,"values")[1]
        else:
            self.cust_name=""
        self.order_string = self.treeview.item(selected_order,"values")[3]
        self.total_amount = self.treeview.item(selected_order,"values")[4]
        self.amount_paid = self.treeview.item(selected_order,"values")[5]
        
        self.update_window = tk.Toplevel(self.root)
        self.update_window.title("Update Order")
        self.update_window.transient(self.root)
        self.update_window.grab_set()
        
        self.update_frame = tk.Frame(self.update_window,bg="#f0f0f0")
        self.update_frame.pack(fill="both",expand=True, padx=10, pady=10)
        
        tk.Label(self.update_frame, text="Name:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=0, column=0, padx=5, pady=5)
        self.update_name_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14,"bold"))
        self.update_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.update_name_entry.insert(0,self.cust_name)
        self.update_name_entry.focus_set()
        self.update_name_entry.bind("<Return>",lambda event: self.update_button.invoke())
        
        tk.Label(self.update_frame, text="Order:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=1, column=0, padx=5, pady=5)
        self.update_order_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14,"bold"))
        self.update_order_entry.grid(row=1, column=1, padx=5, pady=5)
        self.update_order_entry.insert(0,self.order_string)
        self.update_order_entry.bind("<Return>",lambda event: self.update_button.invoke())
        
        tk.Label(self.update_frame, text="Total Amount:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=2, column=0, padx=5, pady=5)
        self.update_total_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14,"bold"))
        self.update_total_entry.grid(row=2, column=1, padx=5, pady=5)
        self.update_total_entry.insert(0,self.total_amount)
        self.update_total_entry.bind("<Return>",lambda event: self.update_button.invoke())
        
        tk.Label(self.update_frame, text="Paid Amount:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=3, column=0, padx=5, pady=5)
        self.update_paid_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14,"bold"))
        self.update_paid_entry.grid(row=3, column=1, padx=5, pady=5)
        self.update_paid_entry.insert(0,self.amount_paid)
        self.update_paid_entry.bind("<Return>",lambda event: self.update_button.invoke())
        
        self.update_button = tk.Button(self.update_frame,text="Update",command=lambda: self.update_order_from_window(self.order_id,self.total_amount,self.amount_paid),bg="#6c757d",fg="white",font=("Arial",14,"bold"))
        self.update_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.update_button.bind("<KeyRelease-Return>",lambda event: self.update_button.invoke())
          
    def update_order_from_window(self,order_id,prev_total,prev_paid):
        cust_name = self.update_name_entry.get()
        order_string = self.update_order_entry.get()
        total_amount = self.update_total_entry.get()
        paid_amount = self.update_paid_entry.get()
        
        if order_string and total_amount and paid_amount and cust_name:
            self.cursor.execute("UPDATE orders SET name=?,order_string=?, total=?, paid=? WHERE order_id=?",(cust_name,order_string,total_amount,paid_amount,order_id))
            self.conn.commit()
            self.cursor.execute("UPDATE customers SET net_balance = net_balance +? WHERE customer_id=?",(float(total_amount)-float(paid_amount) -(float(prev_total)-float(prev_paid)),self.customer_id))
            self.conn.commit()
            self.orders[int(order_id)]["name"] = cust_name
            self.customer_database.customers[int(self.customer_id)]["net_balance"] += float(total_amount)-float(paid_amount) -(float(prev_total)-float(prev_paid))
            self.update_window.destroy()
            self.update_balance_label()
            self.load_order_history()
        else:
            messagebox.showerror("Error", "Please fill in all fields")
            self.update_window.lift()
            self.update_window.focus_force()
            
    def delete_order(self):
        # Get the selected order from the treeview
        selected_order = self.treeview.selection()[0]
        order_id = self.treeview.item(selected_order, "values")[0]

        # Delete the order from the database
        self.cursor.execute("DELETE FROM orders WHERE order_id =?", (order_id,))
        self.conn.commit()
        del self.orders[int(order_id)]
        self.treeview.delete(selected_order)
        # Refresh the order history treeview
        self.load_order_history()

    def load_order_history(self):
        self.treeview.delete(*self.treeview.get_children())

        orders1 = self.get_order_history(self.customer_id)

        for order in orders1:
            self.treeview.insert("", "0", values=order)
            self.orders[order[0]] = {"name": order[1], "order_date": order[2], "order_string": order[3], "total": order[4], "paid": order[5]}
        self.alternate_colors()
        
    def alternate_colors(self):
        for i,item in enumerate(self.treeview.get_children()):
            if i%2==0:
                self.treeview.item(item, tag="even")
            else:
                self.treeview.item(item,tags="odd")
        self.treeview.tag_configure("even", background="#f0f0f0")
        self.treeview.tag_configure("odd", background="#e0e0e0")
    def search_name(self,event=True):
        self.treeview.delete(*self.treeview.get_children())
        print(len(self.orders))
        search_term = self.search_name_entry.get().lower()
        orders1 = self.get_order_history(self.customer_id)
        for order in orders1:
            if order[1] and search_term in order[1].lower():
                self.treeview.insert("", "0", values=(order))
        
        self.alternate_colors()
    def get_order_history(self,customer_id):
        self.cursor.execute("SELECT order_id,name, order_date, order_string, total, paid FROM orders WHERE customer_id = ?", (customer_id,))
        orders = self.cursor.fetchall()
        return orders
    def reset(self):
        self.load_order_history()
class CustomerDatabase:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Arial", 12))
        self.root.title("Customer Database")
        self.root.attributes("-fullscreen", True)
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True)

        self.create_widgets()

        self.conn = sqlite3.connect("customer_database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS customers (customer_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, net_balance INTEGER, phone TEXT, address TEXT)")
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS orders ( order_id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT, customer_id INTEGER ,order_date DATE, order_string TEXT, total REAL,paid REAL, FOREIGN KEY (customer_id) REFERENCES customers(customer_id))''')
        print("Table created successfully!")
        self.conn.commit()
        self.customer_id = 1
        self.customers = {}
        self.orders = {}

        self.load_data_from_database()
        self.tree.bind("<Double-1>", self.treeview_double_click)
        self.tree.bind("<Return>", self.treeview_double_click)
    def minimize_window(self):
        self.root.withdraw()  # if you want to bring it back
        self.root.iconify()  # if you want to keep the window in the taskbar
    def create_widgets(self):
        self.top_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.top_frame.pack(fill="x")

        self.quit_button = tk.Button(self.top_frame, text="Quit", command=self.root.destroy, bg="#dc3545", fg="white")
        self.quit_button.pack(side="top", padx=10,pady=(3,0))
        

        self.tree_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.tree_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Name", "Net Balance", "Phone", "Address"), show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        self.vscrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vscrollbar.set)
        self.vscrollbar.pack(side="right", fill="y")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Net Balance", text="Net Balance")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Address", text="Address")

        self.tree.column("ID", width=20, anchor="center")
        self.tree.column("Name", width=560, anchor="center")
        self.tree.column("Net Balance", width=20, anchor="center")
        self.tree.column("Phone", width=50, anchor="center")
        self.tree.column("Address", width=70, anchor="center")
        

        self.form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.form_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.clear_button = tk.Button(self.form_frame, text="Clear", command=self.clear_entries, bg="#6c757d", fg="white")
        self.clear_button.pack(fill="x", pady=10)
        self.clear_button.config(font=("Arial", 12, "bold"))
        
        self.search_label = tk.Label(self.form_frame, text="Search", bg="#f0f0f0")
        self.search_label.pack(fill="x", pady=10)
        self.search_label.config(font=("Arial", 12, "bold"))

        self.search_entry = tk.Entry(self.form_frame, width=30)
        self.search_entry.pack(fill="x", pady=10)
        self.search_entry.config(font=("Arial,12"))
        self.search_entry.bind("<Return>", lambda event : self.search_customer())
        self.search_entry.focus_set()
        
        
        self.add_button = tk.Button(self.form_frame, text="Add Customer", command=self.add_customer_window, bg="#28a745", fg="white")
        self.add_button.pack(fill="x", pady=10)
        self.add_button.config(font=("Arial", 12, "bold"))
        
        self.update_button = tk.Button(self.form_frame, text="Update Customer", command=self.update_customer_window, bg="#007bff", fg="white")
        self.update_button.pack(fill="x", pady=10)
        self.update_button.config(font=("Arial", 12, "bold"))

        self.delete_button = tk.Button(self.form_frame, text="Delete Customer", command=self.delete_customer, bg="#dc3545", fg="white")
        self.delete_button.pack(fill="x", pady=10)
        self.delete_button.config(font=("Arial", 12, "bold"))

        self.reset_button = tk.Button(self.form_frame, text="Reset", command=self.reset_treeview, bg="#6c757d", fg="white")
        self.reset_button.pack(fill="x", pady=10)
        self.reset_button.config(font=("Arial", 12, "bold"))
        
        self.sort_button = tk.Button(self.form_frame, text="Sort", command=self.sort_treeview, bg="#6c757d", fg="white")
        self.sort_button.pack(fill="x", pady=10)
        self.sort_button.config(font=("Arial", 12, "bold"))
        
        self.minimise_button = tk.Button(self.form_frame, text="Minimise", command=self.minimize_window, bg="#dc3545", fg="white")
        self.minimise_button.pack( padx=10,pady=10)
        self.minimise_button.config(font=("Arial", 12, "bold"))

    def load_data_from_database(self):
        self.cursor.execute("SELECT * FROM customers")
        rows = self.cursor.fetchall()

        for row in rows:
            self.tree.insert("", "0", values=row)
            self.customers[row[0]] = {"name": row[1], "net_balance": row[2], "phone": row[3], "address":row[4]}
            self.customer_id = row[0] + 1

    def add_customer_window(self):
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Customer")
        self.add_window.geometry("800x300")
        self.add_window.grab_set()
        self.add_window.transient(self.root)
        
        self.name_label = tk.Label(self.add_window, text="Name:", bg="#f0f0f0",font=("Arial",14,"bold"))
        self.name_label.pack(fill="x", pady=10)
        self.name_label.grid(row=0,column=0,padx=5,pady=5)

        self.name_entry = tk.Entry(self.add_window, width=50,font=("Arial",14))
        self.name_entry.grid(row=0,column=1,padx=5,pady=5)
        self.name_entry.focus_set()
        
        self.phone_label = tk.Label(self.add_window, text="Phone:", bg="#f0f0f0",font=("Arial",14,"bold"))
        self.phone_label.grid(row=1,column=0,padx=5,pady=5)
        
        self.phone_entry = tk.Entry(self.add_window, width=50,font=("Arial",14))
        self.phone_entry.grid(row=1,column=1,padx=5,pady=5)
        self.phone_entry.bind('<Return>', lambda event: self.submit_button.focus_set())
        

        self.balance_label = tk.Label(self.add_window, text="Net Balance:", bg="#f0f0f0",font=("Arial",14,"bold"))
        self.balance_label.grid(row=2,column=0,padx=5,pady=5)
        

        self.balance_entry = tk.Entry(self.add_window, width=50,font=("Arial",14))
        self.balance_entry.grid(row=2,column=1,padx=5,pady=5)
        
        
        self.address_label = tk.Label(self.add_window, text="Address", bg="#f0f0f0",font=("Arial",14,"bold"))
        self.address_label.grid(row=3,column=0,padx=5,pady=5)
        

        self.address_entry = tk.Entry(self.add_window, width=50,font=("Arial",14))
        self.address_entry.grid(row=3,column=1,padx=5,pady=5)
        self.address_entry.bind('<Return>', lambda event: self.submit_button.focus_set())

        self.submit_button = tk.Button(self.add_window, text="Submit", command=self.add_customer_from_window, bg="#007bff", fg="white")
        self.submit_button.grid(row=4,column=0,columnspan=2,padx=5,pady=5)
        self.submit_button.bind("<KeyRelease-Return>",lambda event: self.submit_button.invoke())


    def add_customer_from_window(self,event=True):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        if self.address_entry.get():
            address=self.address_entry.get()
        else:
            address=""
        if self.balance_entry.get():
            balance = self.balance_entry.get()
        else:
            balance=0
            
        if name and phone:
            self.cursor.execute("INSERT INTO customers (name, net_balance, phone,address) VALUES (?,?,?,?)", (name, int(balance), phone,address))
            self.conn.commit()

            self.tree.insert("", "0", values=(self.customer_id, name, int(balance), phone,address))
            self.customers[self.customer_id] = {"name": name, "net_balance": int(balance), "phone": phone, "address": address}
            self.customer_id += 1

            self.name_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.balance_entry.delete(0, "end")
            self.address_entry.delete(0, "end")

            self.add_window.destroy()
            self.reset_treeview()

    def update_customer_window(self):
        selected_item = self.tree.selection()[0]
        customer_id = self.tree.item(selected_item, "values")[0]
        
        self.update_window = tk.Toplevel(self.root)
        self.update_window.title("Update Customer")
        self.update_window.grab_set()
        self.update_window.transient(self.root)
        self.update_window.geometry("800x300")
        self.update_frame = tk.Frame(self.update_window, bg="#f0f0f0")
        self.update_frame.pack(fill="both", expand=True)
        customer = self.customers[int(customer_id)]

        tk.Label(self.update_frame, text="Name:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=0, column=0, padx=5, pady=5)
        self.update_name_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14))
        self.update_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.update_name_entry.insert(0, customer["name"])
        self.update_name_entry.focus_set()
        
        tk.Label(self.update_frame, text="Net Balance:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=1, column=0, padx=5, pady=5)
        self.update_net_balance_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14))
        self.update_net_balance_entry.grid(row=1, column=1, padx=5, pady=5)
        self.update_net_balance_entry.insert(0, customer["net_balance"])

        tk.Label(self.update_frame, text="Phone:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=2, column=0, padx=5, pady=5)
        self.update_phone_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14))
        self.update_phone_entry.grid(row=2, column=1, padx=5, pady=5)
        self.update_phone_entry.insert(0, customer["phone"])
        
        tk.Label(self.update_frame, text="Address:", bg="#f0f0f0",font=("Arial",14,"bold")).grid(row=3, column=0, padx=5, pady=5)
        self.update_address_entry = tk.Entry(self.update_frame, width=50,font=("Arial",14))
        self.update_address_entry.grid(row=3, column=1, padx=5, pady=5)
        if customer["address"]:
            self.update_address_entry.insert(0, customer["address"])

        self.update_button = tk.Button(self.update_frame, text="Update", command=lambda: self.update_customer_from_window(customer_id), bg="#6c757d", fg="white")
        self.update_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def update_customer_from_window(self, customer_id):
        name = self.update_name_entry.get()
        net_balance = self.update_net_balance_entry.get()
        phone = self.update_phone_entry.get()
        address = self.update_address_entry.get()

        if name and net_balance and phone and address:
            self.cursor.execute("UPDATE customers SET name=?, net_balance=?, phone=?, address=? WHERE customer_id=?", (name, net_balance, phone,address, customer_id))
            self.conn.commit()
            self.load_data_from_database()
            self.update_window.destroy()
            self.reset_treeview()
        else:
            messagebox.showerror("Error", "Please fill in all fields")
            self.update_window.lift()
            self.update_window.focus_force()
            
    def delete_customer(self):
        if self.tree.selection():
            selected_item = self.tree.selection()[0]
            customer_id = self.tree.item(selected_item, "values")[0]
            
            confirm_dialog = tk.Toplevel(self.root)
            confirm_dialog.title("Confirm Deletion")
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            dialog_width = 500
            dialog_height = 200
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
            confirm_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            label = tk.Label(confirm_dialog, text=f"Are you sure you want to delete customer {customer_id}?")
            label.config(font=("Arial", 12, "bold"))
            label.pack()
            
            yes_button = tk.Button(confirm_dialog, text="Yes", command=lambda: self.delete_customer_confirm(customer_id, confirm_dialog),width=10,anchor="center",padx=5)
            yes_button.pack(side=tk.LEFT,padx=5)
            
            no_button = tk.Button(confirm_dialog, text="No", command=confirm_dialog.destroy,width=10,anchor="center",padx=5)
            no_button.pack(side=tk.RIGHT,padx=5)
        else:
            messagebox.showerror("Error", "No customer selected")

    def delete_customer_confirm(self, customer_id, dialog):
        self.tree.delete(self.tree.selection())
        del self.customers[int(customer_id)]
        self.cursor.execute("DELETE FROM customers WHERE customer_id =?",(customer_id,))
        
        self.conn.commit()
        print("Deleted customer")
        dialog.destroy()
    def search_customer(self):
        self.tree.delete(*self.tree.get_children())
        
        search_term = self.search_entry.get().lower()
        items = []
        item_ids = []
        for customer_id, customer in self.customers.items():
            if search_term in customer["name"].lower():
                item = self.tree.insert("", "0", values=(customer_id, customer["name"], customer["net_balance"], customer["phone"], customer["address"]))
                items.append((customer_id, customer["name"], customer["net_balance"], customer["phone"], customer["address"]))
                item_ids.append(item)
        
        if items:
            self.tree.focus_set()
            self.tree.focus(item_ids[0])  # Set focus to the first item
            self.tree.selection_set(item_ids[0])  # Select the first item

        
        self.alternate_colors()
    def clear_entries(self):    
        self.search_entry.delete(0,"end")
        self.reset_treeview()

    def reset_treeview(self):
        self.tree.delete(*self.tree.get_children())
        self.load_data_from_database()
    
        if self.search_entry.get():
            self.search_customer()
        self.alternate_colors()

    def alternate_colors(self):
        for i, item in enumerate(self.tree.get_children()):
            if i % 2 == 0:
                self.tree.item(item, tag="even")
            else:
                self.tree.item(item, tag="odd")

        self.tree.tag_configure("even", background="#f0f0f0")
        self.tree.tag_configure("odd", background="#e0e0e0")

    def sort_treeview(self):
        # Get the customer data from the Treeview
        customer_data = []
        for child in self.tree.get_children():
            customer_data.append(self.tree.item(child, 'values'))

        # Sort the customer data by balance
        customer_data.sort(key=lambda x: float(x[2]),reverse=True)

        # Clear the Treeview
        self.tree.delete(*self.tree.get_children())

        # Insert the sorted customer data into the Treeview
        for customer in customer_data:
            self.tree.insert("", "end", values=customer)

        # Alternate the row colors
        self.alternate_colors()
            
    def treeview_double_click(self, event):
        selected_item = self.tree.selection()[0]
        customer_id = self.tree.item(selected_item, "values")[0]
        customer_name = self.tree.item(selected_item, "values")[1]

        order_history_window = tk.Toplevel(self.root)
        OrderHistory(order_history_window, customer_id, customer_name,self)
    def run(self):
        self.alternate_colors() 
        self.root.mainloop()
    
if __name__ == "__main__":
    root = tk.Tk()
    app = CustomerDatabase(root)
    app.run()
