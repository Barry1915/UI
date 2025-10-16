package com.library.auth;

import com.library.common.api.ApiResponse;
import com.library.security.JwtService;
import com.library.user.Role;
import com.library.user.RoleRepository;
import com.library.user.User;
import com.library.user.UserRepository;
import jakarta.validation.constraints.NotBlank;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtService jwtService;
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthController(AuthenticationManager authenticationManager, JwtService jwtService, UserRepository userRepository, RoleRepository roleRepository, PasswordEncoder passwordEncoder) {
        this.authenticationManager = authenticationManager;
        this.jwtService = jwtService;
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
        this.passwordEncoder = passwordEncoder;
    }

    record LoginRequest(@NotBlank String username, @NotBlank String password) {}

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<Map<String, Object>>> login(@RequestBody LoginRequest req) {
        authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(req.username(), req.password()));
        User user = userRepository.findByUsername(req.username()).orElseThrow();
        Map<String, Object> claims = new HashMap<>();
        claims.put("roles", user.getRoles().stream().map(Role::getCode).toList());
        String token = jwtService.generateToken(user.getUsername(), claims);
        Map<String, Object> body = new HashMap<>();
        body.put("token", token);
        body.put("username", user.getUsername());
        return ResponseEntity.ok(ApiResponse.ok(body));
    }

    record RegisterRequest(@NotBlank String username, @NotBlank String password, String fullName) {}

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<String>> register(@RequestBody RegisterRequest req) {
        if (userRepository.findByUsername(req.username()).isPresent()) {
            return ResponseEntity.badRequest().body(ApiResponse.error("用户名已存在"));
        }
        User user = User.builder()
                .username(req.username())
                .passwordHash(passwordEncoder.encode(req.password()))
                .fullName(req.fullName())
                .enabled(true)
                .build();
        Role reader = roleRepository.findByCode("READER").orElseGet(() -> roleRepository.save(Role.builder().code("READER").name("读者").build()));
        user.getRoles().add(reader);
        userRepository.save(user);
        return ResponseEntity.ok(ApiResponse.ok("注册成功", "OK"));
    }
}
