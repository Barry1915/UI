import http from '@/utils/http'

export const CirculationService = {
  async borrow(cardNumber: string, isbn: string): Promise<void> {
    await http.post('/api/circulation/borrow', { cardNumber, isbn })
  },
  async returnBook(cardNumber: string, isbn: string): Promise<void> {
    await http.post('/api/circulation/return', { cardNumber, isbn })
  }
}
