from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    Numeric, Date, DateTime, ForeignKey, UniqueConstraint, 
    CheckConstraint, Index, func, JSON 
)
from sqlalchemy.orm import relationship

# استيراد الـ Base المشترك من ملف الجلسة لربط الجداول بالـ Engine الحقيقي
from database.session import Base 


# =========================================================
# 1. ROLES
# =========================================================
class Role(Base):
    __tablename__ = 'roles'
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="role")
    


# =========================================================
# 2. USERS
# =========================================================
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.role_id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    full_name = Column(String(150), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    purchase_orders = relationship("PurchaseOrder", back_populates="user")
    sales_invoices = relationship("SalesInvoice", back_populates="user")
    stock_movements = relationship("StockMovement", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    sales_returns = relationship("SalesReturn",back_populates="user")
    expired_medicines = relationship("ExpiredMedicine",back_populates="user")
    purchase_returns = relationship(
    "PurchaseReturn",
    back_populates="user")

Index('idx_users_role_id', User.role_id)
Index('idx_users_is_active', User.is_active)


# =========================================================
# 3. CATEGORIES
# =========================================================
class Category(Base):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    medicines = relationship("Medicine", back_populates="category")


# =========================================================
# 4. MANUFACTURERS
# =========================================================
class Manufacturer(Base):
    __tablename__ = 'manufacturers'
    
    manufacturer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    contact_email = Column(String(150))
    contact_phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    medicines = relationship("Medicine", back_populates="manufacturer")


# =========================================================
# 5. SUPPLIERS
# =========================================================
class Supplier(Base):
    __tablename__ = 'suppliers'
    
    supplier_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(150))
    address = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    batches = relationship("MedicineBatch", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

Index('idx_suppliers_name', Supplier.name)
Index('idx_suppliers_is_active', Supplier.is_active)


# =========================================================
# 6. MEDICINES
# =========================================================
class Medicine(Base):
    __tablename__ = 'medicines'

    medicine_id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name = Column(String(150), nullable=False)
    commercial_name = Column(String(150), nullable=False)
    barcode = Column(String(50), nullable=False, unique=True)

    # NEW
    rxcui = Column(String(50), unique=True)

    description = Column(Text)
    dosage_form = Column(String(50))
    requires_prescription = Column(Boolean, nullable=False, default=False)
    category_id = Column(Integer, ForeignKey('categories.category_id', onupdate='CASCADE', ondelete='SET NULL'))
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.manufacturer_id', onupdate='CASCADE', ondelete='SET NULL'))
    selling_price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            'selling_price >= 0',
            name='ck_medicines_selling_price'
        ),
        CheckConstraint(
            "dosage_form IS NULL OR dosage_form IN ('TABLET','CAPSULE','SYRUP','INJECTION','OINTMENT','DROPS','CREAM','POWDER','OTHER')",
            name='ck_medicines_dosage_form'
        ),
    )

    category = relationship("Category", back_populates="medicines")
    manufacturer = relationship("Manufacturer", back_populates="medicines")
    batches = relationship("MedicineBatch", back_populates="medicine")
    inventory = relationship("Inventory", back_populates="medicine", uselist=False)
    purchase_items = relationship("PurchaseItem", back_populates="medicine")
    sale_items = relationship("SaleItem", back_populates="medicine")
    notifications = relationship("Notification", back_populates="medicine")
    prescription_items = relationship("PrescriptionItem", back_populates="medicine")

  

