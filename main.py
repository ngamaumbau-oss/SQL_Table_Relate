import sqlite3
import pandas as pd

# Connect to the database
# Tables: orderdetails, payments, offices, customers, orders,
#         productlines, products, employees
conn = sqlite3.connect('data.sqlite')

# ── Step 1 ─────────────────────────────────────────────────────────────────
# Boston employees: first name, last name, job title
df_boston = pd.read_sql("""
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
""", conn)

# ── Step 2 ─────────────────────────────────────────────────────────────────
# Offices with zero employees — rubric requires HAVING with aggregate COUNT
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city,
           COUNT(e.employeeNumber) AS num_employees
    FROM offices o
    LEFT JOIN employees e ON o.officeCode = e.officeCode
    GROUP BY o.officeCode
    HAVING COUNT(e.employeeNumber) = 0
""", conn)

# ── Step 3 ─────────────────────────────────────────────────────────────────
# All employees with office city and state (LEFT JOIN to include all)
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName
""", conn)

# ── Step 4 ─────────────────────────────────────────────────────────────────
# Customers who have NOT placed any orders (24 total)
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName,
           c.phone, c.salesRepEmployeeNumber
    FROM customers c
    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName
""", conn)

# ── Step 5 ─────────────────────────────────────────────────────────────────
# All customer payments sorted by amount descending
# CAST to REAL ensures numeric sort (not lexicographic)
df_payment = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName,
           p.paymentDate, p.amount
    FROM customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC
""", conn)

# ── Step 6 ─────────────────────────────────────────────────────────────────
# Employees whose customers have average credit limit > 90k (4 employees)
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName,
           COUNT(c.customerNumber) AS num_customers
    FROM employees e
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber
    HAVING AVG(CAST(c.creditLimit AS REAL)) > 90000
    ORDER BY num_customers DESC
""", conn)

# ── Step 7 ─────────────────────────────────────────────────────────────────
# Product sales: number of orders and total units sold
df_product_sold = pd.read_sql("""
    SELECT p.productName,
           COUNT(DISTINCT od.orderNumber) AS numorders,
           SUM(od.quantityOrdered)        AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productCode
    ORDER BY totalunits DESC
""", conn)

# ── Step 8 ─────────────────────────────────────────────────────────────────
# Number of unique customers per product (market reach)
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode,
           COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products p
    JOIN orderdetails od ON p.productCode  = od.productCode
    JOIN orders o        ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode
    ORDER BY numpurchasers DESC
""", conn)

# ── Step 9 ─────────────────────────────────────────────────────────────────
# Number of customers per office
df_customers = pd.read_sql("""
    SELECT o.officeCode, o.city,
           COUNT(c.customerNumber) AS n_customers
    FROM offices o
    JOIN employees e ON o.officeCode    = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode
""", conn)

# ── Step 10 ────────────────────────────────────────────────────────────────
# Employees who sold products ordered by fewer than 20 customers (subquery)
df_under_20 = pd.read_sql("""
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName,
                    o.city, o.officeCode
    FROM employees e
    JOIN offices      o   ON e.officeCode         = o.officeCode
    JOIN customers    c   ON e.employeeNumber      = c.salesRepEmployeeNumber
    JOIN orders       ord ON c.customerNumber      = ord.customerNumber
    JOIN orderdetails od  ON ord.orderNumber       = od.orderNumber
    WHERE od.productCode IN (
        SELECT p.productCode
        FROM products p
        JOIN orderdetails od2 ON p.productCode   = od2.productCode
        JOIN orders       o2  ON od2.orderNumber = o2.orderNumber
        GROUP BY p.productCode
        HAVING COUNT(DISTINCT o2.customerNumber) < 20
    )
    ORDER BY e.lastName
""", conn)

conn.close()
