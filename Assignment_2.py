import mysql.connector

#STORED PROCEDURES

#DELIMITER //
# CREATE PROCEDURE newOrder(IN myCustomerID INT, IN myOrderDate TEXT, IN myShipDate TEXT, IN myShipAddress TEXT, IN myShipCity TEXT,
#  IN myShipPostalCode TEXT, IN myShipCountry TEXT, IN myProductID INT, IN myQuantity INT)
#     BEGIN
#         INSERT INTO Orders (CustomerID, OrderDate, ShipDate, ShipAddress, ShipCity,
#                             ShipPostalCode, ShipCountry) VALUES
#                             (myCustomerID, myOrderDate, myShipDate, myShipAddress, myShipCity, myShipPostalCode, myShipCountry);
#         INSERT INTO OrderDetails (ProductID, Quantity) VALUES (myProductID, myQuantity);
#         CALL updateStock(myProductID, myQuantity);
#     END //
# DELIMITER ;
#
#
# DELIMITER //
# CREATE PROCEDURE updateStock(IN myProductID INT, IN myQuantity INT)
#     BEGIN
#         UPDATE Products
#         SET UnitsInStock = UnitsInStock - myQuantity
#         WHERE ProductID = myProductID;
#     END //
# DELIMITER ;


#Function to connect to database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port='3306',
            user='root',
            passwd='change-me',
            database='murillo_cpsc408'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

#Function to display a product that has 0 units in stock
def displayStock(conn):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM Products WHERE UnitsInStock=0"
        cursor.execute(query)
        for (ProductID, ProductName, SupplierID, Category, UnitPrice, UnitsInStock) in cursor:
            print(f"Product ID: {ProductID}, Product Name: {ProductName}, Category: {Category}, Price: {UnitPrice}\n")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")

#Function that displays the total orders of a customer
def totalOrders(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT COUNT(*) as TotalOrders, Orders.CustomerID, Customers.CustomerName "
                 "FROM Orders JOIN Customers ON Orders.CustomerID=Customers.CustomerID "
                 "GROUP BY Orders.CustomerID")
        cursor.execute(query)
        for (TotalOrders, CustomerID, CustomerName) in cursor:
            print(f"Customer: {CustomerName}, ID: {CustomerID}, Total Orders: {TotalOrders}\n")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")

#Function that displays the details of a product inputted by the user
def productDetails(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT o.OrderID, p.ProductID, p.ProductName, od.UnitPrice, od.Quantity "
                 "FROM Orders o JOIN OrderDetails od ON o.OrderID = od.OrderID "
                 "JOIN Products p ON od.ProductID = p.ProductID "
                 "WHERE (o.OrderID, od.UnitPrice) IN (SELECT OrderID, MAX(UnitPrice) "
                 "FROM OrderDetails GROUP BY OrderID) ORDER BY o.OrderID")
        cursor.execute(query)
        for (OrderID, ProductID, ProductName, UnitPrice, Quantity) in cursor:
            print(f"OrderID: {OrderID}, ProductID: {ProductID}, ProductName{ProductName}, Unit Price: {UnitPrice}, Quantity: {Quantity}\n")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")

#Function that displays if a product has never been ordered
def neverOrdered(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT ProductID, ProductName FROM Products WHERE NOT EXISTS "
                 "(SELECT * FROM OrderDetails WHERE OrderDetails.ProductID = Products.ProductID)")
        cursor.execute(query)
        for (ProductID, ProductName) in cursor:
            print(f"ProductID: {ProductID}, Product Name: {ProductName}\n")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")

