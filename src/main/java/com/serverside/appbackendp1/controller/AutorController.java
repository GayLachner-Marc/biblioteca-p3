package com.serverside.appbackendp1.controller;

import com.serverside.appbackendp1.model.Autor;
import com.serverside.appbackendp1.repository.AutorRepository;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/autores")
public class AutorController {

    private final AutorRepository autorRepository;

    public AutorController(AutorRepository autorRepository) {
        this.autorRepository = autorRepository;
    }

    @GetMapping
    @Transactional(readOnly = true)
    public String listar(Model model) {
        var autores = autorRepository.findAllByOrderByNombreAsc();
        autores.forEach(a -> a.getLibros().size());
        model.addAttribute("autores", autores);
        return "autores/lista";
    }

    @GetMapping("/nuevo")
    public String nuevo(Model model) {
        model.addAttribute("autor", new Autor());
        return "autores/formulario";
    }

    @PostMapping
    public String crear(@Valid @ModelAttribute("autor") Autor autor, BindingResult result,
                        RedirectAttributes redirect) {
        if (result.hasErrors()) {
            return "autores/formulario";
        }
        autorRepository.save(autor);
        redirect.addFlashAttribute("exito", "Autor creado correctamente");
        return "redirect:/autores";
    }
}
