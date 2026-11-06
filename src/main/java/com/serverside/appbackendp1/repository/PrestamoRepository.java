package com.serverside.appbackendp1.repository;
import com.serverside.appbackendp1.model.EstadoPrestamo;
import com.serverside.appbackendp1.model.Prestamo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import com.serverside.appbackendp1.model.Libro;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface PrestamoRepository extends JpaRepository<Prestamo, Long> {

    List<Prestamo> findAllByOrderByFechaPrestamoDescIdDesc();

    List<Prestamo> findTop5ByOrderByFechaPrestamoDescIdDesc();

    long countByEstado(EstadoPrestamo estado);

    boolean existsByLibroId(Long libroId);

    boolean existsByUsuarioId(Long usuarioId);

    @Query("""
    SELECT CASE WHEN COUNT(p) > 0 THEN true ELSE false END
    FROM Prestamo p
    WHERE p.usuario.id = :usuarioId
      AND p.libro.id = :libroId
      AND p.estado IN :estados
    """)
    boolean existePrestamoPorUsuarioLibroYEstados(
            @Param("usuarioId") Long usuarioId,
            @Param("libroId") Long libroId,
            @Param("estados") List<EstadoPrestamo> estados
    );
    // Consulta para obtener los libros más prestados
    @Query("""
        SELECT p.libro 
        FROM Prestamo p 
        GROUP BY p.libro 
        ORDER BY COUNT(p) DESC
    """)
    List<Libro> findLibrosMasPrestados(org.springframework.data.domain.Pageable pageable);
}
