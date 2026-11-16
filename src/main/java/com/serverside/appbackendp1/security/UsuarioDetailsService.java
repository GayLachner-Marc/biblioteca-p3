package com.serverside.appbackendp1.security;

import com.serverside.appbackendp1.model.Rol;
import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.UsuarioRepository;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Carga los usuarios de la tabla usuarios (por email) con sus roles para Spring Security. */
@Service
public class UsuarioDetailsService implements UserDetailsService {

    private final UsuarioRepository usuarioRepository;

    public UsuarioDetailsService(UsuarioRepository usuarioRepository) {
        this.usuarioRepository = usuarioRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        String clave = email == null ? "" : email.trim();
        Usuario usuario = usuarioRepository.findByEmail(clave)
                .orElseThrow(() -> new UsernameNotFoundException("Usuario no encontrado: " + clave));
        return User.withUsername(usuario.getEmail())
                .password(usuario.getPassword())
                .roles(usuario.getRoles().stream().map(Rol::getNombre).toArray(String[]::new))
                .build();
    }
}
