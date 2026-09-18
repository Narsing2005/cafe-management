-- Brewline Cafe Management System - MySQL schema
DROP DATABASE IF EXISTS cafe_db;
CREATE DATABASE cafe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cafe_db;

CREATE TABLE admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  email VARCHAR(120),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  category VARCHAR(60) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  description TEXT,
  image VARCHAR(255),
  available TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  customer_name VARCHAR(100),
  total DECIMAL(10,2) NOT NULL DEFAULT 0,
  status ENUM('Pending','Preparing','Served','Completed','Cancelled') DEFAULT 'Pending',
  source ENUM('admin','customer') ,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

CREATE TABLE order_details (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  menu_item_id INT NOT NULL,
  item_name VARCHAR(120) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  subtotal DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);


INSERT INTO menu_items (name, category, price, description, image) VALUES
('Espresso',        'Coffee',  150.00, 'Rich single-shot espresso',        'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?w=600&q=80'),
('Cappuccino',      'Coffee',  180.00, 'Espresso with steamed milk foam',  'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=600&q=80'),
('Caramel Latte',   'Coffee',  220.00, 'Smooth latte with caramel syrup',  'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=600&q=80'),
('Iced Mocha',      'Coffee',  240.00, 'Chocolate espresso over ice',      'https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=600&q=80'),
('Masala Chai',     'Tea',     80.00,  'Spiced Indian milk tea',           'https://images.unsplash.com/photo-1597318236499-69f1c8c0a4a3?w=600&q=80'),
('Green Tea',       'Tea',     120.00, 'Premium loose-leaf green tea',     'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=600&q=80'),
('Croissant',       'Bakery',  140.00, 'Buttery French croissant',         'https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&q=80'),
('Chocolate Muffin','Bakery',  160.00, 'Double chocolate chip muffin',     'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=600&q=80'),
('Veg Sandwich',    'Food',    220.00, 'Grilled veggies, cheese, herbs',   'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600&q=80'),
('Paneer Wrap',     'Food',    260.00, 'Spiced paneer in soft tortilla',   'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&q=80'),
('Cheesecake',      'Dessert', 280.00, 'New York style cheesecake',        'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=600&q=80'),
('Tiramisu',        'Dessert', 300.00, 'Classic Italian tiramisu',         'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&q=80');
