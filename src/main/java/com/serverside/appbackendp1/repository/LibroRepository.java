

package com.serverside.appbackendp1.repository;

import com.serverside.appbackendp1.model.Libro;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface LibroRepository extends JpaRepository<Libro, Long> {

    boolean existsByIsbnAndIdNot(String isbn, Long id);

    boolean existsByIsbn(String isbn);

    List<Libro> findAllByOrderByTituloAsc();

    @Query("SELECT COALESCE(SUM(l.ejemplaresDisponibles), 0) FROM Libro l")
    long contarEjemplaresDisponibles();

    @Query("""
        SELECT DISTINCT l
        FROM Libro l
        LEFT JOIN l.autores a
        WHERE (
            :texto = ''
            OR LOWER(l.titulo) LIKE LOWER(CONCAT('%', :texto, '%'))
            OR LOWER(l.isbn) LIKE LOWER(CONCAT('%', :texto, '%'))
            OR LOWER(a.nombre) LIKE LOWER(CONCAT('%', :texto, '%'))
        )
        AND (
            :disponibilidad = 'todos'
            OR (:disponibilidad = 'disponibles'
                AND l.ejemplaresDisponibles > 0)
            OR (:disponibilidad = 'agotados'
                AND l.ejemplaresDisponibles = 0)
        )
        ORDER BY l.titulo ASC
        """)
    List<Libro> buscarCatalogo(
            @Param("texto") String texto,
            @Param("disponibilidad") String disponibilidad
    );
}

