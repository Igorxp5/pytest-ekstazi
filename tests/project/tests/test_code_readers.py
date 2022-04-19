from project.readers import read_qrcode, read_barcode


def test_read_qr_code():
    assert read_qrcode([1, 2, 3]) == 3
    assert read_qrcode([1, 2, 3, 4]) == 4


def test_read_barcode():
    assert read_barcode([0, 1, 0, 1]) == 2
    assert read_barcode([0, 1, 0, 1, 1, 1]) == 7  # xfail
