package com.serverside.appbackendp1.repository;

import com.serverside.appbackendp1.model.Autor;
import com.serverside.appbackendp1.model.Libro;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.test.context.ActiveProfiles;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@ActiveProfiles("test")
class LibroRepositoryTest {

    @Autowired
    private LibroRepository libroRepository;

    @Autowired
    private AutorRepository autorRepository;

    @Test
    void testGuardarLibroConDosAutoresYRecuperarConSusAutores() {
        // Arrange
        Autor autor1 = new Autor();
        autor1.setNombre("Gabriel García Márquez");
        autor1.setNacionalidad("Colombiana");
        autorRepository.save(autor1);

        Autor autor2 = new Autor();
        autor2.setNombre("Miguel de Cervantes");
        autor2.setNacionalidad("Española");
        autorRepository.save(autor2);

        Libro libro = new Libro();
        libro.setTitulo("El Quijote");
        libro.setIsbn("978-8420412146");
        libro.setEditorial("Alfaguara");
        libro.setAnioPublicacion(1605);
        libro.setEjemplaresDisponibles(2);
        libro.getAutores().add(autor1);
        libro.getAutores().add(autor2);

        // Act
        Libro libroGuardado = libroRepository.save(libro);
        Libro libroRecuperado = libroRepository.findById(libroGuardado.getId()).orElse(null);

        // Assert
        assertNotNull(libroRecuperado);
        assertEquals("El Quijote", libroRecuperado.getTitulo());
        assertEquals(2, libroRecuperado.getAutores().size());
        assertTrue(libroRecuperado.getAutores().stream()
                .anyMatch(a -> a.getNombre().equals("Gabriel García Márquez")));
        assertTrue(libroRecuperado.getAutores().stream()
                .anyMatch(a -> a.getNombre().equals("Miguel de Cervantes")));
    }

    @Test
    void testExistsByIsbn() {
        // Arrange
        Libro libro = new Libro();
        libro.setTitulo("Cien años de soledad");
        libro.setIsbn("978-8497592208");
        libro.setEditorial("Debolsillo");
        libro.setAnioPublicacion(1967);
        libro.setEjemplaresDisponibles(3);
        libroRepository.save(libro);

        // Act & Assert
        assertTrue(libroRepository.existsByIsbn("978-8497592208"));
        assertFalse(libroRepository.existsByIsbn("999-9999999999"));
    }

    @Test
    void testFindAllByOrderByTituloAsc() {
        // Arrange
        Libro libro1 = new Libro();
        libro1.setTitulo("Zamora");
        libro1.setIsbn("ISBN-001");
        libro1.setEjemplaresDisponibles(1);
        libroRepository.save(libro1);

        Libro libro2 = new Libro();
        libro2.setTitulo("Alineación");
        libro2.setIsbn("ISBN-002");
        libro2.setEjemplaresDisponibles(1);
        libroRepository.save(libro2);

        Libro libro3 = new Libro();
        libro3.setTitulo("Museo");
        libro3.setIsbn("ISBN-003");
        libro3.setEjemplaresDisponibles(1);
        libroRepository.save(libro3);

        // Act
        List<Libro> librosOrdenados = libroRepository.findAllByOrderByTituloAsc();

        // Assert
        assertEquals(3, librosOrdenados.size());
        assertEquals("Alineación", librosOrdenados.get(0).getTitulo());
        assertEquals("Museo", librosOrdenados.get(1).getTitulo());
        assertEquals("Zamora", librosOrdenados.get(2).getTitulo());
    }
}
