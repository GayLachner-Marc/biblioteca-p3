package com.serverside.appbackendp1.service;

import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.PrestamoRepository;
import com.serverside.appbackendp1.repository.UsuarioRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class UsuarioService {

    private final UsuarioRepository usuarioRepository;
    private final PrestamoRepository prestamoRepository;

    public UsuarioService(UsuarioRepository usuarioRepository, PrestamoRepository prestamoRepository) {
        this.usuarioRepository = usuarioRepository;
        this.prestamoRepository = prestamoRepository;
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

    @Transactional
    public Usuario guardar(Usuario usuario) {
        return usuarioRepository.saveAndFlush(usuario);
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
