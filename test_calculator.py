import importlib.util

spec = importlib.util.spec_from_file_location("calculator", "calculator.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_scientific_expression():
    assert module.evaluate_expression("sin(pi/2)") == 1.0


def test_scientific_sqroot():
    assert module.evaluate_expression("sqrt(9)") == 3.0
