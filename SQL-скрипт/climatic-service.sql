CREATE TABLE Clients (
    ClientID SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    Email VARCHAR(100),
    Address TEXT
);

CREATE TABLE Masters (
    MasterID SERIAL PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Specialization VARCHAR(100),
    Phone VARCHAR(20) NOT NULL
);

CREATE TABLE Equipment (
    EquipmentID SERIAL PRIMARY KEY,
    Model VARCHAR(100) NOT NULL,
    SerialNumber VARCHAR(50) UNIQUE,
    ClientID INT NOT NULL,
    EquipmentType VARCHAR(100),
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID) ON DELETE CASCADE
);

CREATE TABLE FaultTypes (
    FaultTypeID SERIAL PRIMARY KEY,
    FaultName VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE Requests (
    RequestID SERIAL PRIMARY KEY,
    CreateDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Description TEXT,
    EquipmentID INT NOT NULL,
    MasterID INT,
    Status VARCHAR(50) NOT NULL DEFAULT 'Новая',
    CompletionDate DATE,
    FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID) ON DELETE CASCADE,
    FOREIGN KEY (MasterID) REFERENCES Masters(MasterID) ON DELETE SET NULL
);

CREATE TABLE RequestDetails (
    DetailID SERIAL PRIMARY KEY,
    RequestID INT NOT NULL,
    FaultTypeID INT NOT NULL,
    FOREIGN KEY (RequestID) REFERENCES Requests(RequestID) ON DELETE CASCADE,
    FOREIGN KEY (FaultTypeID) REFERENCES FaultTypes(FaultTypeID) ON DELETE CASCADE,
    UNIQUE(RequestID, FaultTypeID)
);

CREATE TABLE Roles (
    RoleID SERIAL PRIMARY KEY,
    RoleName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Login VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    RoleID INT NOT NULL,
    MasterID INT,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID) ON DELETE CASCADE,
    FOREIGN KEY (MasterID) REFERENCES Masters(MasterID) ON DELETE SET NULL
);

CREATE INDEX idx_equipment_client ON Equipment(ClientID);
CREATE INDEX idx_requests_equipment ON Requests(EquipmentID);
CREATE INDEX idx_requests_master ON Requests(MasterID);
CREATE INDEX idx_requests_status ON Requests(Status);
CREATE INDEX idx_requestdetails_request ON RequestDetails(RequestID);
CREATE INDEX idx_users_login ON Users(Login);

INSERT INTO Roles (RoleName) VALUES 
    ('Администратор'),
    ('Мастер'),
    ('Менеджер'),
    ('Оператор');

INSERT INTO FaultTypes (FaultName) VALUES 
    ('Не включается'),
    ('Не охлаждает'),
    ('Не греет'),
    ('Утечка фреона'),
    ('Странный шум'),
    ('Течь воды'),
    ('Не работает вентилятор'),
    ('Проблемы с пультом'),
    ('Запах при работе'),
    ('Плохой обдув'),
    ('Замерзает испаритель'),
    ('Пульт не реагирует'),
    ('Мигают индикаторы'),
    ('Выбивает автомат'),
    ('Грязный фильтр'),
    ('Не работает компрессор'),
    ('Шум при выключении'),
    ('Вибрация'),
    ('Не регулируется температура'),
    ('Посторонние звуки');