Index('idx_medicines_rxcui', Medicine.rxcui)
# =========================================================
# 7. MEDICINE_BATCHES
# =========================================================
class MedicineBatch(Base):
    __tablename__ = 'medicine_batches'

    batch_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(
        Integer,
        ForeignKey('medicines.medicine_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    supplier_id = Column(
        Integer,
        ForeignKey('suppliers.supplier_id', onupdate='CASCADE', ondelete='SET NULL')
    )

    # رقم الباتش القادم من الشركة المصنعة
    batch_number = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    manufacture_date = Column(Date)
    expiry_date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint('quantity >= 0', name='ck_batches_quantity_non_negative'),
        CheckConstraint('purchase_price >= 0', name='ck_batches_purchase_price'),
        CheckConstraint('selling_price >= 0', name='ck_batches_selling_price'),
        CheckConstraint('manufacture_date IS NULL OR manufacture_date < expiry_date', name='ck_batches_dates'),
    )

    # Relationships
    medicine = relationship("Medicine", back_populates="batches")
    supplier = relationship("Supplier", back_populates="batches")
    purchase_items = relationship("PurchaseItem", back_populates="batch")
    sale_items = relationship("SaleItem", back_populates="batch")
    stock_movements = relationship("StockMovement", back_populates="batch")
    notifications = relationship("Notification", back_populates="batch")


# Indexes
Index('idx_batches_medicine_id', MedicineBatch.medicine_id)
Index('idx_batches_supplier_id', MedicineBatch.supplier_id)
Index('idx_batches_expiry_date', MedicineBatch.expiry_date)
Index('idx_batches_batch_number', MedicineBatch.batch_number)

# =========================================================
# 8. INVENTORY
# =========================================================
class Inventory(Base):
    __tablename__ = 'inventory'
    
    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicines.medicine_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=False, default=0)
    location = Column(String(100))
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('quantity >= 0', name='ck_inventory_quantity_non_negative'),
        CheckConstraint('min_stock_level >= 0', name='ck_inventory_min_stock_non_negative'),
    )

    medicine = relationship("Medicine", back_populates="inventory")

Index('idx_inventory_quantity', Inventory.quantity)


# =========================================================
# 9. CUSTOMERS
# =========================================================
class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150))
    phone = Column(String(20))
    email = Column(String(150))
    loyalty_points = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    sales_invoices = relationship("SalesInvoice", back_populates="customer")
    prescriptions = relationship("Prescription", back_populates="customer")

Index('idx_customers_phone', Customer.phone)
Index('idx_customers_email', Customer.email)


# =========================================================
# 10. PURCHASE_ORDERS
# =========================================================
class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    
    purchase_id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.supplier_id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', onupdate='CASCADE', ondelete='SET NULL'))
    order_date = Column(Date, nullable=False, server_default=func.current_date())
    received_date = Column(Date)
    status = Column(String(20), nullable=False, default='PENDING')
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('PENDING','RECEIVED','CANCELLED')", name='ck_purchase_orders_status'),
        CheckConstraint('total_amount >= 0', name='ck_purchase_orders_total_amount'),
        CheckConstraint('received_date IS NULL OR received_date >= order_date', name='ck_purchase_orders_received_date'),
    )

    supplier = relationship("Supplier", back_populates="purchase_orders")
    user = relationship("User", back_populates="purchase_orders")
    purchase_items = relationship("PurchaseItem",back_populates="purchase_order",cascade="all, delete-orphan",passive_deletes=True)
    purchase_returns = relationship("PurchaseReturn",back_populates="purchase",cascade="all, delete-orphan")

Index('idx_purchase_orders_supplier', PurchaseOrder.supplier_id)
Index('idx_purchase_orders_user', PurchaseOrder.user_id)
Index('idx_purchase_orders_order_date', PurchaseOrder.order_date)
Index('idx_purchase_orders_status', PurchaseOrder.status)

