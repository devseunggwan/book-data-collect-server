from odmantic import Model


class BookModel(Model):
    keyword: str
    publisher: str
    discount: int
    image: str

    class Config:
        collection = "books"
