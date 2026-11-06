package com.serverside.appbackendp1.repository;

import com.serverside.appbackendp1.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UsuarioRepository extends JpaRepository<Usuario, Long> {

    boolean existsByEmailAndIdNot(String email, Long id);

    boolean existsByEmail(String email);

    List<Usuario> findAllByOrderByApellidosAscNombreAsc();
}
