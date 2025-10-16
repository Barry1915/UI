package com.library.circulation;

import com.library.catalog.Book;
import com.library.catalog.BookRepository;
import com.library.common.api.ApiResponse;
import com.library.user.User;
import com.library.user.UserRepository;
import jakarta.validation.constraints.NotBlank;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api/reservations")
public class ReservationController {

    private final ReservationRepository reservationRepository;
    private final UserRepository userRepository;
    private final BookRepository bookRepository;

    public ReservationController(ReservationRepository reservationRepository, UserRepository userRepository, BookRepository bookRepository) {
        this.reservationRepository = reservationRepository;
        this.userRepository = userRepository;
        this.bookRepository = bookRepository;
    }

    record CreateReservation(@NotBlank String cardNumber, @NotBlank String isbn) {}

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN','LIBRARIAN','READER')")
    public ResponseEntity<ApiResponse<String>> create(@RequestBody CreateReservation req) {
        User user = userRepository.findByCardNumber(req.cardNumber()).orElse(null);
        Book book = bookRepository.findByIsbn(req.isbn()).orElse(null);
        if (user == null || book == null) return ResponseEntity.badRequest().body(ApiResponse.error("无效的证号或ISBN"));
        Reservation r = Reservation.builder().user(user).book(book)
                .createdAt(LocalDateTime.now())
                .expiresAt(LocalDateTime.now().plusDays(7)).build();
        reservationRepository.save(r);
        return ResponseEntity.ok(ApiResponse.ok("预约成功", "OK"));
    }
}
