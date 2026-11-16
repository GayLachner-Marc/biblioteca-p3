package com.serverside.appbackendp1.security;

import com.serverside.appbackendp1.model.Rol;
import com.serverside.appbackendp1.model.Usuario;
import com.serverside.appbackendp1.repository.UsuarioRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.endsWith;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestBuilders.formLogin;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestBuilders.logout;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.response.SecurityMockMvcResultMatchers.authenticated;
import static org.springframework.security.test.web.servlet.response.SecurityMockMvcResultMatchers.unauthenticated;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class SeguridadTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void elFormularioDeLoginEsPublico() throws Exception {
        mockMvc.perform(get("/login"))
                .andExpect(status().isOk())
                .andExpect(view().name("login"));
    }

    @Test
    void sinSesionSeRedirigeAlLogin() throws Exception {
        mockMvc.perform(get("/libros"))
                .andExpect(status().is3xxRedirection())
                .andExpect(header().string("Location", endsWith("/login")));
    }

    @Test
    @WithMockUser(roles = "USER")
    void unUsuarioNormalPuedeConsultarPeroNoModificar() throws Exception {
        mockMvc.perform(get("/libros")).andExpect(status().isOk());
        mockMvc.perform(get("/libros/nuevo")).andExpect(status().isForbidden());
        mockMvc.perform(get("/usuarios/1/editar")).andExpect(status().isForbidden());
        mockMvc.perform(post("/libros").with(csrf()).param("titulo", "X").param("isbn", "SEC-1"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void sinTokenCsrfSeRechazaElPost() throws Exception {
        mockMvc.perform(post("/libros").param("titulo", "X").param("isbn", "SEC-2"))
                .andExpect(status().isForbidden());
    }

    @Test
    void loginCorrectoYCierreDeSesion() throws Exception {
        crearUsuario("login.ok@example.com", "Secreta123");

        mockMvc.perform(formLogin("/login").user("email", "login.ok@example.com").password("password", "Secreta123"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/"))
                .andExpect(authenticated().withUsername("login.ok@example.com").withRoles(Rol.USER));

        mockMvc.perform(logout())
                .andExpect(redirectedUrl("/login?logout"))
                .andExpect(unauthenticated());
    }

    @Test
    void loginConContrasenaIncorrectaVuelveAlFormulario() throws Exception {
        crearUsuario("login.ko@example.com", "Secreta123");

        mockMvc.perform(formLogin("/login").user("email", "login.ko@example.com").password("password", "otra-clave"))
                .andExpect(redirectedUrl("/login?error"))
                .andExpect(unauthenticated());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void elRegistroCifraLaContrasenaYAsignaRolUser() throws Exception {
        mockMvc.perform(post("/usuarios").with(csrf())
                        .param("nombre", "Nuevo")
                        .param("apellidos", "Socio")
                        .param("email", "nuevo.socio@example.com")
                        .param("fechaAlta", "2026-11-06")
                        .param("passwordNueva", "Secreta123")
                        .param("passwordConfirmacion", "Secreta123"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/usuarios"));

        Usuario guardado = usuarioRepository.findByEmail("nuevo.socio@example.com").orElseThrow();
        assertThat(guardado.getPassword()).isNotEqualTo("Secreta123");
        assertThat(passwordEncoder.matches("Secreta123", guardado.getPassword())).isTrue();
        assertThat(guardado.getRoles()).extracting(Rol::getNombre).containsExactly(Rol.USER);
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void elRegistroExigeContrasenaYConfirmacion() throws Exception {
        mockMvc.perform(post("/usuarios").with(csrf())
                        .param("nombre", "Sin")
                        .param("apellidos", "Clave")
                        .param("email", "sin.clave@example.com")
                        .param("fechaAlta", "2026-11-06")
                        .param("passwordNueva", "Secreta123")
                        .param("passwordConfirmacion", "Distinta123"))
                .andExpect(status().isOk())
                .andExpect(model().attributeHasFieldErrors("usuario", "passwordNueva"));

        assertThat(usuarioRepository.existsByEmail("sin.clave@example.com")).isFalse();
    }

    private void crearUsuario(String email, String password) throws Exception {
        mockMvc.perform(post("/usuarios").with(csrf())
                        .with(org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors
                                .user("admin").roles(Rol.ADMIN))
                        .param("nombre", "Prueba")
                        .param("apellidos", "Login")
                        .param("email", email)
                        .param("fechaAlta", "2026-11-06")
                        .param("passwordNueva", password)
                        .param("passwordConfirmacion", password))
                .andExpect(redirectedUrl("/usuarios"));
    }
}
