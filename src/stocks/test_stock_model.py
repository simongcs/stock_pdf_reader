from src.stocks.stock_model import Stock


def test_stock_instance():
    stock = Stock("name", "ticker")
    assert isinstance(stock, Stock)


def test_stock_repr():
    stock = Stock("name", "ticker")
    assert repr(stock) == "<Stock(name, ticker)>"
