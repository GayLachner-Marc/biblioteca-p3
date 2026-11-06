# Biblioteca – FP065 Producto 2

Aplicación de gestión de biblioteca basada en Spring Boot, diseñada para administrar usuarios, libros, autores y préstamos de forma eficiente mediante una arquitectura modular con JPA/Hibernate.

## Tecnologías

- **Spring Boot** 4.1.1
- **Java** 25
- **Spring Data JPA** (Hibernate)
- **Thymeleaf** (templates HTML)
- **Bootstrap** 5 (estilos)
- **MariaDB** 11 (base de datos principal)
- **H2 Database** (tests con perfil `test`)
- **Docker** y **Docker Compose**
- **JUnit 5** (pruebas unitarias)

## Modelo de Datos

| Tabla | Descripción | Columnas |
|-------|-------------|----------|
| **usuarios** | Registro de usuarios de la biblioteca | id (PK), nombre, apellidos, email (UK), telefono, fecha_alta |
| **libros** | Catálogo de libros | id (PK), titulo, isbn (UK), editorial, anio_publicacion, ejemplares_disponibles |
| **autores** | Información de autores | id (PK), nombre, nacionalidad |
| **libro_autor** | Relación N:M entre libros y autores | libro_id (FK), autor_id (FK) |
| **prestamos** | Registro de préstamos y devoluciones | id (PK), usuario_id (FK), libro_id (FK), fecha_prestamo, fecha_devolucion_prevista, fecha_devolucion, estado (ACTIVO/DEVUELTO/RETRASADO) |

### Relaciones
- **Usuario** (1:N) **Préstamo**
- **Libro** (1:N) **Préstamo**
- **Libro** (N:M) **Autor** (mediante tabla `libro_autor`)

## Estructura de Paquetes

```
com.serverside.appbackendp1
├── model/          Entidades JPA (Usuario, Libro, Autor, Prestamo, EstadoPrestamo)
├── repository/     Interfaces JpaRepository (UsuarioRepository, LibroRepository, AutorRepository, PrestamoRepository)
├── service/        Lógica de negocio (creada por otros)
├── controller/     Controladores MVC (creados por otros)
└── templates/      Vistas Thymeleaf (creadas por otros)
```

## Cómo Arrancar

### Con Docker Compose (recomendado)

```bash
# Construir e iniciar los contenedores
docker compose up -d --build

# Acceder a la aplicación
# Web: http://localhost:8080
# Base de datos: localhost:3306

# Parar los contenedores
docker compose down

# Reiniciar completamente (eliminar datos)
docker compose down -v
```

### Sin Docker (desarrollo local)

Asegúrate de tener MariaDB ejecutándose en `localhost:3306` con:
- Base de datos: `biblioteca`
- Usuario: `biblioteca`
- Contraseña: `biblioteca`

Luego:
```bash
./mvnw spring-boot:run
```

## Ejecutar Tests

Los tests utilizan **H2 en memoria** con el perfil `test` (definido en `src/test/resources/application-test.properties`).

```bash
# Ejecutar todos los tests
./mvnw test

# Ejecutar solo tests de repositorio
./mvnw test -Dtest="*RepositoryTest"

# Sin JDK local: ejecutar los tests dentro de un contenedor
docker run --rm -v "$(pwd)":/app -w /app eclipse-temurin:25-jdk sh mvnw test
```

Tests incluidos:

- `AppBackendP1ApplicationTests`: el contexto de Spring arranca.
- `LibroRepositoryTest` y `PrestamoRepositoryTest` (`@DataJpaTest`): relación N:M libro–autor, consultas derivadas y contadores.
- `BibliotecaControllerTest` (MockMvc): todas las páginas responden 200, alta de libro válida, errores de validación y borrado bloqueado de un libro con préstamos.

## Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SPRING_DATASOURCE_URL` | `jdbc:mariadb://localhost:3306/biblioteca` | URL de conexión a MariaDB |
| `SPRING_DATASOURCE_USERNAME` | `biblioteca` | Usuario de base de datos |
| `SPRING_DATASOURCE_PASSWORD` | `biblioteca` | Contraseña de base de datos |
| `SPRING_JPA_HIBERNATE_DDL_AUTO` | `validate` | Estrategia de DDL (validate, create, update) |

## Rutas de la Aplicación

### Panel Principal
- `GET /` – Página de inicio

### Gestión de Libros
- `GET /libros` – Listado de libros
- `GET /libros/nuevo` – Formulario crear libro
- `POST /libros` – Guardar nuevo libro
- `GET /libros/{id}/editar` – Formulario editar libro
- `POST /libros/{id}/editar` – Guardar cambios en libro
- `POST /libros/{id}/eliminar` – Eliminar libro

### Gestión de Usuarios
- `GET /usuarios` – Listado de usuarios
- `GET /usuarios/nuevo` – Formulario crear usuario
- `POST /usuarios` – Guardar nuevo usuario
- `GET /usuarios/{id}/editar` – Formulario editar usuario
- `POST /usuarios/{id}/editar` – Guardar cambios en usuario
- `POST /usuarios/{id}/eliminar` – Eliminar usuario

### Gestión de Préstamos
- `GET /prestamos` – Listado de préstamos
- `GET /prestamos/nuevo` – Formulario crear préstamo
- `POST /prestamos` – Guardar nuevo préstamo
- `POST /prestamos/{id}/devolver` – Registrar devolución

### Gestión de Autores
- `GET /autores` – Listado de autores
- `GET /autores/nuevo` – Formulario crear autor
- `POST /autores` – Guardar nuevo autor

### Rutas Útiles
- `GET /hello` – Prueba de conectividad

## Datos de Ejemplo

La base de datos se inicializa automáticamente con:
- **5 usuarios**: Lucía García, Marc Puig, Andrea Valero, Javier Martín, Sara Fernández
- **8 libros**: Cien años de soledad, Don Quijote, La casa de los espíritus, La sombra del viento, etc.
- **5 autores**: Gabriel García Márquez, Miguel de Cervantes, Isabel Allende, Carlos Ruiz Zafón, Arturo Pérez-Reverte
- **6 préstamos**: Con varios estados (ACTIVO, DEVUELTO, RETRASADO)

Los datos se cargan desde `db/init.sql` al crear el contenedor MariaDB.

## Notas Importantes

- **Validación de esquema**: `spring.jpa.hibernate.ddl-auto=validate` – JPA solo valida que el esquema coincida con las entidades. El esquema se crea en `db/init.sql`.
- **Codificación**: Base de datos con UTF-8 (`utf8mb4_unicode_ci`) para soporte completo de caracteres acentuados.
- **Tests**: Utilizan H2 en memoria sin requerir MariaDB. Los tests de repositorio incluyen relaciones N:M y operaciones CRUD completas.
- **Multi-stage Docker**: El Dockerfile cachea las dependencias Maven para compilaciones más rápidas.

## Troubleshooting

### "Port 3306 already in use"
```bash
# Parar contenedores existentes
docker compose down

# O usar un puerto diferente en docker-compose.yml
```

### Tests fallan en H2
Asegúrate de que `src/test/resources/application-test.properties` existe y contiene la configuración H2.

### Cambios en el esquema no se reflejan
Como `ddl-auto=validate`, debes:
1. Eliminar el volumen: `docker compose down -v`
2. Reiniciar: `docker compose up -d --build`

Esto recrea la base de datos desde `db/init.sql`.
