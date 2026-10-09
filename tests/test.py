from src.sources1 import extract_date_range

tests = [
    ("10 t/m 11 oktober 2026", "2026-10-10", "2026-10-11"),
    ("31 oktober t/m 1 november 2026", "2026-10-31", "2026-11-01"),
    ("20 september 2026 - 8 februari 2027", "2026-09-20", "2027-02-08"),
]

for text, expected_start, expected_end in tests:
    start, end = extract_date_range(text)

    print(text, "->", start, end)

    assert str(start) == expected_start
    assert str(end) == expected_end

print("All date parser tests passed.")