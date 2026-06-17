from pathlib import Path


def pdf_escape(text: str) -> str:
    return text.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')


def build_pdf(lines: list[str], output_path: Path) -> None:
    commands = ["BT", "/F1 14 Tf", "72 760 Td", f"({pdf_escape(lines[0])}) Tj"]
    commands.append("/F1 10 Tf")
    for line in lines[1:]:
        commands.append("0 -14 Td")
        commands.append(f"({pdf_escape(line)}) Tj")
    commands.append("ET")
    content_stream = "\n".join(commands).encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    )
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(
        b"5 0 obj\n<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n"
        + content_stream
        + b"\nendstream\nendobj\n"
    )

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    xref_offsets = [0]
    for obj in objects:
        xref_offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in xref_offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )

    output_path.write_bytes(pdf)


def main() -> None:
    lines = [
        "Algebra Factoring Patterns + Unit Circle Reference",
        "",
        "Common Factoring Patterns:",
        "1) Greatest Common Factor:      ax + ay = a(x + y)",
        "2) Difference of Squares:       a^2 - b^2 = (a - b)(a + b)",
        "3) Perfect Square Trinomial:    a^2 + 2ab + b^2 = (a + b)^2",
        "4) Perfect Square Trinomial:    a^2 - 2ab + b^2 = (a - b)^2",
        "5) Trinomial (x^2 + bx + c):    x^2 + bx + c = (x + m)(x + n), m+n=b, mn=c",
        "6) AC Method (ax^2 + bx + c):   split middle term, then factor by grouping",
        "7) Grouping:                    ax + ay + bx + by = (a + b)(x + y)",
        "8) Sum of Cubes:                a^3 + b^3 = (a + b)(a^2 - ab + b^2)",
        "9) Difference of Cubes:         a^3 - b^3 = (a - b)(a^2 + ab + b^2)",
        "",
        "Unit Circle Reference (exact values):",
        "Angle      Radians   (cos, sin)                 tan",
        "0 deg      0         (1, 0)                     0",
        "30 deg     pi/6      (sqrt(3)/2, 1/2)           sqrt(3)/3",
        "45 deg     pi/4      (sqrt(2)/2, sqrt(2)/2)     1",
        "60 deg     pi/3      (1/2, sqrt(3)/2)           sqrt(3)",
        "90 deg     pi/2      (0, 1)                     undefined",
        "120 deg    2pi/3     (-1/2, sqrt(3)/2)          -sqrt(3)",
        "135 deg    3pi/4     (-sqrt(2)/2, sqrt(2)/2)    -1",
        "150 deg    5pi/6     (-sqrt(3)/2, 1/2)          -sqrt(3)/3",
        "180 deg    pi        (-1, 0)                    0",
        "210 deg    7pi/6     (-sqrt(3)/2, -1/2)         sqrt(3)/3",
        "225 deg    5pi/4     (-sqrt(2)/2, -sqrt(2)/2)   1",
        "240 deg    4pi/3     (-1/2, -sqrt(3)/2)         sqrt(3)",
        "270 deg    3pi/2     (0, -1)                    undefined",
        "300 deg    5pi/3     (1/2, -sqrt(3)/2)          -sqrt(3)",
        "315 deg    7pi/4     (sqrt(2)/2, -sqrt(2)/2)    -1",
        "330 deg    11pi/6    (sqrt(3)/2, -1/2)          -sqrt(3)/3",
        "360 deg    2pi       (1, 0)                     0",
    ]

    build_pdf(lines, Path("/home/runner/work/bookwork2/bookwork2/algebra_factoring_unit_circle_reference.pdf"))


if __name__ == "__main__":
    main()