#Function that displays the total revenue of a supplier
def totalRevenue(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT SUM(Products.UnitPrice * OrderDetails.Quantity) AS TotalRevenue, Suppliers.SupplierID, Suppliers.SupplierName "
                 "FROM Suppliers JOIN Products ON Suppliers.SupplierID = Products.SupplierID "
                 "JOIN OrderDetails ON Products.ProductID = OrderDetails.ProductID "
                 "JOIN Orders ON OrderDetails.OrderID = Orders.OrderID GROUP BY Suppliers.SupplierID, Suppliers.SupplierName")
        cursor.execute(query)
        for (TotalRevenue, SupplierID, SupplierName) in cursor:
            print(f"SupplierID: {SupplierID}, SupplierName{SupplierName}, Total Revenue: {TotalRevenue}\n")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")

#Function that adds a new order to the database
def addNewOrder(conn):
    try:
        cursor = conn.cursor()
        inputCustomerID = input("Enter a value for CustomerID: ")
        queryOne = (f"SELECT Address, City, PostalCode, Country FROM Customers WHERE CustomerID = {inputCustomerID}")
        cursor.execute(queryOne)
        cusomerTuple = cursor.fetchone()
        ShipAddress = cusomerTuple[0]
        ShipCity = cusomerTuple[1]
        ShipPostalCode = cusomerTuple[2]
        ShipCountry = cusomerTuple[3]
        OrderDate = input("Enter a value for Order Date (format as: YYYY-MM-DD):\n")
        ShipDate = input("Enter a value for Ship Date (format as: YYYY-MM-DD):\n")
        # OrderDate, ShipDate must be inputted by user

        myProductID = input("Enter a value for ProductID:\n")
        queryTwo = ("SELECT * From Products")
        cursor.execute(queryTwo)
        rowCount = cursor.fetchall()
        while (True):
            if (int(myProductID) < len(rowCount) and int(myProductID) > 0):
                break
            else:
                myProductID = input("The value entered is out of range, please enter a value within the range:\n")
            if (myProductID.isNumeric == False):
                myProductID = input("Please enter a valid value for ProductID:\n")
                continue

        queryThree = (f"SELECT UnitsInStock FROM Products WHERE ProductID = {myProductID}")
        cursor.execute(queryThree)
        quantityTuple = cursor.fetchone()
        unitsLeft = quantityTuple[0]
        myQuantity = input(f"Enter a value for quantity of the order (Units in stock: {unitsLeft}):\n")
        while(True):
            if(myQuantity.isnumeric() == False):
                myQuantity = ("Please enter a numerical value for the quantity:\n")
            if(int(myQuantity) > 0 and int(myQuantity) <= unitsLeft):
                break;
            else:
                myQuantity = input(f"Quantity exceeds the amount of units left in stock. Please enter a range between 1 and {unitsLeft} for the quantity:\n")

        orderUserInput = (inputCustomerID, OrderDate, ShipDate, ShipAddress, ShipCity,
                              ShipPostalCode, ShipCountry, myProductID, myQuantity)
        cursor.callproc('newOrder', orderUserInput)
        conn.commit()
        print("A new order has been added.\n")
    except mysql.connector.Error as e:
        print(f"Error creating a record: {e}")


#main function
def main():
    conn = connect_to_database()
    exitProgram = False
    if conn:
        while (exitProgram != True):
            userInput = input('\nEnter "List" to list all products that are out of stock\n'
        'Enter "Details" to display the details of the most expensive product ordered in each order.\n'
        'Enter "Retrieve" to retrieve a list of products that have never been ordered\n'
        'Enter "Revenue" to show the total revenue generated by each supplier.\n'
        'Enter "Add" to add a new order.\nElse type "Exit" to exit the program\n')

            if (userInput == "List"):
                displayStock(conn)
            elif (userInput == "Details"):
                totalOrders(conn)
            elif (userInput == "Retrieve"):
                neverOrdered(conn)
            elif (userInput == "Revenue"):
                totalRevenue(conn)
            elif (userInput == "Add"):
                addNewOrder(conn)
            elif (userInput == "Exit"):
                conn.close()
                print(f"You have exited the program.\n")
                exitProgram = True

if __name__ == "__main__":
    main()
