-- Biblioteca - esquema y datos de ejemplo (MariaDB)
-- Se ejecuta automáticamente al crear el contenedor (docker-entrypoint-initdb.d)

CREATE DATABASE IF NOT EXISTS biblioteca CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biblioteca;

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS usuarios (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100) NOT NULL,
    apellidos   VARCHAR(150) NOT NULL,
    email       VARCHAR(150) NOT NULL,
    telefono    VARCHAR(20)  NULL,
    fecha_alta  DATE         NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uk_usuarios_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS libros (
    id                     BIGINT       NOT NULL AUTO_INCREMENT,
    titulo                 VARCHAR(200) NOT NULL,
    isbn                   VARCHAR(20)  NOT NULL,
    editorial              VARCHAR(150) NULL,
    anio_publicacion       INT          NULL,
    ejemplares_disponibles INT          NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT uk_libros_isbn UNIQUE (isbn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS autores (
    id           BIGINT       NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(150) NOT NULL,
    nacionalidad VARCHAR(100) NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Relación N:M Libro <-> Autor
CREATE TABLE IF NOT EXISTS libro_autor (
    libro_id BIGINT NOT NULL,
    autor_id BIGINT NOT NULL,
    PRIMARY KEY (libro_id, autor_id),
    CONSTRAINT fk_libro_autor_libro FOREIGN KEY (libro_id) REFERENCES libros (id) ON DELETE CASCADE,
    CONSTRAINT fk_libro_autor_autor FOREIGN KEY (autor_id) REFERENCES autores (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS prestamos (
    id                        BIGINT      NOT NULL AUTO_INCREMENT,
    usuario_id                BIGINT      NOT NULL,
    libro_id                  BIGINT      NOT NULL,
    fecha_prestamo            DATE        NOT NULL,
    fecha_devolucion_prevista DATE        NOT NULL,
    fecha_devolucion          DATE        NULL,
    estado                    VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    PRIMARY KEY (id),
    CONSTRAINT fk_prestamos_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    CONSTRAINT fk_prestamos_libro   FOREIGN KEY (libro_id)   REFERENCES libros (id),
    CONSTRAINT ck_prestamos_estado  CHECK (estado IN ('ACTIVO', 'DEVUELTO', 'RETRASADO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- Datos de ejemplo ----------

INSERT INTO usuarios (nombre, apellidos, email, telefono, fecha_alta) VALUES
('Lucía',  'García López',     'lucia.garcia@example.com',  '600111222', '2026-01-15'),
('Marc',   'Puig Ferrer',      'marc.puig@example.com',     '600222333', '2026-02-03'),
('Andrea', 'Valero Sanz',      'andrea.valero@example.com', '600333444', '2026-03-10'),
('Javier', 'Martín Ruiz',      'javier.martin@example.com', '600444555', '2026-04-22'),
('Sara',   'Fernández Gómez',  'sara.fernandez@example.com','600555666', '2026-05-30');

INSERT INTO autores (nombre, nacionalidad) VALUES
('Gabriel García Márquez', 'Colombiana'),
('Miguel de Cervantes',    'Española'),
('Isabel Allende',         'Chilena'),
('Carlos Ruiz Zafón',      'Española'),
('Arturo Pérez-Reverte',   'Española');

INSERT INTO libros (titulo, isbn, editorial, anio_publicacion, ejemplares_disponibles) VALUES
('Cien años de soledad',          '9788497592208', 'Debolsillo',  1967, 3),
('El amor en los tiempos del cólera', '9788497592451', 'Debolsillo', 1985, 2),
('Don Quijote de la Mancha',      '9788420412146', 'Alfaguara',   1605, 4),
('La casa de los espíritus',      '9788401352836', 'Plaza & Janés', 1982, 2),
('La sombra del viento',          '9788408163381', 'Planeta',     2001, 5),
('El juego del ángel',            '9788408081180', 'Planeta',     2008, 1),
('El capitán Alatriste',          '9788466329880', 'Alfaguara',   1996, 2),
('La tabla de Flandes',           '9788466329897', 'Alfaguara',   1990, 0);

INSERT INTO libro_autor (libro_id, autor_id) VALUES
(1, 1), (2, 1), (3, 2), (4, 3), (5, 4), (6, 4), (7, 5), (8, 5);

INSERT INTO prestamos (usuario_id, libro_id, fecha_prestamo, fecha_devolucion_prevista, fecha_devolucion, estado) VALUES
(1, 1, '2026-09-01', '2026-09-15', '2026-09-14', 'DEVUELTO'),
(2, 3, '2026-09-10', '2026-09-24', NULL,         'RETRASADO'),
(3, 5, '2026-09-28', '2026-10-12', NULL,         'ACTIVO'),
(4, 7, '2026-09-30', '2026-10-14', NULL,         'ACTIVO'),
(5, 4, '2026-08-20', '2026-09-03', '2026-09-02', 'DEVUELTO'),
(1, 8, '2026-10-01', '2026-10-15', NULL,         'ACTIVO');
