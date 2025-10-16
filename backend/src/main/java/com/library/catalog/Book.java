package com.library.catalog;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

@Entity
@Table(name = "books")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(length = 150)
    private String author;

    @Column(length = 13, unique = true)
    private String isbn;

    @ManyToOne
    private Category category;

    @ManyToOne
    private Publisher publisher;

    private LocalDate publishDate;

    @Column(length = 1000)
    private String description;

    private Integer totalCopies;
    private Integer availableCopies;
}
