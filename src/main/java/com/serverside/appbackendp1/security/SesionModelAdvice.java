package com.serverside.appbackendp1.security;

import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

/**
 * Expone en todas las vistas quién ha iniciado sesión y si es administrador,
 * para mostrar el botón de cerrar sesión y ocultar acciones a quien no es ADMIN.
 */
@ControllerAdvice
public class SesionModelAdvice {

    @ModelAttribute("usuarioActual")
    public String usuarioActual() {
        Authentication auth = autenticacion();
        return auth == null ? null : auth.getName();
    }

    @ModelAttribute("esAdmin")
    public boolean esAdmin() {
        Authentication auth = autenticacion();
        return auth != null && auth.getAuthorities().stream()
                .anyMatch(a -> "ROLE_ADMIN".equals(a.getAuthority()));
    }

    private Authentication autenticacion() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || auth instanceof AnonymousAuthenticationToken) {
            return null;
        }
        return auth;
    }
}
