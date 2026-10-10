"""Compare entradas determinísticas com a versão original do Git."""

import contextlib
import importlib.util
import io
import random
import subprocess
import sys
import types
from pathlib import Path

project = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
snapshot = project / "reports/original_git.py.txt"
if snapshot.exists():
    original_source = snapshot.read_text(encoding="utf-8")
else:
    original_source = subprocess.check_output(
        ["git", "show", "HEAD:src/legacy_checkout.py"], cwd=project
    ).decode("utf-8")
original = types.ModuleType("original")
exec(compile(original_source, "original.py", "exec"), original.__dict__)
spec = importlib.util.spec_from_file_location(
    "refactored", project / "src/legacy_checkout.py"
)
refactored = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refactored)
generator = random.Random(20261010)

for case in range(2000):
    customer = {
        "name": "Cliente",
        "type": generator.choice(["regular", "vip", "employee", "unknown"]),
    }
    items = []
    for _ in range(generator.randrange(9)):
        item = {
            "name": generator.choice(["A", "B", "C", "D"]),
            "price": generator.choice([0, 1.01, 19.995, 100, 499, 500, 799, 800, 999, 1000]),
            "qty": generator.choice([-1, 0, 1, 2, 3]),
        }
        if generator.choice([True, False]):
            item["weight"] = generator.choice([0, 0.2, 1, 2.3, 9])
        items.append(item)
    arguments = (
        customer,
        items,
        generator.choice(["", "PROMO10", "PROMO20", "VIP50", "promo10", "INVALID"]),
        generator.choice(["MG", "SP", "RJ", "ES", "BA"]),
        generator.choice([False, True]),
    )
    original_stdout = io.StringIO()
    refactored_stdout = io.StringIO()
    with contextlib.redirect_stdout(original_stdout):
        expected = original.process_order(*arguments)
    with contextlib.redirect_stdout(refactored_stdout):
        actual = refactored.process_order(*arguments)
    assert expected == actual, (case, arguments, expected, actual)
    assert original_stdout.getvalue() == refactored_stdout.getvalue(), (
        case, arguments, original_stdout.getvalue(), refactored_stdout.getvalue()
    )
    assert original.ORDERS_PROCESSED == refactored.ORDERS_PROCESSED, case

print("2000 casos compatíveis: resultado, ordem de duplicados, mensagens e histórico.")
