import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests, json, os, csv
from datetime import datetime

API_KEY = "e44ccde4bb88aba57cf5f314"
HISTORY_FILE = "history.json"
history = []

def load():
    global history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

def save():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def refresh():
    for item in tree.get_children():
        tree.delete(item)
    for e in reversed(history):
        tree.insert('', 'end', values=(e['date'], e['from'], e['amount'], e['to'], e['result'], e['rate']))

def load_cur():
    try:
        data = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD").json()
        if data['result'] == 'success':
            cur = sorted(data['conversion_rates'].keys())
            from_combo['values'] = to_combo['values'] = cur
            from_var.set('USD')
            to_var.set('EUR')
            status.set(f"Загружено {len(cur)} валют")
    except:
        messagebox.showerror("Ошибка", "Нет интернета")

def conv():
    try:
        am = float(entry.get())
        if am <= 0: raise
    except:
        messagebox.showerror("Ошибка", "Введите число > 0")
        return
    f, t = from_var.get(), to_var.get()
    if not f or not t or f == t:
        messagebox.showerror("Ошибка", "Выберите разные валюты")
        return
    try:
        d = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{f}/{t}/{am}").json()
        if d['result'] == 'success':
            res = d['conversion_result']
            result.set(f"{am} {f} = {res} {t}")
            history.append({'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'from': f, 'amount': am, 'to': t, 'result': res, 'rate': d['conversion_rate']})
            refresh(); save()
            messagebox.showinfo("OK", result.get())
    except:
        messagebox.showerror("Ошибка", "Ошибка соединения")

def save_man():
    p = filedialog.asksaveasfilename(defaultextension=".json")
    if p:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

def load_man():
    global history
    p = filedialog.askopenfilename()
    if p:
        with open(p, 'r', encoding='utf-8') as f:
            history = json.load(f)
        refresh()

def clear():
    global history
    if messagebox.askyesno("?", "Очистить?"):
        history = []; refresh(); save()

def export():
    p = filedialog.asksaveasfilename(defaultextension=".csv")
    if p:
        with open(p, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Дата','Из','Сумма','В','Результат','Курс'])
            w.writerows([[e['date'], e['from'], e['amount'], e['to'], e['result'], e['rate']] for e in history])

root = tk.Tk()
root.title("Конвертер")
root.geometry("662x550")
from_var, to_var, result, status = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(value="Готов")

main = ttk.Frame(root, padding=10); main.grid(sticky='nsew')
root.columnconfigure(0, weight=1); root.rowconfigure(0, weight=1)

ttk.Label(main, text="💱 Конвертер", font=('Arial',20,'bold')).grid(columnspan=3, pady=10)

f1 = ttk.LabelFrame(main, text="Конвертация", padding=10)
f1.grid(row=1, column=0, columnspan=2, sticky='ew', pady=10)
ttk.Label(f1, text="Сумма:").grid(row=0, column=0)
entry = ttk.Entry(f1, width=20); entry.grid(row=0, column=1)
ttk.Label(f1, text="Из:").grid(row=1, column=0)
from_combo = ttk.Combobox(f1, textvariable=from_var, width=20, state='readonly'); from_combo.grid(row=1, column=1)
ttk.Label(f1, text="В:").grid(row=2, column=0)
to_combo = ttk.Combobox(f1, textvariable=to_var, width=20, state='readonly'); to_combo.grid(row=2, column=1)
btn = ttk.Button(f1, text="🔄 Конвертировать", command=conv, width=20); btn.grid(row=3, column=0, columnspan=2, pady=10)
ttk.Label(f1, textvariable=result, font=('Arial',14,'bold'), foreground='green').grid(row=4, column=0, columnspan=2)

f2 = ttk.LabelFrame(main, text="📊 История", padding=10)
f2.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=10)
main.rowconfigure(2, weight=1)
tree = ttk.Treeview(f2, columns=('Дата','Из','Сумма','В','Результат','Курс'), show='headings', height=8)
for c in ['Дата','Из','Сумма','В','Результат','Курс']:
    tree.heading(c, text=c); tree.column(c, width=100, anchor='center')
tree.grid(row=0, column=0, sticky='nsew')
f2.columnconfigure(0, weight=1); f2.rowconfigure(0, weight=1)
ttk.Scrollbar(f2, orient='vertical', command=tree.yview).grid(row=0, column=1, sticky='ns')
tree.configure(yscrollcommand=lambda *args: None)

bf = ttk.Frame(f2); bf.grid(row=1, column=0, pady=10)
for t,c in [('💾 Сохранить', save_man), ('📂 Загрузить', load_man), ('🗑️ Очистить', clear), ('📤 CSV', export)]:
    ttk.Button(bf, text=t, command=c, width=12).pack(side='left', padx=5)

ttk.Label(main, textvariable=status, relief='sunken', anchor='w').grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)

load(); refresh(); load_cur()
root.mainloop()