package com.serverside.appbackendp1.service;

import com.serverside.appbackendp1.model.EstadoPrestamo;
import com.serverside.appbackendp1.model.Libro;
import com.serverside.appbackendp1.model.Prestamo;
import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.PrestamoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.data.domain.PageRequest;

import java.time.LocalDate;
import java.util.List;

@Service
public class PrestamoService {

    private final PrestamoRepository prestamoRepository;

    public PrestamoService(PrestamoRepository prestamoRepository) {
        this.prestamoRepository = prestamoRepository;
    }

    /** Marca como RETRASADO los préstamos ACTIVO cuya fecha prevista ya pasó. */
    @Transactional
    public void actualizarRetrasados() {
        LocalDate hoy = LocalDate.now();
        for (Prestamo p : prestamoRepository.findAll()) {
            if (p.getEstado() == EstadoPrestamo.ACTIVO && p.getFechaDevolucionPrevista() != null
                    && p.getFechaDevolucionPrevista().isBefore(hoy)) {
                p.setEstado(EstadoPrestamo.RETRASADO);
            }
        }
    }

    @Transactional
    public List<Prestamo> listar() {
        actualizarRetrasados();
        return prestamoRepository.findAllByOrderByFechaPrestamoDescIdDesc();
    }

    @Transactional
    public List<Prestamo> ultimos() {
        actualizarRetrasados();
        return prestamoRepository.findTop5ByOrderByFechaPrestamoDescIdDesc();
    }

    @Transactional(readOnly = true)
    public long contarActivos() {
        return prestamoRepository.countByEstado(EstadoPrestamo.ACTIVO)
                + prestamoRepository.countByEstado(EstadoPrestamo.RETRASADO);
    }

    @Transactional(readOnly = true)
    public long contarRetrasados() {
        return prestamoRepository.countByEstado(EstadoPrestamo.RETRASADO);
    }

    /** Crea el préstamo y descuenta un ejemplar del libro. El libro debe tener ejemplares disponibles. */
    @Transactional
    public Prestamo crear(Usuario usuario, Libro libro, LocalDate fechaPrestamo, LocalDate fechaPrevista) {
        if (prestamoRepository.existePrestamoPorUsuarioLibroYEstados(
                usuario.getId(),
                libro.getId(),
                List.of(EstadoPrestamo.ACTIVO, EstadoPrestamo.RETRASADO))) {

            throw new IllegalStateException(
                    "Este usuario ya tiene un préstamo activo de este libro");
        }

        if (libro.getEjemplaresDisponibles() == null || libro.getEjemplaresDisponibles() <= 0) {
            throw new IllegalStateException("No hay ejemplares disponibles de este libro");
        }
        libro.setEjemplaresDisponibles(libro.getEjemplaresDisponibles() - 1);
        Prestamo p = new Prestamo();
        p.setUsuario(usuario);
        p.setLibro(libro);
        p.setFechaPrestamo(fechaPrestamo);
        p.setFechaDevolucionPrevista(fechaPrevista);
        p.setEstado(EstadoPrestamo.ACTIVO);
        return prestamoRepository.save(p);
    }

    /** Devuelve true si se marcó como devuelto; false si no existe o ya estaba devuelto. */
    @Transactional
    public boolean devolver(Long id) {
        Prestamo p = prestamoRepository.findById(id).orElse(null);
        if (p == null || p.getEstado() == EstadoPrestamo.DEVUELTO) {
            return false;
        }
        p.setEstado(EstadoPrestamo.DEVUELTO);
        p.setFechaDevolucion(LocalDate.now());
        Libro libro = p.getLibro();
        libro.setEjemplaresDisponibles(libro.getEjemplaresDisponibles() + 1);
        return true;
    }

    @Transactional(readOnly = true)
    public boolean existe(Long id) {
        return prestamoRepository.existsById(id);
    }

    // Obtener los 5 libros más prestados

    @Transactional(readOnly = true)
    public List<Libro> obtenerTop5Libros() {
        // PageRequest.of(0, 5) significa: página 0, 5 elementos (los 5 primeros)
        return prestamoRepository.findLibrosMasPrestados(PageRequest.of(0, 5));
    }
}

