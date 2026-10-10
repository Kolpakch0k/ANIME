import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, os, shutil
from PIL import Image, ImageTk

BG, PANEL, INPUT = "#1a0b2e", "#2d1b4e", "#3d2661"
PINK, PURPLE, TXT, DIM = "#ff6ec7", "#b57bff", "#fff", "#c4a8e0"

db = sqlite3.connect("anime.db"); cur = db.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS chars(
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, anime TEXT,
    age INTEGER, role TEXT, power TEXT, image TEXT)""")

if cur.execute("SELECT COUNT(*) FROM chars").fetchone()[0] == 0:
    cur.executemany("INSERT INTO chars(name,anime,age,role,power,image) VALUES(?,?,?,?,?,?)", [
        ("Микаса Аккерман", "Attack on Titan", 19, "Главная героиня", "Титан-сила", "mikasa.png"),
        ("Сакура Харуно",   "Naruto", 17, "Главная героиня", "Медицинское ниндзюцу", "sakura.png"),
        ("Хината Хьюга",    "Naruto", 16, "Второстепенная", "Бьякуган", "hinata.png"),
        ("Нами",            "One Piece", 20, "Главная героиня", "Навигация", "nami.png"),
        ("Нико Робин",      "One Piece", 30, "Главная героиня", "Плод Хана-Хана", "robin.png"),
        ("Рем",             "Re:Zero", 17, "Второстепенная", "Магия воды", "rem.png"),
        ("Эмилия",          "Re:Zero", 18, "Главная героиня", "Магия льда", "emilia.png"),
        ("Сэйбер",          "Fate/stay night", 25, "Главная героиня", "Экскалибур", "saber.png"),
        ("Рин Тоосака",     "Fate/stay night", 17, "Главная героиня", "Магия камней", "rin.png"),
        ("Асуна Юки",       "Sword Art Online", 17, "Главная героиня", "Фехтование", "asuna.png"),
        ("Эрза Скарлет",    "Fairy Tail", 19, "Главная героиня", "Магия огня", "erza.png"),
        ("Люси Хартфилия",  "Fairy Tail", 17, "Главная героиня", "Духи звёзд", "lucy.png"),
        ("Мадока Канаме",   "Madoka Magica", 14, "Главная героиня", "Магия", "madoka.png"),
        ("Хомура Акэми",    "Madoka Magica", 14, "Главная героиня", "Время", "homura.png"),
        ("Рюко Матой",      "Kill la Kill", 17, "Главная героиня", "Клинок-ножницы", "ryuko.png"),
        ("Аска Лэнгли",     "Evangelion", 14, "Главная героиня", "Пилот Евы-02", "asuka.png"),
        ("Рей Аянами",      "Evangelion", 14, "Главная героиня", "Пилот Евы-00", "rei.png"),
        ("Виолетта",        "Violet Evergarden", 14, "Главная героиня", "Автозаписка", "violet.png"),
        ("Тоука Киришима",  "Tokyo Ghoul", 17, "Главная героиня", "Кукаку", "touka.png"),
        ("Холо",            "Spice and Wolf", 600, "Главная героиня", "Волчица-богиня", "holo.png"),
    ]); db.commit()

cache = {} 

def img(name, size):
    if not name or not os.path.exists(f"images/{name}"): return None
    try:
        return ImageTk.PhotoImage(Image.open(f"images/{name}").convert("RGBA").resize(size, Image.LANCZOS))
    except: return None

def load(*_):
    for r in tree.get_children(): tree.delete(r)
    prev.config(image="", text="🌷\n\nВыбери персонажа")
    q = "SELECT * FROM chars WHERE (name LIKE ? OR anime LIKE ? OR power LIKE ?)"
    p = [f"%{sv.get()}%"]*3
    if av.get() != "Все": q += " AND anime=?"; p.append(av.get())
    if rv.get() != "Все": q += " AND role=?";  p.append(rv.get())
    cur.execute(q + " ORDER BY name", p)
    for cid, n, a, ag, r, pw, im in cur.fetchall():
        ph = img(im, (100, 140))
        if ph: cache[cid] = ph; tree.insert("", "end", iid=cid, text="", image=ph, values=(n, a, ag, r, pw))
        else: tree.insert("", "end", iid=cid, text="🌸", values=(n, a, ag, r, pw))
    ac["values"] = ["Все"] + [x[0] for x in cur.execute("SELECT DISTINCT anime FROM chars ORDER BY anime")]
    rc["values"] = ["Все"] + [x[0] for x in cur.execute("SELECT DISTINCT role FROM chars ORDER BY role")]
    st.config(text=f"🌸 Найдено: {len(tree.get_children())}")

def select(_=None):

    s = tree.selection()
    if not s: return
    cur.execute("SELECT * FROM chars WHERE id=?", (s[0],)); row = cur.fetchone()
    for e, v in zip(entries, row[1:]): e.delete(0, tk.END); e.insert(0, str(v))
    ph = img(row[6], (260, 360))
    if ph: cache["p"] = ph; prev.config(image=ph, text="")
    else: prev.config(image="", text=f"🌸\n\n{row[1]}\n\n(нет картинки)")

def form():
    n, a = en.get().strip(), ea.get().strip()
    if not n or not a: messagebox.showwarning("!", "Заполни Имя и Аниме"); return None
    try: ag = int(eag.get() or 0)
    except: ag = 0
    return (n, a, ag, er.get(), ep.get(), ei.get())

def add():
    d = form()
    if d: cur.execute("INSERT INTO chars(name,anime,age,role,power,image) VALUES(?,?,?,?,?,?)", d); db.commit(); load(); clear(); st.config(text="✅ Добавлено")

def upd():
    s = tree.selection()
    if not s: return messagebox.showwarning("!", "Выбери строку")
    d = form()
    if d: cur.execute("UPDATE chars SET name=?,anime=?,age=?,role=?,power=?,image=? WHERE id=?", (*d, s[0])); db.commit(); load(); st.config(text="✏ Обновлено")

def dele():
    s = tree.selection()
    if not s: return messagebox.showwarning("!", "Выбери строку")
    if messagebox.askyesno("?", "Удалить?"):
        cur.execute("DELETE FROM chars WHERE id=?", (s[0],)); db.commit(); load(); clear(); st.config(text="🗑 Удалено")

def clear():
    for e in entries: e.delete(0, tk.END)
    prev.config(image="", text="🌷\n\nВыбери персонажа")

def pick_img():
    p = filedialog.askopenfilename(filetypes=[("Картинки", "*.png *.jpg *.jpeg *.gif")])
    if not p: return
    os.makedirs("images", exist_ok=True)
    shutil.copy(p, f"images/{os.path.basename(p)}")
    ei.delete(0, tk.END); ei.insert(0, os.path.basename(p))

def reset():
    sv.set(""); av.set("Все"); rv.set("Все"); load()

root = tk.Tk(); root.title("🌸 Аниме-персонажи 🌸"); root.geometry("1250x740"); root.configure(bg=BG)
style = ttk.Style(); style.theme_use("clam")
style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TXT, rowheight=110, font=("Segoe UI", 10), borderwidth=0)
style.configure("Treeview.Heading", background=PURPLE, foreground="white", font=("Segoe UI", 10, "bold"), relief="flat")
style.map("Treeview", background=[("selected", PINK)], foreground=[("selected", "white")])
style.map("Treeview.Heading", background=[("active", PINK)])

tk.Label(root, text="🌸  Учёт аниме-персонажей  🌸", font=("Segoe UI", 18, "bold"), bg=BG, fg=PINK).pack(pady=10)

ff = tk.Frame(root, bg=PANEL, padx=12, pady=10); ff.pack(fill="x", padx=12, pady=6)
def lab(t): tk.Label(ff, text=t, font=("Segoe UI", 10, "bold"), bg=PANEL, fg=TXT).pack(side="left", padx=(10, 4))
def entry(var=None, w=22):
    e = tk.Entry(ff, textvariable=var, width=w, bg=INPUT, fg=TXT, insertbackground=PINK, relief="flat", font=("Segoe UI", 10))
    e.pack(side="left", ipady=4); return e
lab(" Поиск:"); sv = tk.StringVar(); sv.trace("w", load); entry(sv)
lab(" Аниме:"); av = tk.StringVar(value="Все"); ac = ttk.Combobox(ff, textvariable=av, state="readonly", width=22); ac.pack(side="left", padx=4); ac.bind("<<ComboboxSelected>>", load)
lab(" Роль:");  rv = tk.StringVar(value="Все"); rc = ttk.Combobox(ff, textvariable=rv, state="readonly", width=18); rc.pack(side="left", padx=4); rc.bind("<<ComboboxSelected>>", load)
tk.Button(ff, text=" Сброс", bg=PINK, fg="white", relief="flat", padx=10, pady=3, command=reset).pack(side="left", padx=10)

mid = tk.Frame(root, bg=BG); mid.pack(fill="both", expand=True, padx=12)
tf = tk.Frame(mid, bg=BG); tf.pack(side="left", fill="both", expand=True)
tree = ttk.Treeview(tf, columns=("n","a","ag","r","p"), show="tree headings", height=15)
for c, h, w in [("#0","🌸",110),("n","Имя",170),("a","Аниме",170),("ag","Возраст",70),("r","Роль",140),("p","Способности",250)]:
    tree.heading(c, text=h); tree.column(c, width=w, anchor="center" if c in ("#0","ag") else "w")
vs = ttk.Scrollbar(tf,

orient="vertical", command=tree.yview); tree.configure(yscrollcommand=vs.set)
tree.pack(side="left", fill="both", expand=True); vs.pack(side="right", fill="y")
tree.bind("<<TreeviewSelect>>", select)

pf = tk.Frame(mid, bg=PANEL, padx=10, pady=10); pf.pack(side="right", fill="y", padx=(12, 0))
tk.Label(pf, text="🖼 Превью", font=("Segoe UI", 10, "bold"), bg=PANEL, fg=PINK).pack()
prev = tk.Label(pf, text="\n\nВыбери персонажа", bg=PANEL, fg=DIM, font=("Segoe UI", 10), width=30, height=18)
prev.pack(pady=4)

form_f = tk.LabelFrame(root, text=" ✏ Данные ", font=("Segoe UI", 10, "bold"), bg=BG, fg=PINK, padx=10, pady=8)
form_f.pack(fill="x", padx=12, pady=8)

entries = []
def field(label, row, col, w=22):
    tk.Label(form_f, text=label, bg=BG, fg=TXT, font=("Segoe UI", 10, "bold")).grid(row=row, column=col*2, sticky="e", padx=(6, 3), pady=3)
    e = tk.Entry(form_f, width=w, bg=INPUT, fg=TXT, insertbackground=PINK, relief="flat", font=("Segoe UI", 10))
    e.grid(row=row, column=col*2+1, padx=(0, 12), pady=3, ipady=3); entries.append(e); return e

en  = field("Имя:", 0, 0)
ea  = field("Аниме:", 0, 1)
eag = field("Возраст:", 0, 2, 8)
er  = field("Роль:", 1, 0)
ep  = field("Способности:", 1, 1, 30)
ei  = field("Картинка:", 1, 2, 16)
tk.Button(form_f, text="папка", bg=PURPLE, fg="white", relief="flat", padx=8, command=pick_img).grid(row=1, column=6, padx=4)

act = tk.Frame(root, bg=BG); act.pack(pady=8)
for t, c, f in [(" Добавить","#27ae60",add), ("Обновить","#2980b9",upd), (" Удалить","#c0392b",dele), (" Очистить","#7f8c8d",clear)]:
    tk.Button(act, text=t, bg=c, fg="white", relief="flat", padx=16, pady=5, font=("Segoe UI", 10, "bold"), command=f).pack(side="left", padx=5)

st = tk.Label(root, text="Готово", bg=BG, fg=DIM, anchor="w"); st.pack(fill="x", padx=12, pady=(0, 8))

load()
root.mainloop()