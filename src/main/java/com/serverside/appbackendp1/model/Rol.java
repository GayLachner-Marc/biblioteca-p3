package com.serverside.appbackendp1.model;

import jakarta.persistence.*;

/**
 * Rol de seguridad (capa de seguridad del modelo E/R).
 * Se guarda sin el prefijo "ROLE_": ADMIN, USER.
 */
@Entity
@Table(name = "roles")
public class Rol {

    public static final String ADMIN = "ADMIN";
    public static final String USER = "USER";

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 30)
    private String nombre;

    public Rol() {
    }

    public Rol(String nombre) {
        this.nombre = nombre;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
}
