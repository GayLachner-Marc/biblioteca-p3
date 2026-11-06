package com.serverside.appbackendp1.controller;

import com.serverside.appbackendp1.model.Libro;
import com.serverside.appbackendp1.model.Prestamo;
import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.LibroRepository;
import com.serverside.appbackendp1.service.PrestamoService;
import com.serverside.appbackendp1.service.UsuarioService;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/prestamos")
public class PrestamoController {

    private final PrestamoService prestamoService;
    private final UsuarioService usuarioService;
    private final LibroRepository libroRepository;

    public PrestamoController(PrestamoService prestamoService, UsuarioService usuarioService,
                              LibroRepository libroRepository) {
        this.prestamoService = prestamoService;
        this.usuarioService = usuarioService;
        this.libroRepository = libroRepository;
    }

    @InitBinder("prestamo")
    void configurarBinder(WebDataBinder binder) {
        binder.setAllowedFields("fechaPrestamo", "fechaDevolucionPrevista");
    }

    @GetMapping
    public String listar(Model model) {
        model.addAttribute("prestamos", prestamoService.listar());
        return "prestamos/lista";
    }

    @GetMapping("/nuevo")
    public String nuevo(Model model) {
        model.addAttribute("prestamo", new Prestamo());
        return formulario(model);
    }

    @PostMapping
    public String crear(@ModelAttribute("prestamo") Prestamo prestamo, BindingResult result,
                        @RequestParam(required = false) Long usuarioId,
                        @RequestParam(required = false) Long libroId,
                        Model model, RedirectAttributes ra) {
        model.addAttribute("usuarioId", usuarioId);
        model.addAttribute("libroId", libroId);

        Usuario usuario = usuarioId == null ? null : usuarioService.buscarPorId(usuarioId).orElse(null);
        Libro libro = libroId == null ? null : libroRepository.findById(libroId).orElse(null);

        if (usuario == null) {
            result.rejectValue("usuario", "requerido", "Selecciona un usuario");
        }
        if (libro == null) {
            result.rejectValue("libro", "requerido", "Selecciona un libro");
        }
        if (!result.hasFieldErrors("fechaPrestamo") && prestamo.getFechaPrestamo() == null) {
            result.rejectValue("fechaPrestamo", "requerido", "La fecha de préstamo es obligatoria");
        }
        if (!result.hasFieldErrors("fechaDevolucionPrevista") && prestamo.getFechaDevolucionPrevista() == null) {
            result.rejectValue("fechaDevolucionPrevista", "requerido",
                    "La fecha de devolución prevista es obligatoria");
        }
        if (prestamo.getFechaPrestamo() != null && prestamo.getFechaDevolucionPrevista() != null
                && prestamo.getFechaDevolucionPrevista().isBefore(prestamo.getFechaPrestamo())) {
            result.rejectValue("fechaDevolucionPrevista", "rango",
                    "La fecha prevista no puede ser anterior a la fecha de préstamo");
        }
        if (libro != null && (libro.getEjemplaresDisponibles() == null || libro.getEjemplaresDisponibles() <= 0)) {
            result.rejectValue("libro", "sinStock", "No hay ejemplares disponibles de este libro");
        }
        if (result.hasErrors()) {
            return formulario(model);
        }
        try {
            prestamoService.crear(usuario, libro, prestamo.getFechaPrestamo(), prestamo.getFechaDevolucionPrevista());
        } catch (IllegalStateException e) {
            result.rejectValue("libro", "prestamoInvalido", e.getMessage());
            return formulario(model);
        } catch (DataIntegrityViolationException e) {
            result.rejectValue("libro", "integridad", "No se pudo registrar el préstamo");
            return formulario(model);
        }
        ra.addFlashAttribute("exito", "Préstamo registrado correctamente");
        return "redirect:/prestamos";
    }

    @PostMapping("/{id}/devolver")
    public String devolver(@PathVariable Long id, RedirectAttributes ra) {
        if (!prestamoService.existe(id)) {
            ra.addFlashAttribute("error", "El préstamo solicitado no existe");
        } else if (prestamoService.devolver(id)) {
            ra.addFlashAttribute("exito", "Préstamo marcado como devuelto");
        } else {
            ra.addFlashAttribute("error", "El préstamo ya estaba devuelto");
        }
        return "redirect:/prestamos";
    }

    private String formulario(Model model) {
        model.addAttribute("usuarios", usuarioService.listar());
        model.addAttribute("libros", libroRepository.findAllByOrderByTituloAsc());
        return "prestamos/formulario";
    }
}