# =========================================================
# PURCHASE_ITEMS
# =========================================================
class PurchaseItem(Base):
    __tablename__ = 'purchase_items'

    purchase_item_id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(
        Integer, 
        ForeignKey('purchase_orders.purchase_id', onupdate='CASCADE', ondelete='CASCADE'), 
        nullable=False
    )
    medicine_id = Column(
        Integer, 
        ForeignKey('medicines.medicine_id', onupdate='CASCADE', ondelete='RESTRICT'), 
        nullable=False
    )
    batch_id = Column(
        Integer, 
        ForeignKey('medicine_batches.batch_id', onupdate='CASCADE', ondelete='SET NULL')
    )

    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    
    batch_number = Column(String(50), nullable=False)
    manufacture_date = Column(Date)
    expiry_date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        # منع تكرار نفس الدواء بنفس رقم الباتش داخل نفس طلب الشراء
        UniqueConstraint('purchase_id', 'medicine_id', 'batch_number', name='uq_purchase_item_batch'),
        
        CheckConstraint('quantity > 0', name='ck_purchase_items_quantity_positive'),
        CheckConstraint('unit_cost >= 0', name='ck_purchase_items_unit_cost'),
        CheckConstraint('selling_price >= 0', name='ck_purchase_items_selling_price'),
        CheckConstraint('subtotal >= 0', name='ck_purchase_items_subtotal'),
        CheckConstraint('manufacture_date IS NULL OR manufacture_date < expiry_date', name='ck_purchase_items_dates'),
    )

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="purchase_items")
    medicine = relationship("Medicine", back_populates="purchase_items")
    batch = relationship("MedicineBatch", back_populates="purchase_items")
    purchase_returns = relationship("PurchaseReturnItem", back_populates="purchase_item")


# =========================================================
# 12. SALES_INVOICES
# =========================================================
class SalesInvoice(Base):
    __tablename__ = 'sales_invoices'

    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(30), nullable=False, unique=True)
    user_id = Column(
        Integer,
        ForeignKey(
            'users.user_id',
            onupdate='CASCADE',
            ondelete='RESTRICT'
        ),
        nullable=False
    )
    customer_id = Column(
        Integer,
        ForeignKey(
            'customers.customer_id',
            onupdate='CASCADE',
            ondelete='SET NULL'
        )
    )
    sale_date = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    total_amount = Column(
        Numeric(12, 2),
        nullable=False
    )
    discount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )
    payment_method = Column(
        String(20),
        nullable=False,
        default='CASH'
    )
    status = Column(
        String(20),
        nullable=False,
        default='DRAFT'
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "payment_method IN ('CASH','CARD','INSURANCE','OTHER')",
            name='ck_sales_invoices_payment_method'
        ),
        CheckConstraint(
            "status IN ('DRAFT','COMPLETED','CANCELLED','REFUNDED')",
            name='ck_sales_invoices_status'
        ),
        CheckConstraint(
            'total_amount >= 0',
            name='ck_sales_invoices_total_amount'
        ),
        CheckConstraint(
            'discount >= 0',
            name='ck_sales_invoices_discount'
        ),
    )

    sales_returns = relationship(
        "SalesReturn",
        back_populates="invoice"
    )

    user = relationship(
        "User",
        back_populates="sales_invoices"
    )

    customer = relationship(
        "Customer",
        back_populates="sales_invoices"
    )

    sale_items = relationship(
        "SaleItem",
        back_populates="sales_invoice"
    )


Index(
    'idx_sales_invoices_user',
    SalesInvoice.user_id
)

Index(
    'idx_sales_invoices_customer',
    SalesInvoice.customer_id
)

Index(
    'idx_sales_invoices_sale_date',
    SalesInvoice.sale_date
)

Index(
    'idx_sales_invoices_status',
    SalesInvoice.status
)

# =========================================================
# 13. SALE_ITEMS
# =========================================================
class SaleItem(Base):
    __tablename__ = 'sale_items'
    
    sale_item_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('sales_invoices.invoice_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicines.medicine_id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    batch_id = Column(Integer, ForeignKey('medicine_batches.batch_id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_sale_items_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='ck_sale_items_unit_price'),
        CheckConstraint('subtotal >= 0', name='ck_sale_items_subtotal'),
    )

    sales_invoice = relationship("SalesInvoice", back_populates="sale_items")
    medicine = relationship("Medicine", back_populates="sale_items")
    batch = relationship("MedicineBatch", back_populates="sale_items")

