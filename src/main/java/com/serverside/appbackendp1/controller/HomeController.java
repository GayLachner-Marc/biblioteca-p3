package com.serverside.appbackendp1.controller;

import com.serverside.appbackendp1.repository.AutorRepository;
import com.serverside.appbackendp1.repository.LibroRepository;
import com.serverside.appbackendp1.repository.UsuarioRepository;
import com.serverside.appbackendp1.service.PrestamoService;
import com.serverside.appbackendp1.model.Libro;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import com.serverside.appbackendp1.model.Libro;
import java.util.List;


@Controller
public class HomeController {

    private final LibroRepository libroRepository;
    private final UsuarioRepository usuarioRepository;
    private final AutorRepository autorRepository;
    private final PrestamoService prestamoService;

    public HomeController(LibroRepository libroRepository, UsuarioRepository usuarioRepository,
                          AutorRepository autorRepository, PrestamoService prestamoService) {
        this.libroRepository = libroRepository;
        this.usuarioRepository = usuarioRepository;
        this.autorRepository = autorRepository;
        this.prestamoService = prestamoService;
    }

    @GetMapping("/")
    public String inicio(Model model) {
        prestamoService.actualizarRetrasados();
        model.addAttribute("totalLibros", libroRepository.count());
        model.addAttribute("totalUsuarios", usuarioRepository.count());
        model.addAttribute("totalAutores", autorRepository.count());
        model.addAttribute("prestamosActivos", prestamoService.contarActivos());
        model.addAttribute("prestamosRetrasados", prestamoService.contarRetrasados());
        model.addAttribute("ultimosPrestamos", prestamoService.ultimos());
        model.addAttribute("ejemplaresDisponibles", libroRepository.contarEjemplaresDisponibles());

        // Obtener los 5 libros más prestados
        List<Libro> topLibros = prestamoService.obtenerTop5Libros();
        model.addAttribute("topLibros", topLibros);

        return "index";
    }
}
