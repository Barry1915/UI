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

import java.time.LocalDate;

@RestController
@RequestMapping("/api/circulation")
public class CirculationController {

    private final UserRepository userRepository;
    private final BookRepository bookRepository;
    private final BorrowRecordRepository borrowRecordRepository;

    public CirculationController(UserRepository userRepository, BookRepository bookRepository, BorrowRecordRepository borrowRecordRepository) {
        this.userRepository = userRepository;
        this.bookRepository = bookRepository;
        this.borrowRecordRepository = borrowRecordRepository;
    }

    record BorrowRequest(@NotBlank String cardNumber, @NotBlank String isbn) {}

    @PostMapping("/borrow")
    @PreAuthorize("hasAnyRole('ADMIN','LIBRARIAN')")
    public ResponseEntity<ApiResponse<String>> borrow(@RequestBody BorrowRequest req) {
        User user = userRepository.findByCardNumber(req.cardNumber()).orElse(null);
        Book book = bookRepository.findByIsbn(req.isbn()).orElse(null);
        if (user == null || book == null) return ResponseEntity.badRequest().body(ApiResponse.error("无效的证号或ISBN"));
        if (book.getAvailableCopies() == null || book.getAvailableCopies() <= 0) return ResponseEntity.badRequest().body(ApiResponse.error("馆藏不足"));
        BorrowRecord br = BorrowRecord.builder()
                .user(user)
                .book(book)
                .borrowDate(LocalDate.now())
                .dueDate(LocalDate.now().plusDays(30))
                .renewCount(0)
                .build();
        borrowRecordRepository.save(br);
        book.setAvailableCopies(book.getAvailableCopies() - 1);
        bookRepository.save(book);
        return ResponseEntity.ok(ApiResponse.ok("借阅成功", "OK"));
    }

    record ReturnRequest(@NotBlank String cardNumber, @NotBlank String isbn) {}

    @PostMapping("/return")
    @PreAuthorize("hasAnyRole('ADMIN','LIBRARIAN')")
    public ResponseEntity<ApiResponse<String>> returnBook(@RequestBody ReturnRequest req) {
        User user = userRepository.findByCardNumber(req.cardNumber()).orElse(null);
        Book book = bookRepository.findByIsbn(req.isbn()).orElse(null);
        if (user == null || book == null) return ResponseEntity.badRequest().body(ApiResponse.error("无效的证号或ISBN"));
        BorrowRecord record = borrowRecordRepository.findAll().stream()
                .filter(r -> r.getUser().getId().equals(user.getId()) && r.getBook().getId().equals(book.getId()) && r.getReturnDate() == null)
                .findFirst().orElse(null);
        if (record == null) return ResponseEntity.badRequest().body(ApiResponse.error("未找到借阅记录"));
        record.setReturnDate(LocalDate.now());
        borrowRecordRepository.save(record);
        book.setAvailableCopies(book.getAvailableCopies() + 1);
        bookRepository.save(book);
        return ResponseEntity.ok(ApiResponse.ok("归还成功", "OK"));
    }
}
