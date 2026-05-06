import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data.sqlite')

conn = sqlite3.connect(DB_PATH)

# -------------------- Part 1: Join and Filter --------------------

# Step 1
df_boston = pd.read_sql("""
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston';
""", conn)

# Step 2
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM offices o
    LEFT JOIN employees e ON o.officeCode = e.officeCode
    GROUP BY o.officeCode
    HAVING COUNT(e.employeeNumber) = 0;
""", conn)
# -------------------- Part 2: Type of Join --------------------

# Step 3
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName;
""", conn)

# Step 4
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName,
           c.phone, c.salesRepEmployeeNumber
    FROM customers c
    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName;
""", conn)

# -------------------- Part 3: Built-in Function --------------------

# Step 5
df_payment = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName,
           p.paymentDate, p.amount
    FROM customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC;
""", conn)

# -------------------- Part 4: Joining and Grouping --------------------

# Step 6
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName,
           COUNT(c.customerNumber) AS num_customers
    FROM employees e
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber
    HAVING AVG(CAST(c.creditLimit AS REAL)) > 90000
    ORDER BY num_customers DESC;
""", conn)

# Step 7
df_product_sold = pd.read_sql("""
    SELECT p.productName,
           COUNT(DISTINCT od.orderNumber) AS numorders,
           SUM(od.quantityOrdered) AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productCode
    ORDER BY totalunits DESC;
""", conn)

# -------------------- Part 5: Multiple Joins --------------------

# Step 8
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode,
           COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode
    ORDER BY numpurchasers DESC;
""", conn)

# Step 9
df_customers = pd.read_sql("""
    SELECT o.officeCode, o.city,
           COUNT(c.customerNumber) AS n_customers
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode;
""", conn)

# -------------------- Part 6: Subquery --------------------

# Step 10
df_under_20 = pd.read_sql("""
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName,
                    o.city, o.officeCode
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders ord ON c.customerNumber = ord.customerNumber
    JOIN orderdetails od ON ord.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT p.productCode
        FROM products p
        JOIN orderdetails od2 ON p.productCode = od2.productCode
        JOIN orders o2 ON od2.orderNumber = o2.orderNumber
        GROUP BY p.productCode
        HAVING COUNT(DISTINCT o2.customerNumber) < 20
    )
    ORDER BY e.lastName;
""", conn)

# -------------------- Close connection --------------------
conn.close()
