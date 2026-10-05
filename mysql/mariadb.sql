USE mydb;

CREATE TABLE tbcategories (
  code int(11) NOT NULL AUTO_INCREMENT,
  description varchar(150) DEFAULT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE tbproducts (
  code int(11) NOT NULL AUTO_INCREMENT,
  description varchar(150) DEFAULT NULL,
  salevalue decimal(18,2) DEFAULT NULL,
  active int(1) DEFAULT '1',
  category int(11) DEFAULT NULL,
  PRIMARY KEY (code),
  KEY fkprodcat (category),
  CONSTRAINT fkprodcat
    FOREIGN KEY (category)
    REFERENCES tbcategories (code)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE tbcustomers (
  code int(11) NOT NULL AUTO_INCREMENT,
  Name varchar(100) DEFAULT NULL,
  Address varchar(250) DEFAULT NULL,
  Phone varchar(25) DEFAULT NULL,
  Email varchar(100) DEFAULT NULL,
  BirthDate datetime DEFAULT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE tborders (
  code int(11) NOT NULL AUTO_INCREMENT,
  customer int(11) DEFAULT NULL,
  orderdate timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (code),
  KEY fkordercustomers (customer),
  CONSTRAINT fkordercustomers
    FOREIGN KEY (customer)
    REFERENCES tbcustomers (code)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE tborderdetail (
  product int(11) DEFAULT NULL,
  orders int(11) DEFAULT NULL,
  quantity int(11) DEFAULT NULL,
  salesvalue decimal(18,2) DEFAULT NULL,
  KEY fkproddetail (product),
  KEY fkorders (orders),
  CONSTRAINT fkproddetail
    FOREIGN KEY (product)
    REFERENCES tbproducts (code)
    ON DELETE SET NULL,
  CONSTRAINT fkorders
    FOREIGN KEY (orders)
    REFERENCES tborders (code)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO tbcustomers (Name, Address, Phone, Email, BirthDate) VALUES
('John Smith','101 Main Street, New York, NY','212-5550001','john.smith@email.com','1980-01-01'),
('Mary Johnson','202 Oak Avenue, Chicago, IL','312-5550002','mary.johnson@email.com','1981-02-02'),
('Robert Brown','303 Pine Road, Dallas, TX','214-5550003','robert.brown@email.com','1979-03-03'),
('Linda Davis','404 Maple Street, Miami, FL','305-5550004','linda.davis@email.com','1984-04-04'),
('Michael Wilson','505 Cedar Lane, Seattle, WA','206-5550005','michael.wilson@email.com','1985-05-05'),
('Sarah Miller','606 Birch Street, Denver, CO','303-5550006','sarah.miller@email.com','1986-06-06'),
('David Moore','707 Walnut Avenue, Boston, MA','617-5550007','david.moore@email.com','1977-07-07'),
('Karen Taylor','808 Chestnut Road, Phoenix, AZ','602-5550008','karen.taylor@email.com','1988-08-08'),
('James Anderson','909 Spruce Street, Portland, OR','503-5550009','james.anderson@email.com','1989-09-09'),
('Patricia Thomas','111 Willow Lane, Austin, TX','512-5550010','patricia.thomas@email.com','1975-10-10'),
('Christopher Jackson','112 River Road, Albany, NY','518-5550011','chris.jackson@email.com','1982-11-11'),
('Barbara White','113 Lake Street, Madison, WI','608-5550012','barbara.white@email.com','1979-12-12'),
('Daniel Harris','114 Hill Avenue, Boulder, CO','720-5550013','daniel.harris@email.com','1983-01-13'),
('Elizabeth Martin','115 Valley Road, Napa, CA','707-5550014','elizabeth.martin@email.com','1986-02-14'),
('Matthew Thompson','116 Forest Lane, Eugene, OR','541-5550015','matthew.thompson@email.com','1987-03-15'),
('Susan Garcia','117 Sunset Blvd, Los Angeles, CA','213-5550016','susan.garcia@email.com','1978-04-16'),
('Joshua Martinez','118 Palm Street, San Diego, CA','619-5550017','joshua.martinez@email.com','1989-05-17'),
('Jessica Robinson','119 Ocean Drive, Miami, FL','786-5550018','jessica.robinson@email.com','1990-06-18'),
('Andrew Clark','120 Bay Avenue, Tampa, FL','813-5550019','andrew.clark@email.com','1981-07-19'),
('Amanda Rodriguez','121 Coral Way, Miami, FL','305-5550020','amanda.rodriguez@email.com','1983-08-20'),
('Brian Lewis','122 Market Street, San Francisco, CA','415-5550021','brian.lewis@email.com','1976-09-21'),
('Laura Lee','123 Mission Street, San Jose, CA','408-5550022','laura.lee@email.com','1984-10-22'),
('Kevin Walker','124 King Road, San Mateo, CA','650-5550023','kevin.walker@email.com','1987-11-23'),
('Angela Hall','125 Queen Avenue, Oakland, CA','510-5550024','angela.hall@email.com','1988-12-24'),
('Steven Allen','126 Prince Street, Berkeley, CA','510-5550025','steven.allen@email.com','1975-01-25'),
('Melissa Young','127 Duke Road, Palo Alto, CA','650-5550026','melissa.young@email.com','1989-02-26'),
('Edward Hernandez','128 Knight Lane, Mountain View, CA','650-5550027','edward.hernandez@email.com','1980-03-27'),
('Rachel King','129 Castle Street, Sunnyvale, CA','408-5550028','rachel.king@email.com','1984-04-28'),
('Mark Wright','130 Tower Road, Santa Clara, CA','408-5550029','mark.wright@email.com','1977-05-29'),
('Nicole Lopez','131 Bridge Avenue, Fremont, CA','510-5550030','nicole.lopez@email.com','1988-06-30'),
('Jason Hill','132 Harbor Street, Redwood City, CA','650-5550031','jason.hill@email.com','1981-07-01'),
('Stephanie Scott','133 Dock Road, San Carlos, CA','650-5550032','stephanie.scott@email.com','1982-08-02'),
('Ryan Green','134 Shore Lane, Belmont, CA','650-5550033','ryan.green@email.com','1983-09-03'),
('Emily Adams','135 Coast Street, Half Moon Bay, CA','650-5550034','emily.adams@email.com','1984-10-04'),
('Brandon Baker','136 Cliff Road, Pacifica, CA','650-5550035','brandon.baker@email.com','1985-11-05'),
('Hannah Nelson','137 Ridge Avenue, Daly City, CA','415-5550036','hannah.nelson@email.com','1986-12-06'),
('Justin Carter','138 Peak Street, South San Francisco, CA','650-5550037','justin.carter@email.com','1987-01-07'),
('Megan Mitchell','139 Summit Road, Brisbane, CA','415-5550038','megan.mitchell@email.com','1988-02-08'),
('Aaron Perez','140 Canyon Lane, San Bruno, CA','650-5550039','aaron.perez@email.com','1979-03-09'),
('Olivia Roberts','141 Meadow Road, Millbrae, CA','650-5550040','olivia.roberts@email.com','1990-04-10'),
('Nathan Turner','142 Field Avenue, Burlingame, CA','650-5550041','nathan.turner@email.com','1981-05-11'),
('Victoria Phillips','143 Garden Street, Hillsborough, CA','650-5550042','victoria.phillips@email.com','1982-06-12'),
('Kyle Campbell','144 Orchard Road, Foster City, CA','650-5550043','kyle.campbell@email.com','1983-07-01'),
('Samantha Parker','145 Vineyard Lane, San Mateo, CA','650-5550044','samantha.parker@email.com','1984-08-02'),
('Dylan Evans','146 Grove Street, Belmont, CA','650-5550045','dylan.evans@email.com','1985-09-03'),
('Rebecca Edwards','147 Park Avenue, San Carlos, CA','650-5550046','rebecca.edwards@email.com','1986-10-04'),
('Sean Collins','148 Plaza Road, Redwood City, CA','650-5550047','sean.collins@email.com','1987-11-05'),
('Lauren Stewart','149 Circle Street, Palo Alto, CA','650-5550048','lauren.stewart@email.com','1988-12-06'),
('Ethan Sanchez','150 Square Avenue, Mountain View, CA','650-5550049','ethan.sanchez@email.com','1979-01-07'),
('Grace Morris','151 Center Road, Sunnyvale, CA','408-5550050','grace.morris@email.com','1990-02-08'),
('Adam Rogers','152 North Street, Santa Clara, CA','408-5550051','adam.rogers@email.com','1981-03-09'),
('Chloe Reed','153 South Avenue, Cupertino, CA','408-5550052','chloe.reed@email.com','1982-04-10'),
('Tyler Cook','154 East Road, Los Altos, CA','650-5550053','tyler.cook@email.com','1983-05-11'),
('Natalie Morgan','155 West Street, Los Gatos, CA','408-5550054','natalie.morgan@email.com','1984-06-12'),
('Jordan Bell','156 Cross Road, Saratoga, CA','408-5550055','jordan.bell@email.com','1985-01-01'),
('Isabella Murphy','157 Union Street, Campbell, CA','408-5550056','isabella.murphy@email.com','1986-02-02'),
('Lucas Bailey','158 Liberty Road, Milpitas, CA','408-5550057','lucas.bailey@email.com','1987-03-03'),
('Sophia Rivera','159 Freedom Avenue, San Jose, CA','408-5550058','sophia.rivera@email.com','1988-04-04'),
('Benjamin Cooper','160 Pioneer Road, Santa Clara, CA','408-5550059','benjamin.cooper@email.com','1979-05-05'),
('Emma Richardson','161 Frontier Street, Sunnyvale, CA','408-5550060','emma.richardson@email.com','1990-06-06'),
('Henry Cox','162 Explorer Road, Mountain View, CA','650-5550061','henry.cox@email.com','1981-07-07'),
('Ava Howard','163 Traveler Lane, Palo Alto, CA','650-5550062','ava.howard@email.com','1982-08-08'),
('Jack Ward','164 Journey Street, Menlo Park, CA','650-5550063','jack.ward@email.com','1983-09-09'),
('Lily Torres','165 Route Avenue, Redwood City, CA','650-5550064','lily.torres@email.com','1984-10-10'),
('Owen Peterson','166 Path Road, San Carlos, CA','650-5550065','owen.peterson@email.com','1985-11-11'),
('Mia Gray','167 Trail Street, Belmont, CA','650-5550066','mia.gray@email.com','1986-12-12'),
('Caleb Ramirez','168 Way Avenue, San Mateo, CA','650-5550067','caleb.ramirez@email.com','1987-03-01'),
('Zoe James','169 Course Road, Burlingame, CA','650-5550068','zoe.james@email.com','1988-04-02'),
('Noah Watson','170 Direction Street, Millbrae, CA','650-5550069','noah.watson@email.com','1979-05-03'),
('Ella Brooks','171 Compass Avenue, San Bruno, CA','650-5550070','ella.brooks@email.com','1990-06-04');

INSERT INTO tbcategories (description)
VALUES
  ('Books'),
  ('Cell Phones'),
  ('Tablets'),
  ('Notebooks'),
  ('Office Supply');

INSERT INTO tbproducts (description, salevalue, active, category)
VALUES
('Clean Code Book',45.90,1,1),
('The Pragmatic Programmer',49.90,1,1),
('Design Patterns Book',59.90,1,1),
('SQL Fundamentals',29.90,1,1),
('Python for Data Analysis',42.50,1,1),
('Cloud Architecture Guide',55.00,1,1),
('DevOps Handbook',47.00,1,1),
('Machine Learning Basics',52.00,1,1),
('Agile Project Management',34.90,1,1),
('Data Engineering Essentials',39.90,1,1),
('iPhone 14 128GB',999.00,1,2),
('iPhone 13 128GB',899.00,1,2),
('Samsung Galaxy S23',850.00,1,2),
('Samsung Galaxy A54',420.00,1,2),
('Google Pixel 7',650.00,1,2),
('Google Pixel 6a',399.00,1,2),
('Xiaomi Redmi Note 12',280.00,1,2),
('Motorola Edge 40',530.00,1,2),
('OnePlus Nord',480.00,1,2),
('Sony Xperia 5',720.00,1,2),
('iPad Air 10.9',699.00,1,3),
('iPad Mini',599.00,1,3),
('Samsung Galaxy Tab S8',749.00,1,3),
('Samsung Galaxy Tab A8',299.00,1,3),
('Lenovo Tab P11',330.00,1,3),
('Amazon Fire HD 10',199.00,1,3),
('Xiaomi Pad 5',389.00,1,3),
('Microsoft Surface Go',499.00,1,3),
('Huawei MatePad',360.00,1,3),
('Nokia T20 Tablet',290.00,1,3),
('MacBook Air M2',1199.00,1,4),
('MacBook Pro 14',1999.00,1,4),
('Dell XPS 13',1399.00,1,4),
('Dell Inspiron 15',799.00,1,4),
('HP Spectre x360',1499.00,1,4),
('HP Pavilion 14',749.00,1,4),
('Lenovo ThinkPad X1',1599.00,1,4),
('Lenovo IdeaPad 3',599.00,1,4),
('Asus ZenBook 14',1099.00,1,4),
('Acer Aspire 5',649.00,1,4),
('Ergonomic Office Chair',199.90,1,5),
('Wood Office Desk',299.90,1,5),
('Wireless Keyboard',49.90,1,5),
('Wireless Mouse',29.90,1,5),
('Notebook Stand',39.90,1,5),
('LED Desk Lamp',25.90,1,5),
('A4 Paper Ream 500 Sheets',12.90,1,5),
('Pen Set Pack 10',9.90,1,5),
('Magnetic Whiteboard',89.90,1,5),
('Desktop File Organizer',19.90,1,5);


INSERT INTO tborders (customer, orderdate)
SELECT
    c.code AS customer,
    TIMESTAMP(
        CONCAT(y.year, '-', LPAD(m.month, 2, '0'), '-15 10:00:00')
    ) AS orderdate
FROM tbcustomers c
CROSS JOIN (
    SELECT 2022 AS year UNION ALL
    SELECT 2023 UNION ALL
    SELECT 2024 UNION ALL
    SELECT 2025
) y
CROSS JOIN (
    SELECT 1 AS month UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
    SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL
    SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL
    SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
) m
ORDER BY c.code, y.year, m.month;

INSERT INTO tborderdetail (product, orders, quantity, salesvalue)
SELECT
  (MOD(o.code + n.n, 50) + 1) AS product,
  o.code AS orders,
  (MOD(o.code + n.n, 5) + 1) AS quantity,
  (MOD(o.code + n.n, 5) + 1) * (50 + MOD(o.code * n.n, 200)) AS salesvalue
FROM tborders o
JOIN (
  SELECT 1 AS n UNION ALL
  SELECT 2 UNION ALL
  SELECT 3
) n
ON n.n <= (MOD(o.code, 3) + 1)
WHERE o.code BETWEEN 1 AND 3360;