INSERT INTO Clients (FullName, Phone, Email, Address) VALUES
    ('Иванов Иван Иванович', '+7(999)123-45-67', 'ivanov@mail.com', 'ул. Ленина, д.1, кв.1'),
    ('Петров Петр Петрович', '+7(999)234-56-78', 'petrov@mail.com', 'ул. Гагарина, д.5, кв.12'),
    ('Сидорова Анна Сергеевна', '+7(999)345-67-89', 'sidorova@mail.com', 'пр. Мира, д.10, кв.45'),
    ('Козлов Дмитрий Николаевич', '+7(999)456-78-90', 'kozlov@mail.com', 'ул. Советская, д.15, кв.7'),
    ('Морозова Елена Викторовна', '+7(999)567-89-01', 'morozova@mail.com', 'ул. Лесная, д.3, кв.23'),
    ('Волков Андрей Павлович', '+7(999)678-90-12', 'volkov@mail.com', 'пр. Победы, д.20, кв.56'),
    ('Соколова Татьяна Игоревна', '+7(999)789-01-23', 'sokolova@mail.com', 'ул. Садовая, д.8, кв.14'),
    ('Михайлов Сергей Алексеевич', '+7(999)890-12-34', 'mikhailov@mail.com', 'ул. Новая, д.12, кв.34'),
    ('Федорова Ольга Дмитриевна', '+7(999)901-23-45', 'fedorova@mail.com', 'пр. Ленинградский, д.7, кв.89'),
    ('Алексеев Максим Игоревич', '+7(999)012-34-56', 'alekseev@mail.com', 'ул. Пушкина, д.25, кв.5');

INSERT INTO Masters (FullName, Specialization, Phone) VALUES
    ('Сидоров Сидор Сидорович', 'Сплит-системы', '+7(999)345-67-89'),
    ('Смирнов Алексей Владимирович', 'Промышленное оборудование', '+7(999)456-78-90'),
    ('Кузнецов Денис Андреевич', 'Мульти-сплит системы', '+7(999)567-89-01'),
    ('Попов Игорь Валерьевич', 'VRF системы', '+7(999)678-90-12'),
    ('Васильев Роман Сергеевич', 'Оконные кондиционеры', '+7(999)789-01-23'),
    ('Зайцев Константин Павлович', 'Кассетные кондиционеры', '+7(999)890-12-34'),
    ('Павлов Дмитрий Викторович', 'Канальные кондиционеры', '+7(999)901-23-45'),
    ('Николаев Артем Геннадьевич', 'Колонные кондиционеры', '+7(999)012-34-56'),
    ('Борисов Максим Эдуардович', 'Прецизионные кондиционеры', '+7(999)123-45-67'),
    ('Григорьев Евгений Александрович', 'Бытовые кондиционеры', '+7(999)234-56-78');

INSERT INTO Equipment (Model, SerialNumber, ClientID, EquipmentType) VALUES
    ('Samsung AC12', 'SN123456789', 1, 'Сплит-система'),
    ('LG DUAL 9', 'SN987654321', 2, 'Кондиционер'),
    ('Mitsubishi MSZ', 'SN456789123', 3, 'Сплит-система инверторная'),
    ('Daikin FTX', 'SN789123456', 4, 'Настенный кондиционер'),
    ('Toshiba RAS', 'SN321654987', 5, 'Сплит-система'),
    ('Panasonic CS', 'SN654987321', 6, 'Инверторный кондиционер'),
    ('Haier HSU', 'SN147258369', 7, 'Мобильный кондиционер'),
    ('Electrolux EACS', 'SN369147258', 8, 'Оконный кондиционер'),
    ('Ballu BSU', 'SN258369147', 9, 'Колонный кондиционер'),
    ('Gree GWC', 'SN951753456', 10, 'Канальный кондиционер'),
    ('MDC VRF', 'SN753951852', 1, 'VRF система'),
    ('Midea MSG', 'SN852654123', 2, 'Мульти-сплит система'),
    ('Hisense AS', 'SN456123789', 3, 'Сплит-система'),
    ('TCL TAC', 'SN789456123', 4, 'Мобильный кондиционер'),
    ('AEG AS', 'SN123789456', 5, 'Настенный кондиционер'),
    ('Sharp AY', 'SN456789321', 6, 'Сплит-система'),
    ('Hitachi RAS', 'SN789321456', 7, 'Инвертор'),
    ('Fujitsu ASY', 'SN321456789', 8, 'Кассетный кондиционер'),
    ('Samsung AC18', 'SN654123789', 9, 'Сплит-система'),
    ('LG ARTCOOL', 'SN987321654', 10, 'Дизайн-радиатор');

