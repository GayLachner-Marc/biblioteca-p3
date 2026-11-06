package com.serverside.appbackendp1.controller;

import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.service.UsuarioService;
import jakarta.validation.Valid;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/usuarios")
public class UsuarioController {

    private static final String REDIRECT_LISTA = "redirect:/usuarios";

    private final UsuarioService usuarioService;

    public UsuarioController(UsuarioService usuarioService) {
        this.usuarioService = usuarioService;
    }

    @InitBinder("usuario")
    void configurarBinder(WebDataBinder binder) {
        binder.setDisallowedFields("id", "prestamos");
    }

    @GetMapping
    public String listar(Model model) {
        model.addAttribute("usuarios", usuarioService.listar());
        return "usuarios/lista";
    }

    @GetMapping("/nuevo")
    public String nuevo(Model model) {
        model.addAttribute("usuario", new Usuario());
        return "usuarios/formulario";
    }

    @PostMapping
    public String crear(@Valid @ModelAttribute("usuario") Usuario usuario, BindingResult result,
                        RedirectAttributes ra) {
        normalizar(usuario);
        usuario.setId(null);
        validarEmail(usuario, result);
        if (result.hasErrors()) {
            return "usuarios/formulario";
        }
        try {
            usuarioService.guardar(usuario);
        } catch (DataIntegrityViolationException e) {
            result.rejectValue("email", "duplicado", "Ya existe un usuario con ese email");
            return "usuarios/formulario";
        }
        ra.addFlashAttribute("exito", "Usuario creado correctamente");
        return REDIRECT_LISTA;
    }

    @GetMapping("/{id}/editar")
    public String editar(@PathVariable Long id, Model model, RedirectAttributes ra) {
        return usuarioService.buscarPorId(id).map(u -> {
            model.addAttribute("usuario", u);
            return "usuarios/formulario";
        }).orElseGet(() -> noEncontrado(ra));
    }

    @PostMapping("/{id}/editar")
    public String actualizar(@PathVariable Long id, @Valid @ModelAttribute("usuario") Usuario usuario,
                             BindingResult result, RedirectAttributes ra) {
        if (usuarioService.buscarPorId(id).isEmpty()) {
            return noEncontrado(ra);
        }
        normalizar(usuario);
        usuario.setId(id);
        validarEmail(usuario, result);
        if (result.hasErrors()) {
            return "usuarios/formulario";
        }
        try {
            usuarioService.guardar(usuario);
        } catch (DataIntegrityViolationException e) {
            result.rejectValue("email", "duplicado", "Ya existe un usuario con ese email");
            return "usuarios/formulario";
        }
        ra.addFlashAttribute("exito", "Usuario actualizado correctamente");
        return REDIRECT_LISTA;
    }

    @PostMapping("/{id}/eliminar")
    public String eliminar(@PathVariable Long id, RedirectAttributes ra) {
        if (usuarioService.buscarPorId(id).isEmpty()) {
            return noEncontrado(ra);
        }
        try {
            usuarioService.eliminar(id);
            ra.addFlashAttribute("exito", "Usuario eliminado correctamente");
        } catch (IllegalStateException | DataIntegrityViolationException e) {
            ra.addFlashAttribute("error", "No se puede eliminar el usuario porque tiene préstamos asociados");
        }
        return REDIRECT_LISTA;
    }

    private void normalizar(Usuario u) {
        if (u.getEmail() != null) {
            u.setEmail(u.getEmail().trim());
        }
        if (u.getTelefono() != null && u.getTelefono().isBlank()) {
            u.setTelefono(null);
        }
    }

    private void validarEmail(Usuario usuario, BindingResult result) {
        if (!result.hasFieldErrors("email") && usuarioService.emailDuplicado(usuario.getEmail(), usuario.getId())) {
            result.rejectValue("email", "duplicado", "Ya existe un usuario con ese email");
        }
    }

    private String noEncontrado(RedirectAttributes ra) {
        ra.addFlashAttribute("error", "El usuario solicitado no existe");
        return REDIRECT_LISTA;
    }
}
