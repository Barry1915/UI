package com.library.circulation;

import com.library.user.User;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "fine_payments")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FinePayment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(optional = false)
    private User user;

    private BigDecimal amount;

    private String reason;

    private LocalDateTime paidAt;

    @PrePersist
    public void onCreate() {
        this.paidAt = LocalDateTime.now();
    }
}