INSERT INTO Requests (CreateDate, Description, EquipmentID, MasterID, Status, CompletionDate) VALUES
    ('2024-01-15', 'Не охлаждает, течет вода', 1, 1, 'Выполнена', '2024-01-16'),
    ('2024-02-01', 'Странный шум при включении', 2, NULL, 'Новая', NULL),
    ('2024-01-20', 'Вообще не включается', 3, 2, 'Выполнена', '2024-01-22'),
    ('2024-01-25', 'Плохо охлаждает', 4, 3, 'Выполнена', '2024-01-27'),
    ('2024-02-05', 'Течет вода из внутреннего блока', 5, NULL, 'В работе', NULL),
    ('2024-01-10', 'Запах при работе', 6, 4, 'Выполнена', '2024-01-12'),
    ('2024-01-30', 'Мигают индикаторы', 7, 5, 'Выполнена', '2024-02-01'),
    ('2024-02-07', 'Не реагирует на пульт', 8, NULL, 'Новая', NULL),
    ('2024-01-18', 'Выбивает автомат', 9, 6, 'Выполнена', '2024-01-20'),
    ('2024-02-03', 'Слабая мощность', 10, 7, 'В работе', NULL),
    ('2024-01-22', 'Шум при выключении', 11, 8, 'Выполнена', '2024-01-24'),
    ('2024-02-08', 'Не греет зимой', 12, NULL, 'Новая', NULL),
    ('2024-01-12', 'Вибрация наружного блока', 13, 9, 'Выполнена', '2024-01-14'),
    ('2024-01-28', 'Замерзает испаритель', 14, 10, 'Выполнена', '2024-01-30'),
    ('2024-02-10', 'Не переключает режимы', 15, NULL, 'Новая', NULL),
    ('2024-01-05', 'Пульт работает с перебоями', 16, 1, 'Выполнена', '2024-01-07'),
    ('2024-01-17', 'Грязный фильтр', 17, 2, 'Выполнена', '2024-01-18'),
    ('2024-02-12', 'Стук при работе', 18, NULL, 'Новая', NULL),
    ('2024-01-23', 'Не открывает жалюзи', 19, 3, 'Выполнена', '2024-01-25'),
    ('2024-02-15', 'Пахнет горелым', 20, NULL, 'Новая', NULL),
    ('2024-01-08', 'Проблемы с дренажем', 1, 4, 'Выполнена', '2024-01-10'),
    ('2024-01-19', 'Не держит температуру', 3, 5, 'Выполнена', '2024-01-21'),
    ('2024-02-18', 'Посторонние звуки', 5, NULL, 'Новая', NULL),
    ('2024-01-14', 'Утечка фреона', 7, 6, 'Выполнена', '2024-01-16'),
    ('2024-01-29', 'Зависает компрессор', 9, 7, 'Выполнена', '2024-01-31');

INSERT INTO RequestDetails (RequestID, FaultTypeID) VALUES
    (1, 2), (1, 6),
    (2, 5),
    (3, 1),
    (4, 2), (4, 19),
    (5, 6),
    (6, 9),
    (7, 13),
    (8, 12),
    (9, 14),
    (10, 19), (10, 20),
    (11, 17),
    (12, 3),
    (13, 18),
    (14, 11),
    (15, 19),
    (16, 8),
    (17, 15),
    (18, 5), (18, 18),
    (19, 8),
    (20, 9),
    (21, 6),
    (22, 19),
    (23, 20),
    (24, 4),
    (25, 16);

INSERT INTO Users (Login, PasswordHash, RoleID, MasterID) VALUES
    ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 1, NULL),
    ('master.sidorov', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 2, 1),
    ('master.smirnov', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 2, 2),
    ('master.kuznetsov', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 2, 3),
    ('master.popov', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 2, 4),
    ('manager.ivanova', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 3, NULL),
    ('operator.klin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 4, NULL);