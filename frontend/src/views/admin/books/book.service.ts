import http from '@/utils/http'

export interface Book {
  id?: number
  title: string
  author: string
  isbn: string
  category: string
  availableCopies: number
}

export const BookService = {
  async list(q: string): Promise<Book[]> {
    const { data } = await http.get('/api/books', { params: { q } })
    return data.data || []
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/api/books/${id}`)
  }
}
