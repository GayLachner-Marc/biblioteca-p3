package com.serverside.appbackendp1.service;

import com.serverside.appbackendp1.model.Libro;
import com.serverside.appbackendp1.repository.LibroRepository;
import com.serverside.appbackendp1.repository.PrestamoRepository;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class LibroService {

    private final LibroRepository libroRepository;
    private final PrestamoRepository prestamoRepository;

    public LibroService(LibroRepository libroRepository, PrestamoRepository prestamoRepository) {
        this.libroRepository = libroRepository;
        this.prestamoRepository = prestamoRepository;
    }

    @Transactional(readOnly = true)
    public List<Libro> listar() {
        List<Libro> libros = libroRepository.findAllByOrderByTituloAsc();
        // Inicializa los autores dentro de la transacción
        libros.forEach(l -> l.getAutores().size());
        return libros;
    }

    @Transactional(readOnly = true)
    public List<Libro> buscarCatalogo(String texto, String disponibilidad) {
        String textoNormalizado = texto == null ? "" : texto.trim();

        String filtro = disponibilidad == null
                ? "todos"
                : disponibilidad.trim().toLowerCase();

        if (!List.of("todos", "disponibles", "agotados").contains(filtro)) {
            filtro = "todos";
        }

        List<Libro> libros = libroRepository.buscarCatalogo(
                textoNormalizado,
                filtro
        );

        // Inicializa los autores dentro de la transacción.
        libros.forEach(l -> l.getAutores().size());

        return libros;
    }



    @Transactional(readOnly = true)
    public Optional<Libro> buscar(Long id) {
        Optional<Libro> libro = libroRepository.findById(id);
        libro.ifPresent(l -> l.getAutores().size());
        return libro;
    }

    @Transactional(readOnly = true)
    public boolean isbnDuplicado(String isbn, Long idActual) {
        if (isbn == null) {
            return false;
        }
        return idActual == null
                ? libroRepository.existsByIsbn(isbn)
                : libroRepository.existsByIsbnAndIdNot(isbn, idActual);
    }

    @Transactional
    public Libro guardar(Libro libro) {
        return libroRepository.save(libro);
    }

    /**
     * Elimina un libro. Lanza IllegalStateException con mensaje en español
     * si no se puede eliminar (tiene préstamos asociados).
     */
    @Transactional
    public void eliminar(Long id) {
        if (!libroRepository.existsById(id)) {
            throw new IllegalStateException("El libro no existe");
        }
        if (prestamoRepository.existsByLibroId(id)) {
            throw new IllegalStateException(
                    "No se puede eliminar el libro porque tiene préstamos asociados");
        }
        try {
            libroRepository.deleteById(id);
            libroRepository.flush();
        } catch (DataIntegrityViolationException e) {
            throw new IllegalStateException(
                    "No se puede eliminar el libro porque tiene datos asociados", e);
        }
    }
}
