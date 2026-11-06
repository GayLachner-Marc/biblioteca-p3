package com.serverside.appbackendp1.service;

import com.serverside.appbackendp1.model.Rol;
import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.PrestamoRepository;
import com.serverside.appbackendp1.repository.RolRepository;
import com.serverside.appbackendp1.repository.UsuarioRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.List;
import java.util.Optional;

@Service
public class UsuarioService {

    private final UsuarioRepository usuarioRepository;
    private final PrestamoRepository prestamoRepository;
    private final RolRepository rolRepository;
    private final PasswordEncoder passwordEncoder;

    public UsuarioService(UsuarioRepository usuarioRepository, PrestamoRepository prestamoRepository,
                          RolRepository rolRepository, PasswordEncoder passwordEncoder) {
        this.usuarioRepository = usuarioRepository;
        this.prestamoRepository = prestamoRepository;
        this.rolRepository = rolRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional(readOnly = true)
    public List<Usuario> listar() {
        return usuarioRepository.findAllByOrderByApellidosAscNombreAsc();
    }

    @Transactional(readOnly = true)
    public Optional<Usuario> buscarPorId(Long id) {
        return usuarioRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public boolean emailDuplicado(String email, Long id) {
        if (email == null) {
            return false;
        }
        return id == null ? usuarioRepository.existsByEmail(email)
                : usuarioRepository.existsByEmailAndIdNot(email, id);
    }

    /**
     * Guarda el usuario aplicando la capa de seguridad:
     * - La contraseña nueva (en claro) se cifra con BCrypt; si viene vacía al editar, se conserva la actual.
     * - En el alta se asigna el rol USER; al editar se conservan los roles existentes.
     */
    @Transactional
    public Usuario guardar(Usuario usuario) {
        String nueva = usuario.getPasswordNueva();
        boolean hayNueva = nueva != null && !nueva.isBlank();

        if (usuario.getId() == null) {
            if (hayNueva) {
                usuario.setPassword(passwordEncoder.encode(nueva));
            } else if (usuario.getPassword() == null) {
                throw new IllegalArgumentException("La contraseña es obligatoria en el alta");
            }
            if (usuario.getRoles().isEmpty()) {
                usuario.getRoles().add(obtenerRol(Rol.USER));
            }
        } else {
            Usuario actual = usuarioRepository.findById(usuario.getId())
                    .orElseThrow(() -> new IllegalArgumentException("El usuario no existe"));
            usuario.setPassword(hayNueva ? passwordEncoder.encode(nueva) : actual.getPassword());
            usuario.setRoles(new HashSet<>(actual.getRoles()));
        }
        usuario.setPasswordNueva(null);
        return usuarioRepository.saveAndFlush(usuario);
    }

    private Rol obtenerRol(String nombre) {
        return rolRepository.findByNombre(nombre).orElseGet(() -> rolRepository.save(new Rol(nombre)));
    }

    /** Elimina el usuario. Lanza IllegalStateException si tiene préstamos asociados. */
    @Transactional
    public void eliminar(Long id) {
        if (prestamoRepository.existsByUsuarioId(id)) {
            throw new IllegalStateException("No se puede eliminar el usuario porque tiene préstamos asociados");
        }
        usuarioRepository.deleteById(id);
        usuarioRepository.flush();
    }
}
