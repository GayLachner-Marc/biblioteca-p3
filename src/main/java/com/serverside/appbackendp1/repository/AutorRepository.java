package com.serverside.appbackendp1.repository;

import com.serverside.appbackendp1.model.Autor;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AutorRepository extends JpaRepository<Autor, Long> {

    List<Autor> findAllByOrderByNombreAsc();
}