Index('idx_sale_items_invoice', SaleItem.invoice_id)
Index('idx_sale_items_medicine', SaleItem.medicine_id)
Index('idx_sale_items_batch', SaleItem.batch_id)


# =========================================================
# 14. STOCK_MOVEMENTS
# =========================================================
class StockMovement(Base):
    __tablename__ = 'stock_movements'
    
    movement_id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey('medicine_batches.batch_id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    movement_type = Column(String(20), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    reference_type = Column(String(20), nullable=False)
    reference_id = Column(Integer)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey('users.user_id', onupdate='CASCADE', ondelete='SET NULL'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("movement_type IN ('PURCHASE','SALE','ADJUSTMENT','RETURN','DAMAGE','EXPIRED')", name='ck_stock_movements_type'),
        CheckConstraint("reference_type IN ('PURCHASE','SALE','RETURN','EXPIRED','ADJUSTMENT')", name='ck_stock_movements_reference_type'),
        CheckConstraint('quantity_change <> 0', name='ck_stock_movements_quantity_nonzero'),
    )

    batch = relationship("MedicineBatch", back_populates="stock_movements")
    user = relationship("User", back_populates="stock_movements")

Index('idx_stock_movements_batch', StockMovement.batch_id)
Index('idx_stock_movements_type', StockMovement.movement_type)
Index('idx_stock_movements_reference', StockMovement.reference_type, StockMovement.reference_id)
Index('idx_stock_movements_created_at', StockMovement.created_at)


# =========================================================
# 15. NOTIFICATIONS
# =========================================================
class Notification(Base):
    __tablename__ = 'notifications'
    
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicines.medicine_id', onupdate='CASCADE', ondelete='CASCADE'))
    batch_id = Column(Integer, ForeignKey('medicine_batches.batch_id', onupdate='CASCADE', ondelete='CASCADE'))
    message = Column(Text, nullable=False)
    severity = Column(String(10), nullable=False, default='MEDIUM')
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("type IN ('LOW_STOCK','EXPIRY','SYSTEM','OTHER')", name='ck_notifications_type'),
        CheckConstraint("severity IN ('LOW','MEDIUM','HIGH')", name='ck_notifications_severity'),
    )

    medicine = relationship("Medicine", back_populates="notifications")
    batch = relationship("MedicineBatch", back_populates="notifications")

Index('idx_notifications_type', Notification.type)
Index('idx_notifications_medicine', Notification.medicine_id)
Index('idx_notifications_batch', Notification.batch_id)
Index('idx_notifications_created_at', Notification.created_at)

