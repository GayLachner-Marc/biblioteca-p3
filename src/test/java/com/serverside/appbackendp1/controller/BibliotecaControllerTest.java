package com.serverside.appbackendp1.controller;

import com.serverside.appbackendp1.model.EstadoPrestamo;
import com.serverside.appbackendp1.model.Libro;
import com.serverside.appbackendp1.model.Prestamo;
import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.LibroRepository;
import com.serverside.appbackendp1.repository.PrestamoRepository;
import com.serverside.appbackendp1.repository.UsuarioRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class BibliotecaControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private LibroRepository libroRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private PrestamoRepository prestamoRepository;

    @Test
    void lasPaginasPrincipalesResponden() throws Exception {
        for (String ruta : new String[]{"/", "/libros", "/libros/nuevo", "/usuarios", "/usuarios/nuevo",
                "/prestamos", "/prestamos/nuevo", "/autores", "/autores/nuevo"}) {
            mockMvc.perform(get(ruta)).andExpect(status().isOk());
        }
        mockMvc.perform(get("/hello")).andExpect(content().string("Hello World!"));
    }

    @Test
    void crearLibroValidoRedirigeYLoGuarda() throws Exception {
        mockMvc.perform(post("/libros")
                        .param("titulo", "Libro de prueba")
                        .param("isbn", "TEST-0001")
                        .param("editorial", "Editorial")
                        .param("anioPublicacion", "2020")
                        .param("ejemplaresDisponibles", "2"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/libros"));

        assertThat(libroRepository.existsByIsbn("TEST-0001")).isTrue();
    }

    @Test
    void crearLibroSinTituloMuestraErrores() throws Exception {
        mockMvc.perform(post("/libros")
                        .param("titulo", "")
                        .param("isbn", "TEST-0002")
                        .param("ejemplaresDisponibles", "1"))
                .andExpect(status().isOk())
                .andExpect(model().attributeHasFieldErrors("libro", "titulo"));

        assertThat(libroRepository.existsByIsbn("TEST-0002")).isFalse();
    }

    @Test
    void eliminarLibroConPrestamosMuestraErrorSinBorrar() throws Exception {
        Libro libro = new Libro();
        libro.setTitulo("Prestado");
        libro.setIsbn("TEST-0003");
        libro.setEjemplaresDisponibles(1);
        libroRepository.save(libro);

        Usuario usuario = new Usuario();
        usuario.setNombre("Ana");
        usuario.setApellidos("Prueba");
        usuario.setEmail("ana.prueba@example.com");
        usuarioRepository.save(usuario);

        Prestamo prestamo = new Prestamo();
        prestamo.setLibro(libro);
        prestamo.setUsuario(usuario);
        prestamo.setEstado(EstadoPrestamo.ACTIVO);
        prestamo.setFechaPrestamo(LocalDate.now());
        prestamo.setFechaDevolucionPrevista(LocalDate.now().plusDays(15));
        prestamoRepository.save(prestamo);

        mockMvc.perform(post("/libros/{id}/eliminar", libro.getId()))
                .andExpect(status().is3xxRedirection())
                .andExpect(flash().attributeExists("error"));

        assertThat(libroRepository.existsById(libro.getId())).isTrue();
    }
}
