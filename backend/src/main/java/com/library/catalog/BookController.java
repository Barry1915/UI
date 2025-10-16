package com.library.catalog;

import com.library.common.api.ApiResponse;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookRepository bookRepository;

    public BookController(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    @GetMapping
    public ApiResponse<List<Book>> list(@RequestParam(required = false) String q) {
        List<Book> books = (q == null || q.isBlank()) ? bookRepository.findAll() : bookRepository.search(q);
        return ApiResponse.ok(books);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<Book>> get(@PathVariable Long id) {
        return bookRepository.findById(id)
                .map(b -> ResponseEntity.ok(ApiResponse.ok(b)))
                .orElse(ResponseEntity.notFound().build());
    }

    record CreateBookRequest(@NotBlank String title, String author, String isbn, String categoryName, String publisherName, Integer totalCopies, Integer availableCopies) {}

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN','LIBRARIAN')")
    public ApiResponse<Book> create(@Valid @RequestBody CreateBookRequest req) {
        Book b = Book.builder()
                .title(req.title())
                .author(req.author())
                .isbn(req.isbn())
                .totalCopies(req.totalCopies() == null ? 1 : req.totalCopies())
                .availableCopies(req.availableCopies() == null ? 1 : req.availableCopies())
                .build();
        return ApiResponse.ok(bookRepository.save(b));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN','LIBRARIAN')")
    public ResponseEntity<ApiResponse<Book>> update(@PathVariable Long id, @Valid @RequestBody CreateBookRequest req) {
        return bookRepository.findById(id)
                .map(b -> {
                    b.setTitle(req.title());
                    b.setAuthor(req.author());
                    b.setIsbn(req.isbn());
                    if (req.totalCopies() != null) b.setTotalCopies(req.totalCopies());
                    if (req.availableCopies() != null) b.setAvailableCopies(req.availableCopies());
                    return ResponseEntity.ok(ApiResponse.ok(bookRepository.save(b)));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN','LIBRARIAN')")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!bookRepository.existsById(id)) return ResponseEntity.notFound().build();
        bookRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
