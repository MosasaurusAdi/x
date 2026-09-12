import tkinter as tk
import ast
import math

BACKGROUND = "#050706"
PANEL = "#0d1510"
TEXT = "#eef8e8"
MUTED = "#a8b89d"
GREEN = "#7dff9a"
LIGHT_GREEN = "#ccffd8"
SWORD = "#c8b984"
FONT_PRIMARY = ("Arial", 12, "bold")
FONT_DISPLAY = ("Arial", 24, "bold")

ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
)

FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "factorial": math.factorial,
}

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def normalize(expression):
    expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    expression = expression.replace("π", "pi")
    expression = expression.replace("^", "**")
    expression = expression.replace(" ", "")
    return expression


def evaluate_expression(expression):
    expression = normalize(expression)
    tree = ast.parse(expression, mode="eval")

    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError("Invalid syntax")

    return eval_ast(tree.body)


def eval_ast(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Invalid constant")

    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ValueError("Unknown symbol")

    if isinstance(node, ast.BinOp):
        left = eval_ast(node.left)
        right = eval_ast(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Unsupported operator")

    if isinstance(node, ast.UnaryOp):
        value = eval_ast(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +value
        if isinstance(node.op, ast.USub):
            return -value
        raise ValueError("Unsupported unary operator")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function")
        func_name = node.func.id
        if func_name not in FUNCTIONS:
            raise ValueError("Unknown function")
        if len(node.args) != 1:
            raise ValueError("One argument required")
        arg = eval_ast(node.args[0])
        if func_name == "factorial":
            if arg < 0 or int(arg) != arg:
                raise ValueError("Factorial needs a whole non-negative number")
            return math.factorial(int(arg))
        return FUNCTIONS[func_name](arg)

    raise ValueError("Invalid expression")


class BladeButton(tk.Frame):
    def __init__(self, parent, text, kind, command):
        super().__init__(parent, bg=BACKGROUND, highlightbackground=GREEN, highlightthickness=1)
        self.kind = kind
        self.text = text

        # Outer frame for the button
        self.configure(width=64, height=56, padx=0, pady=0)
        self.bind("<Button-1>", lambda event: command())
        self.bind("<Enter>", lambda event: self.configure(highlightbackground=LIGHT_GREEN))
        self.bind("<Leave>", lambda event: self.configure(highlightbackground=GREEN))

        # Small canvas blade icon inside the button, drawn as a dark fairy blade
        self.canvas = tk.Canvas(self, width=34, height=34, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(side="left", padx=(4, 0))
        self.draw_blade_icon(kind)

        # Label for the button text
        self.label = tk.Label(
            self,
            text=text,
            font=FONT_PRIMARY,
            bg=self.button_color(kind),
            fg=self.button_text_color(kind),
            padx=8,
            pady=4,
        )
        self.label.pack(side="right", fill="y", expand=True)

    def draw_blade_icon(self, kind):
        self.canvas.delete("all")
        blade_color = GREEN if kind in ("operator", "function") else SWORD
        blade_fill = "#06120b"

        # Draw a dark blade symbol on a small canvas
        self.canvas.create_polygon(16, 4, 27, 28, 20, 29, 10, 33, 12, 14, fill=blade_fill, outline=blade_color, width=1)
        self.canvas.create_line(16, 3, 16, 30, fill=blade_color, width=1)
        self.canvas.create_line(13, 29, 19, 30, fill=blade_color, width=1)
        if kind == "operator":
            self.canvas.create_line(8, 7, 25, 27, fill=blade_color, width=1)
        elif kind == "function":
            self.canvas.create_line(9, 12, 24, 12, fill=blade_color, width=1)
        elif kind == "constant":
            self.canvas.create_oval(13, 5, 23, 14, outline=blade_color, width=1)
        elif kind == "equals":
            self.canvas.create_line(7, 13, 27, 13, fill=blade_color, width=1)
            self.canvas.create_line(7, 20, 27, 20, fill=blade_color, width=1)

    def button_color(self, kind):
        if kind == "clear":
            return "#302516"
        if kind == "operator":
            return "#20351f"
        if kind == "equals":
            return "#c7a555"
        if kind == "function":
            return "#1b2324"
        if kind == "constant":
            return "#102015"
        if kind == "paren":
            return "#171d16"
        return "#0d1410"

    def button_text_color(self, kind):
        if kind == "clear":
            return SWORD
        if kind == "operator":
            return GREEN
        if kind == "equals":
            return "#05150b"
        if kind == "function":
            return LIGHT_GREEN
        if kind == "constant":
            return SWORD
        if kind == "paren":
            return MUTED
        return TEXT


class CloverBladeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Clover Blade // Scientific")
        self.root.geometry("640x620")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)
        self.expression = ""
        self.build_ui()

    def build_ui(self):
        main = tk.Frame(self.root, bg=BACKGROUND)
        main.pack(fill="both", expand=True, padx=16, pady=16)

        title_frame = tk.Frame(main, bg=BACKGROUND)
        title_frame.pack(fill="x", pady=(0, 12))

        tk.Label(title_frame, text="CLOVER BLADE", font=("Arial", 24, "bold"), fg=GREEN, bg=BACKGROUND).pack(anchor="center")
        tk.Label(title_frame, text="SCIENTIFIC CALCULATOR", font=("Arial", 11, "bold"), fg=MUTED, bg=BACKGROUND).pack(anchor="center", pady=(4, 0))

        display_frame = tk.Frame(main, bg=PANEL, highlightbackground=GREEN, highlightthickness=2)
        display_frame.pack(fill="x", pady=(0, 12))

        self.display_var = tk.StringVar(value="0")
        tk.Label(display_frame, textvariable=self.display_var, font=FONT_DISPLAY, bg=PANEL, fg=LIGHT_GREEN, anchor="e", padx=16, pady=20, height=2).pack(fill="both")

        button_frame = tk.Frame(main, bg=BACKGROUND)
        button_frame.pack(fill="both", expand=True)

        button_specs = [
            ("C", "clear"), ("DEL", "delete"), ("(", "paren"), (")", "paren"), ("÷", "operator"),
            ("sin", "function"), ("cos", "function"), ("tan", "function"), ("√", "function"), ("×", "operator"),
            ("log", "function"), ("ln", "function"), ("exp", "function"), ("π", "constant"), ("−", "operator"),
            ("x²", "function"), ("x³", "function"), ("n!", "function"), ("e", "constant"), ("+", "operator"),
            ("7", "number"), ("8", "number"), ("9", "number"), (".", "decimal"), ("=", "equals"),
            ("4", "number"), ("5", "number"), ("6", "number"), ("±", "sign"), ("^", "operator"),
            ("1", "number"), ("2", "number"), ("3", "number"), ("0", "number"), ("00", "number"),
        ]

        for i, (text, kind) in enumerate(button_specs):
            row = i // 5
            col = i % 5
            btn = BladeButton(button_frame, text, kind, lambda t=text, k=kind: self.handle_button(t, k))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        for col in range(5):
            button_frame.columnconfigure(col, weight=1)
        for row in range(7):
            button_frame.rowconfigure(row, weight=1)

    def button_color(self, kind):
        if kind == "clear":
            return "#302516"
        if kind == "operator":
            return "#20351f"
        if kind == "equals":
            return "#c7a555"
        if kind == "function":
            return "#1b2324"
        if kind == "constant":
            return "#102015"
        if kind == "paren":
            return "#171d16"
        return "#0d1410"

    def button_text_color(self, kind):
        if kind == "clear":
            return SWORD
        if kind == "operator":
            return GREEN
        if kind == "equals":
            return "#05150b"
        if kind == "function":
            return LIGHT_GREEN
        if kind == "constant":
            return SWORD
        if kind == "paren":
            return MUTED
        return TEXT

    def button_active_color(self, kind):
        if kind == "clear":
            return "#503b21"
        if kind == "operator":
            return "#304821"
        if kind == "equals":
            return "#e6d28d"
        return "#273d22"

    def handle_button(self, text, kind):
        if kind == "number":
            self.expression += text
        elif kind == "operator":
            if text == "×":
                self.expression += "*"
            elif text == "÷":
                self.expression += "/"
            elif text == "−":
                self.expression += "-"
            elif text == "+":
                self.expression += "+"
            elif text == "^":
                self.expression += "**"
        elif kind == "clear":
            self.expression = ""
        elif kind == "delete":
            self.expression = self.expression[:-1]
        elif kind == "decimal":
            if not self.expression.endswith("."):
                self.expression += "."
        elif kind == "paren":
            self.expression += text
        elif kind == "constant":
            if text == "π":
                self.expression += "pi"
            elif text == "e":
                self.expression += "e"
        elif kind == "sign":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression
        elif kind == "function":
            if text == "sin":
                self.expression += "sin("
            elif text == "cos":
                self.expression += "cos("
            elif text == "tan":
                self.expression += "tan("
            elif text == "√":
                self.expression += "sqrt("
            elif text == "log":
                self.expression += "log("
            elif text == "ln":
                self.expression += "ln("
            elif text == "exp":
                self.expression += "exp("
            elif text == "x²":
                self.expression += "**2"
            elif text == "x³":
                self.expression += "**3"
            elif text == "n!":
                try:
                    val = evaluate_expression(self.expression)
                    if val is None:
                        raise ValueError
                    if val < 0 or int(val) != val:
                        raise ValueError
                    self.expression = str(math.factorial(int(val)))
                    self.update_display()
                    return
                except Exception:
                    self.expression = "ERROR"
                    self.update_display()
                    return
        elif kind == "equals":
            self.evaluate_expression()
            return

        self.update_display()

    def update_display(self):
        self.display_var.set(self.expression if self.expression else "0")

    def evaluate_expression(self):
        try:
            value = evaluate_expression(self.expression)
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            self.expression = str(value)
            self.update_display()
        except Exception:
            self.expression = "ERROR"
            self.update_display()


def main():
    root = tk.Tk()
    CloverBladeCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
