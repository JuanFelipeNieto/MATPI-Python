create database matpi;
use matpi;

create table Usuario
(
ID varchar(16) primary key,
Telefono varchar(14),
Contraseña varchar(20),
Correo_Electronico varchar(35),
Estado enum(
	'Activo', 
	'Vacaciones', 
	'Inactivo'
		),
Fecha_Nacimiento date,
Nombre_Completo varchar(40),
Direccion varchar(50),
Fecha_ingreso date,
Experiencia_Laboral varchar(15)
);

create table Administrador
(
Ult_Fecha_login datetime,
Ult_IP_login varchar(45),
Formacion_Educativa varchar(35),
	ID_Usr varchar(16),
		constraint Usuario_Hereda_Administrador 
		foreign key (ID_Usr) references Usuario(ID)
);

/* Cambio de Empleado a Cajero */
create table Cajero
(
EPS enum (
	'Nueva EPS',
	'Sanitas', 
    'SURA', 
    'Salud Total', 
    'Compensar', 
    'Famisanar', 
    'Coosalud', 
    'Mutual Ser', 
    'SOS', 
    'Salud Mía', 
    'Aliansalud', 
    'Dusakawi', 
    'Salud Bolívar', 
    'Savia Salud', 
    'Cajacopi', 
    'Asmet Salud', 
    'Emssanar', 
    'Capital Salud'
			),
tipo_contrato enum(
	'Indefinido',
	'Fijo'
					),
Turno enum('Mañana', 'Tarde', 'Noche'),
Contacto_Emergencia_Nombre varchar(35), 
Contacto_Emergencia_Parentesco varchar(15),
Contacto_Emergencia_Numero varchar(14),
Fecha_Terminacion_Contrato date,
	ID_Usr varchar(16),
		constraint Usuario_Hereda_Cajero 
		foreign key (ID_Usr) references Usuario(ID) 
);

create table Cliente
(
ID smallint unsigned primary key,
Nombre_Completo varchar(40),
Telefono varchar(14),
	ID_Usr varchar(16),
		constraint fk_cajero_cliente foreign key (ID_Usr) references Cajero(ID_Usr) 
);

create table Reserva
(
ID smallint unsigned primary key,
Fecha datetime,
Estado boolean,
Observciones tinytext,
	ID_Usr varchar(16),
		constraint fk_reserva_cajero foreign key (ID_Usr) references Cajero(ID_Usr)
);

create table Pedido
(
ID smallint unsigned primary key, 
Fecha date,
Estado boolean,
Valor int unsigned,
numero_orden tinyint unsigned,
Metodo_Pago enum(
        'Efectivo', 
        'Tarjeta Débito', 
        'Tarjeta Crédito', 
        'Nequi', 
        'Daviplata', 
        'PSE'
    ) not null,
	ID_Usr varchar(16),

		constraint fk_pedido_cajero 
		foreign key (ID_Usr) 
		references Cajero(ID_Usr),
	ID_Reserva smallint unsigned,
		constraint fk_pedido_reserva 
		foreign key (ID_Reserva) 
		references Reserva(ID),

	ID_Cliente smallint unsigned,
		constraint fk_pedido_cliente
        foreign key (ID_Cliente)
        references Cliente(ID)
        on delete set null  
        on update cascade
);

create table Proveedor
(
ID smallint unsigned primary key,
Nombre_Proveedor varchar(50),
Direccion varchar(120),
Correo_Electronico varchar(35),
Telefono varchar(14),
	ID_Usr varchar(16),
		constraint fk_proveedor_cajero foreign key (ID_Usr) references Cajero(ID_Usr)
);

create table Producto
(
ID smallint unsigned primary key,
Nombre_Producto varchar(50), -- Aumentado un poco por nombres largos
Descripcion tinytext,
Cantidad smallint unsigned, -- Stock disponible
Precio int unsigned, 
Categoria enum(
    'Hamburguesas',
    'Perros Calientes',
    'Entradas y Snacks',
    'Combos',
    'Bebidas',
    'Postres',
    'Adiciones',
    'Salsas'
    )
);
create table Factura
(
ID smallint unsigned primary key,
Valor_Total int unsigned,
Descripcion tinytext,
IVA float,

	ID_Pedi smallint unsigned,
		constraint fk_factura_pedido
        foreign key (ID_Pedi)
        references Pedido(ID)
        on delete cascade
        on update cascade
);

create table Materia_Prima
(
ID smallint unsigned primary key,
Nombre_Materia_Prima varchar(60),
Unidad_Medida varchar(20),
Cantidad smallint unsigned,
Fecha_Ingreso datetime,
Fecha_Vencimiento date
);

-- tablas intermedias

create table Details_Producto_MateriaP
(
 Producto_ID smallint unsigned,
    MateriaPrima_ID smallint unsigned,
    Cantidad_Usada smallint unsigned, 

    primary key (Producto_ID, MateriaPrima_ID),

    constraint FK_Producto
        foreign key (Producto_ID) 
        references Producto(ID)
        on delete cascade
        on update cascade,

    constraint FK_MateriaPrima
        foreign key (MateriaPrima_ID) 
        references Materia_Prima(ID)
        on delete cascade
        on update cascade
);

create table Details_Proveedor_MateriaP
(
    Proveedor_ID smallint unsigned,
    MateriaPrima_ID smallint unsigned,
    Precio_Unitario decimal(10,2),  
    Fecha_Suministro datetime,   

    primary key (Proveedor_ID, MateriaPrima_ID),

    constraint FK_Proveedor_MateriaPrima_Proveedor 
        foreign key (Proveedor_ID) 
        references Proveedor(ID)
        on delete cascade
        on update cascade,

    constraint FK_Proveedor_MateriaPrima_MateriaPrima 
        foreign key (MateriaPrima_ID) 
        references Materia_Prima(ID)
        on delete cascade
        on update cascade);

create table Details_Pedido_Producto
(
	ID smallint unsigned auto_increment primary key,
    ID_Pedido smallint unsigned,
    ID_Producto smallint unsigned,
    Cantidad smallint unsigned,
    Precio_Unitario int unsigned,
    Estado enum(
    "preparando", 
     "finalizado"),

    constraint fk_producto_pedido_pedido 
        foreign key (ID_Pedido) 
        references Pedido(ID)
        on delete cascade,

    constraint fk_producto_pedido_producto 
        foreign key (ID_Producto) 
        references Producto(ID)
        on delete cascade

);