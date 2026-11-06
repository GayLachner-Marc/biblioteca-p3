package com.serverside.appbackendp1.repository;

import com.serverside.appbackendp1.model.EstadoPrestamo;
import com.serverside.appbackendp1.model.Libro;
import com.serverside.appbackendp1.model.Prestamo;
import com.serverside.appbackendp1.model.Usuario;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@ActiveProfiles("test")
class PrestamoRepositoryTest {

    @Autowired
    private PrestamoRepository prestamoRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private LibroRepository libroRepository;

    @Test
    void testCrearUsuarioLibroPrestamoYComprobarCountByEstado() {
        // Arrange
        Usuario usuario = new Usuario();
        usuario.setNombre("Carlos");
        usuario.setApellidos("García López");
        usuario.setEmail("carlos.garcia@example.com");
        usuario.setTelefono("600123456");
        usuario.setFechaAlta(LocalDate.of(2026, 9, 1));
        usuarioRepository.save(usuario);

        Libro libro = new Libro();
        libro.setTitulo("El Principito");
        libro.setIsbn("978-8532530787");
        libro.setEditorial("Salamandra");
        libro.setAnioPublicacion(1943);
        libro.setEjemplaresDisponibles(2);
        libroRepository.save(libro);

        Prestamo prestamo = new Prestamo();
        prestamo.setUsuario(usuario);
        prestamo.setLibro(libro);
        prestamo.setFechaPrestamo(LocalDate.of(2026, 9, 15));
        prestamo.setFechaDevolucionPrevista(LocalDate.of(2026, 9, 29));
        prestamo.setEstado(EstadoPrestamo.ACTIVO);
        prestamoRepository.save(prestamo);

        // Act
        long countActivos = prestamoRepository.countByEstado(EstadoPrestamo.ACTIVO);
        long countDevueltos = prestamoRepository.countByEstado(EstadoPrestamo.DEVUELTO);

        // Assert
        assertEquals(1, countActivos);
        assertEquals(0, countDevueltos);
    }

    @Test
    void testExistsByLibroId() {
        // Arrange
        Usuario usuario = new Usuario();
        usuario.setNombre("María");
        usuario.setApellidos("Pérez Rodríguez");
        usuario.setEmail("maria.perez@example.com");
        usuario.setFechaAlta(LocalDate.of(2026, 9, 1));
        usuarioRepository.save(usuario);

        Libro libro = new Libro();
        libro.setTitulo("Don Quijote");
        libro.setIsbn("978-8420412146");
        libro.setEditorial("Alfaguara");
        libro.setAnioPublicacion(1605);
        libro.setEjemplaresDisponibles(1);
        Libro libroGuardado = libroRepository.save(libro);

        Prestamo prestamo = new Prestamo();
        prestamo.setUsuario(usuario);
        prestamo.setLibro(libroGuardado);
        prestamo.setFechaPrestamo(LocalDate.of(2026, 9, 1));
        prestamo.setFechaDevolucionPrevista(LocalDate.of(2026, 9, 15));
        prestamo.setEstado(EstadoPrestamo.ACTIVO);
        prestamoRepository.save(prestamo);

        // Act & Assert
        assertTrue(prestamoRepository.existsByLibroId(libroGuardado.getId()));
        assertFalse(prestamoRepository.existsByLibroId(999L));
    }

    @Test
    void testExistsByUsuarioId() {
        // Arrange
        Usuario usuario = new Usuario();
        usuario.setNombre("Juan");
        usuario.setApellidos("Martínez López");
        usuario.setEmail("juan.martinez@example.com");
        usuario.setFechaAlta(LocalDate.of(2026, 9, 1));
        Usuario usuarioGuardado = usuarioRepository.save(usuario);

        Libro libro = new Libro();
        libro.setTitulo("La casa de los espíritus");
        libro.setIsbn("978-8401352836");
        libro.setEditorial("Plaza & Janés");
        libro.setAnioPublicacion(1982);
        libro.setEjemplaresDisponibles(2);
        libroRepository.save(libro);

        Prestamo prestamo = new Prestamo();
        prestamo.setUsuario(usuarioGuardado);
        prestamo.setLibro(libro);
        prestamo.setFechaPrestamo(LocalDate.of(2026, 9, 5));
        prestamo.setFechaDevolucionPrevista(LocalDate.of(2026, 9, 19));
        prestamo.setEstado(EstadoPrestamo.ACTIVO);
        prestamoRepository.save(prestamo);

        // Act & Assert
        assertTrue(prestamoRepository.existsByUsuarioId(usuarioGuardado.getId()));
        assertFalse(prestamoRepository.existsByUsuarioId(999L));
    }

    @Test
    void testFindTop5ByOrderByFechaPrestamoDescIdDesc() {
        // Arrange
        Usuario usuario = new Usuario();
        usuario.setNombre("Pedro");
        usuario.setApellidos("Sánchez Ruiz");
        usuario.setEmail("pedro.sanchez@example.com");
        usuario.setFechaAlta(LocalDate.of(2026, 9, 1));
        usuarioRepository.save(usuario);

        Libro libro = new Libro();
        libro.setTitulo("La sombra del viento");
        libro.setIsbn("978-8408163381");
        libro.setEditorial("Planeta");
        libro.setAnioPublicacion(2001);
        libro.setEjemplaresDisponibles(3);
        libroRepository.save(libro);

        // Crear 6 préstamos con diferentes fechas
        for (int i = 1; i <= 6; i++) {
            Prestamo prestamo = new Prestamo();
            prestamo.setUsuario(usuario);
            prestamo.setLibro(libro);
            prestamo.setFechaPrestamo(LocalDate.of(2026, 9, i));
            prestamo.setFechaDevolucionPrevista(LocalDate.of(2026, 9, i + 14));
            prestamo.setEstado(EstadoPrestamo.ACTIVO);
            prestamoRepository.save(prestamo);
        }

        // Act
        List<Prestamo> top5 = prestamoRepository.findTop5ByOrderByFechaPrestamoDescIdDesc();

        // Assert
        assertEquals(5, top5.size());
        // Los 5 más recientes deben ser los préstamos 2-6 (del 2 al 6 de septiembre)
        assertTrue(top5.get(0).getFechaPrestamo().getDayOfMonth() >= top5.get(4).getFechaPrestamo().getDayOfMonth());
    }
}
