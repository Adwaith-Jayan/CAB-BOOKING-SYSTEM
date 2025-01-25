
CREATE DATABASE CAB_BOOKING_SYSTEM;

USE CAB_BOOKING_SYSTEM;

CREATE TABLE users(
    username VARCHAR(100),
    password VARCHAR(500),
    userID INT AUTO_INCREMENT,
    PRIMARY KEY(userID,username,password)
);

CREATE TABLE user (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone BIGINT,
    address VARCHAR(100)
);




CREATE TABLE booking (
    bookingID INT PRIMARY KEY,
    pickup_location VARCHAR(150),
    pickup_time TIME,
    pickup_date DATE,
    drop_location VARCHAR(150),
    no_of_people INT,
    booking_status VARCHAR(50)
);


	




CREATE TABLE cab (
    cabID INT PRIMARY KEY,
    licence_number VARCHAR(20) UNIQUE,
    car_name VARCHAR(50),
    model VARCHAR(50),
    capacity INT,
    status VARCHAR(20)
);

INSERT INTO cab (cabID, licence_number, car_name, model, capacity, status) VALUES
    (1, 'XYZ1234', 'Toyota', 'Camry', 4, 'available'),
    (2, 'ABC5678', 'Honda', 'Civic', 4, 'in service'),
    (3, 'LMN9101', 'Ford', 'Mustang', 4, 'available'),
    (4, 'PQR2345', 'Chevrolet', 'Impala', 5, 'maintenance'),
    (5, 'DEF3456', 'Hyundai', 'Elantra', 4, 'available'),
    (6, 'GHI7890', 'Nissan', 'Altima', 4, 'available'),
    (7, 'JKL1122', 'Tesla', 'Model S', 5, 'in service'),
    (8, 'STU3344', 'BMW', 'X5', 5, 'available'),
    (9, 'VWX5566', 'Audi', 'A4', 4, 'maintenance'),
    (10, 'YZA7788', 'Mercedes', 'C-Class', 4, 'available');







CREATE TABLE driver (
    driverID INT PRIMARY KEY,
    licence_number VARCHAR(20) UNIQUE,
    name VARCHAR(100)
);

INSERT INTO driver (driverID, licence_number, name) VALUES
    (1, 'DL1234567', 'John Doe'),
    (2, 'DL2345678', 'Jane Smith'),
    (3, 'DL3456789', 'Alice Johnson'),
    (4, 'DL4567890', 'Bob Brown'),
    (5, 'DL5678901', 'Charlie Green'),
    (6, 'DL6789012', 'David White'),
    (7, 'DL7890123', 'Ella Black'),
    (8, 'DL8901234', 'Frank Miller'),
    (9, 'DL9012345', 'Grace Lee'),
    (10, 'DL0123456', 'Henry King');










CREATE TABLE payment (
    paymentID INT PRIMARY KEY,
    payment_status VARCHAR(50),
    amount INT,
    mode VARCHAR(50)
);







CREATE TABLE makes (
    userID INT,
    bookingID INT,
    PRIMARY KEY(userID,bookingID),
    FOREIGN KEY(userID) REFERENCES user(userID),
    FOREIGN KEY(bookingID) REFERENCES booking(bookingID)
);


CREATE TABLE assigned (
    bookingID INT,
    cabID INT,
    PRIMARY KEY(bookingID,cabID),
    FOREIGN KEY(bookingID) REFERENCES booking(bookingID),
    FOREIGN KEY(cabID) REFERENCES cab(cabID)
);

CREATE TABLE pays (
    bookingID INT,
    paymentID INT,
    PRIMARY KEY (bookingID,paymentID),
    FOREIGN KEY(bookingID) REFERENCES booking(bookingID)
);

CREATE TABLE drives (
    cabID INT,
    driverID INT,
    PRIMARY KEY(cabID,driverID),
    FOREIGN KEY (cabID) REFERENCES cab(cabID),
    FOREIGN KEY (driverID) REFERENCES driver(driverID)
);


