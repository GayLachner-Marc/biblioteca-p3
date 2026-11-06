package com.serverside.appbackendp1.controller;

import com.serverside.appbackendp1.model.Autor;
import com.serverside.appbackendp1.model.Libro;
import com.serverside.appbackendp1.repository.AutorRepository;
import com.serverside.appbackendp1.service.LibroService;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.HashSet;
import java.util.List;
import java.util.Optional;

@Controller
@RequestMapping("/libros")
public class LibroController {

    private final LibroService libroService;
    private final AutorRepository autorRepository;

    public LibroController(LibroService libroService, AutorRepository autorRepository) {
        this.libroService = libroService;
        this.autorRepository = autorRepository;
    }


    @GetMapping
    public String listar(
            @RequestParam(name = "q", defaultValue = "") String texto,
            @RequestParam(name = "disponibilidad", defaultValue = "todos")
            String disponibilidad,
            Model model) {

        model.addAttribute(
                "libros",
                libroService.buscarCatalogo(texto, disponibilidad)
        );

        model.addAttribute("q", texto);
        model.addAttribute("disponibilidad", disponibilidad);

        return "libros/lista";
    }


    @GetMapping("/nuevo")
    public String nuevo(Model model) {
        prepararFormulario(model, new Libro(), List.of(), true);
        return "libros/formulario";
    }

    @PostMapping
    public String crearEnColeccion(@Valid @ModelAttribute("libro") Libro libro, BindingResult result,
                                   @RequestParam(name = "autorIds", required = false) List<Long> autorIds,
                                   Model model, RedirectAttributes redirect) {
        return crear(libro, result, autorIds, model, redirect);
    }

    @PostMapping("/nuevo")
    public String crear(@Valid @ModelAttribute("libro") Libro libro, BindingResult result,
                        @RequestParam(name = "autorIds", required = false) List<Long> autorIds,
                        Model model, RedirectAttributes redirect) {
        if (libroService.isbnDuplicado(libro.getIsbn(), null)) {
            result.rejectValue("isbn", "isbn.duplicado", "Ya existe un libro con ese ISBN");
        }
        if (result.hasErrors()) {
            prepararFormulario(model, libro, autorIds, true);
            return "libros/formulario";
        }
        libro.setAutores(new HashSet<>(autorRepository.findAllById(idsSeguros(autorIds))));
        libroService.guardar(libro);
        redirect.addFlashAttribute("exito", "Libro creado correctamente");
        return "redirect:/libros";
    }

    @GetMapping("/{id}/editar")
    public String editar(@PathVariable Long id, Model model, RedirectAttributes redirect) {
        Optional<Libro> libro = libroService.buscar(id);
        if (libro.isEmpty()) {
            redirect.addFlashAttribute("error", "El libro no existe");
            return "redirect:/libros";
        }
        List<Long> seleccionados = libro.get().getAutores().stream().map(Autor::getId).toList();
        prepararFormulario(model, libro.get(), seleccionados, false);
        return "libros/formulario";
    }

    @PostMapping("/{id}/editar")
    public String actualizar(@PathVariable Long id, @Valid @ModelAttribute("libro") Libro libro,
                             BindingResult result,
                             @RequestParam(name = "autorIds", required = false) List<Long> autorIds,
                             Model model, RedirectAttributes redirect) {
        Optional<Libro> existente = libroService.buscar(id);
        if (existente.isEmpty()) {
            redirect.addFlashAttribute("error", "El libro no existe");
            return "redirect:/libros";
        }
        if (libroService.isbnDuplicado(libro.getIsbn(), id)) {
            result.rejectValue("isbn", "isbn.duplicado", "Ya existe un libro con ese ISBN");
        }
        if (result.hasErrors()) {
            libro.setId(id);
            prepararFormulario(model, libro, autorIds, false);
            return "libros/formulario";
        }
        Libro destino = existente.get();
        destino.setTitulo(libro.getTitulo());
        destino.setIsbn(libro.getIsbn());
        destino.setEditorial(libro.getEditorial());
        destino.setAnioPublicacion(libro.getAnioPublicacion());
        destino.setEjemplaresDisponibles(libro.getEjemplaresDisponibles());
        destino.setAutores(new HashSet<>(autorRepository.findAllById(idsSeguros(autorIds))));
        libroService.guardar(destino);
        redirect.addFlashAttribute("exito", "Libro actualizado correctamente");
        return "redirect:/libros";
    }

    @PostMapping("/{id}/eliminar")
    public String eliminar(@PathVariable Long id, RedirectAttributes redirect) {
        try {
            libroService.eliminar(id);
            redirect.addFlashAttribute("exito", "Libro eliminado correctamente");
        } catch (IllegalStateException e) {
            redirect.addFlashAttribute("error", e.getMessage());
        }
        return "redirect:/libros";
    }

    private void prepararFormulario(Model model, Libro libro, List<Long> seleccionados, boolean esNuevo) {
        model.addAttribute("libro", libro);
        model.addAttribute("autoresDisponibles", autorRepository.findAllByOrderByNombreAsc());
        model.addAttribute("autorIdsSeleccionados", idsSeguros(seleccionados));
        model.addAttribute("esNuevo", esNuevo);
    }

    private static List<Long> idsSeguros(List<Long> ids) {
        return ids == null ? List.of() : ids;
    }
}
