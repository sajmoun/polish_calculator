from os.path import basename, splitext
import tkinter as tk
from operation import operation1, operation2
import math

class MyEntry(tk.Entry):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        if "textvariable" not in kw:
            self.variable = tk.StringVar()
            self.config(textvariable=self.variable)
        else:
            self.variable = kw["textvariable"]

    @property
    def value(self):
        return self.variable.get()

    @value.setter
    def value(self, new: str):
        self.variable.set(new)


class MyListbox(tk.Listbox):
    def pop(self):
        if self.size() > 0:
            item = self.get(self.size() - 1)
            self.delete(self.size() - 1)
            return item
        else:
            raise IndexError("Zásobník je prázdný.")


class Application(tk.Tk):
    name = "Polish Calc"
    font_set = ("Verdana", 16)

    def __init__(self):
        super().__init__(className=self.name)

        self.option_add("*Font", self.font_set)
        self.title(self.name)
        self.bind("<Escape>", self.destroy)

        self.history = []
        self.history_index = -1
        self.angle_mode = "D"  

        
        self.listbox = MyListbox(master=self)
        self.lbl = tk.Label(self, text="Kalkulátor v obrácené polské notaci")
        self.entry = MyEntry(master=self)
        self.btn = tk.Button(self, text="Zavřít", command=self.destroy)
        self.status = tk.Label(self, text="Režim: D", fg="blue")  

        
        self.entry.bind("<Return>", func=self.enter_handler)
        self.entry.bind("<KP_Enter>", func=self.enter_handler)
        self.entry.bind("<Up>", self.history_up)
        self.entry.bind("<Down>", self.history_down)

        
        self.lbl.pack()
        self.listbox.pack()
        self.entry.pack()
        self.btn.pack()
        self.status.pack()  

        self.entry.focus()

    def set_status(self, message, error=False):
        """Nastaví stavový řádek, kde error=True změní text na červený."""
        self.status.config(text=message, fg="red" if error else "blue")

    def enter_handler(self, event=None):
        input_text = self.entry.value.strip()
        if input_text:
            self.history.append(input_text)
            self.history_index = len(self.history)

            for token in input_text.split():
                try:
                    self.listbox.insert("end", float(token))
                except ValueError:
                    self.tokenProcess(token)

            self.entry.value = ""
            self.listbox.see("end")

    def history_up(self, event):
        """Přechod na předchozí vstup v historii."""
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.entry.value = self.history[self.history_index]

    def history_down(self, event):
        """Přechod na následující vstup v historii."""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.entry.value = self.history[self.history_index]
        elif self.history_index == len(self.history) - 1:
            self.history_index += 1
            self.entry.value = ""

    def tokenProcess(self, token):
        try:
            if token in ["D", "R"]:
                self.angle_mode = token
                self.set_status(f"Režim: {self.angle_mode}")
                return

            if token in operation2:
                try:
                    b = float(self.listbox.pop())
                    a = float(self.listbox.pop())
                    if token == "/" and b == 0:
                        self.set_status("Chyba: Dělení nulou!", error=True)
                        return
                    result = operation2[token](a, b)
                    self.listbox.insert("end", result)
                    self.set_status(f"Operace {token} úspěšná")
                except IndexError:
                    self.set_status("Chyba: Nedostatek čísel v zásobníku!", error=True)

            elif token in operation1:
                try:
                    a = float(self.listbox.pop())
                    
                    if token == "sin" and self.angle_mode == "D":
                        a = math.radians(a)  
                    elif token == "d":
                        a = math.degrees(a)
                    elif token == "r":
                        a = math.radians(a)
                    result = operation1[token](a)
                    self.listbox.insert("end", result)
                    self.set_status(f"Operace {token} úspěšná")
                except IndexError:
                    self.set_status("Chyba: Nedostatek čísel v zásobníku!", error=True)

            else:
                self.set_status(f"Neznámý token: {token}", error=True)

        except Exception as e:
            self.set_status(f"Chyba: {str(e)}", error=True)

    def destroy(self, event=None):
        super().destroy()

app = Application()
app.mainloop()