# =========================================================
# 16. PRESCRIPTIONS
# =========================================================
class Prescription(Base):
    __tablename__ = "prescriptions"

    prescription_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    customer_id = Column(
        Integer,
        ForeignKey(
            "customers.customer_id",
            onupdate="CASCADE",
            ondelete="SET NULL"
        )
    )

    doctor_name = Column(String(150))
    prescription_image = Column(Text)
    issue_date = Column(Date)
    notes = Column(Text)

    customer = relationship(
        "Customer",
        back_populates="prescriptions"
    )

    prescription_items = relationship(
        "PrescriptionItem",
        back_populates="prescription",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


Index(
    "idx_prescriptions_customer",
    Prescription.customer_id
)

Index(
    "idx_prescriptions_issue_date",
    Prescription.issue_date
)


# =========================================================
# 17. PRESCRIPTION_ITEMS
# =========================================================
class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    prescription_item_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    prescription_id = Column(
        Integer,
        ForeignKey(
            "prescriptions.prescription_id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    medicine_id = Column(
        Integer,
        ForeignKey(
            "medicines.medicine_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    dosage = Column(String(100))
    duration = Column(String(100))
    frequency = Column(String(100))
    notes = Column(Text)

    prescription = relationship(
        "Prescription",
        back_populates="prescription_items"
    )

    medicine = relationship(
        "Medicine",
        back_populates="prescription_items"
    )


Index(
    "idx_prescription_items_prescription",
    PrescriptionItem.prescription_id
)

Index(
    "idx_prescription_items_medicine",
    PrescriptionItem.medicine_id
)
# =========================================================
# 19. SALES_RETURNS
# =========================================================
class SalesReturn(Base):
    __tablename__ = "sales_returns"

    return_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    invoice_id = Column(
        Integer,
        ForeignKey(
            "sales_invoices.invoice_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.user_id",
            onupdate="CASCADE",
            ondelete="SET NULL"
        )
    )

    return_date = Column(
        Date,
        nullable=False,
        server_default=func.current_date()
    )

    status = Column(
        String(20),
        nullable=False,
        default="DRAFT"
    )

    total_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    notes = Column(Text)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (

        CheckConstraint(
            "status IN ('DRAFT','COMPLETED','CANCELLED')",
            name="ck_sales_returns_status"
        ),

        CheckConstraint(
            "total_amount >= 0",
            name="ck_sales_returns_total_amount"
        ),
    )

    invoice = relationship(
        "SalesInvoice",
        back_populates="sales_returns"
    )

    user = relationship(
        "User",
        back_populates="sales_returns"
    )

    return_items = relationship(
        "SalesReturnItem",
        back_populates="sales_return",
        cascade="all, delete-orphan"
    )

# =========================================================
# 20. SALES_RETURN_ITEMS
# =========================================================

class SalesReturnItem(Base):
    __tablename__ = "sales_return_items"

    return_item_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    return_id = Column(
        Integer,
        ForeignKey(
            "sales_returns.return_id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    sale_item_id = Column(
        Integer,
        ForeignKey(
            "sale_items.sale_item_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    medicine_id = Column(
        Integer,
        ForeignKey(
            "medicines.medicine_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    batch_id = Column(
        Integer,
        ForeignKey(
            "medicine_batches.batch_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Numeric(12, 2),
        nullable=False
    )

    subtotal = Column(
        Numeric(12, 2),
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_sales_return_items_quantity"
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_sales_return_items_price"
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_sales_return_items_subtotal"
        ),
    )

    sales_return = relationship(
        "SalesReturn",
        back_populates="return_items"
    )

    sale_item = relationship(
        "SaleItem"
    )

    medicine = relationship(
        "Medicine"
    )

    batch = relationship(
        "MedicineBatch"
    )


Index(
    "idx_sales_return_items_return",
    SalesReturnItem.return_id
)

Index(
    "idx_sales_return_items_sale_item",
    SalesReturnItem.sale_item_id
)

Index(
    "idx_sales_return_items_medicine",
    SalesReturnItem.medicine_id
)



# =========================================================
# 21. EXPIRED_MEDICINES
# =========================================================
class ExpiredMedicine(Base):
    __tablename__ = "expired_medicines"

    expired_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.user_id",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    notes = Column(Text)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="expired_medicines"
    )

    items = relationship(
        "ExpiredMedicineItem",
        back_populates="expired"
    )


# =========================================================
# 22. EXPIRED_MEDICINE_ITEMS
# =========================================================

class ExpiredMedicineItem(Base):
    __tablename__ = "expired_medicine_items"

    expired_item_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    expired_id = Column(
        Integer,
        ForeignKey(
            "expired_medicines.expired_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    medicine_id = Column(
        Integer,
        ForeignKey(
            "medicines.medicine_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    batch_id = Column(
        Integer,
        ForeignKey(
            "medicine_batches.batch_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    reason = Column(
        Text
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_expired_quantity_positive"
        ),
    )

    expired = relationship(
        "ExpiredMedicine",
        back_populates="items"
    )

    medicine = relationship(
        "Medicine"
    )

    batch = relationship(
        "MedicineBatch"
    )


 # =========================================================
# 23. PURCHASE_RETURNS
# =========================================================

class PurchaseReturn(Base):
    __tablename__ = "purchase_returns"

    return_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    purchase_id = Column(
        Integer,
        ForeignKey(
            "purchase_orders.purchase_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.user_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        server_default="DRAFT"
    )

    total_amount = Column(
        Numeric(10, 2),
        nullable=False,
        server_default="0"
    )

    notes = Column(Text)

    return_date = Column(
        Date,
        nullable=False,
        server_default=func.current_date()
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (

        CheckConstraint(
            "status IN ('DRAFT','COMPLETED','CANCELLED')",
            name="ck_purchase_return_status"
        ),

        CheckConstraint(
            "total_amount >= 0",
            name="ck_purchase_return_total_positive"
        ),
    )

    purchase = relationship(
        "PurchaseOrder",
        back_populates="purchase_returns"
    )

    user = relationship(
        "User",
        back_populates="purchase_returns"
    )

    items = relationship(
        "PurchaseReturnItem",
        back_populates="purchase_return",
        cascade="all, delete-orphan"
    )


# =========================================================
# 24. PURCHASE_RETURN_ITEMS
# =========================================================
class PurchaseReturnItem(Base):
    __tablename__ = "purchase_return_items"

    return_item_id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(
        Integer, 
        ForeignKey("purchase_returns.return_id", ondelete="CASCADE"), 
        nullable=False
    )
    purchase_item_id = Column(
        Integer, 
        ForeignKey("purchase_items.purchase_item_id", ondelete="RESTRICT"), 
        nullable=False
    )
    medicine_id = Column(
        Integer, 
        ForeignKey("medicines.medicine_id", ondelete="RESTRICT"), 
        nullable=False
    )
    batch_id = Column(
        Integer, 
        ForeignKey("medicine_batches.batch_id", ondelete="RESTRICT"), 
        nullable=False
    )

    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_purchase_return_qty_positive"),
        CheckConstraint("unit_cost >= 0", name="ck_purchase_return_cost_positive"),
        CheckConstraint("subtotal >= 0", name="ck_purchase_return_subtotal_positive"),
    )

    # Relationships
    purchase_return = relationship("PurchaseReturn", back_populates="items")
    purchase_item = relationship("PurchaseItem", back_populates="purchase_returns")
    medicine = relationship("Medicine")
    batch = relationship("MedicineBatch")
        
# =========================================================
# 25. Audit_Logs
# =========================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL"
        )
    )

    action = Column(
        String(100),
        nullable=False
    )

    table_name = Column(
        String(100),
        nullable=False
    )

    record_id = Column(
        Integer
    )

    details = Column(
        Text
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )

# =========================================================
# DRUG_INTERACTIONS
# =========================================================
class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    interaction_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    medicine_1_id = Column(
        Integer,
        ForeignKey(
            "medicines.medicine_id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    medicine_2_id = Column(
        Integer,
        ForeignKey(
            "medicines.medicine_id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False,
        default="MODERATE"
    )

    description = Column(
        Text,
        nullable=False
    )

    source = Column(
        String(50),
        nullable=False,
        default="DATASET"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "severity IN ('MINOR','MODERATE','MAJOR','CONTRAINDICATED')",
            name="ck_drug_interactions_severity"
        ),
        UniqueConstraint(
            "medicine_1_id",
            "medicine_2_id",
            name="uq_drug_interaction_pair"
        ),
    )

    medicine_1 = relationship(
        "Medicine",
        foreign_keys=[medicine_1_id]
    )

    medicine_2 = relationship(
        "Medicine",
        foreign_keys=[medicine_2_id]
    )


Index(
    "idx_drug_interactions_medicine_1",
    DrugInteraction.medicine_1_id
)

Index(
    "idx_drug_interactions_medicine_2",
    DrugInteraction.medicine_2_id
)

Index(
    "idx_drug_interactions_severity",
    DrugInteraction.severity
)