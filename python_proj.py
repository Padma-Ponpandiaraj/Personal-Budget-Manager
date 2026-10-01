import wx
import wx.grid as gridlib
import math

FILE = "data.txt"


# ---------- Data Handling ----------

def read_data():
    salary = 0
    expenses = []
    try:
        with open(FILE) as f:
            for line in f:
                name, val = line.strip().split(",")
                if name == "SALARY":
                    salary = int(val)
                else:
                    expenses.append((name, int(val)))
    except:
        pass
    return salary, expenses


def write_all(salary, expenses):
    with open(FILE, "w") as f:
        f.write(f"SALARY,{salary}\n")
        for n, a in expenses:
            f.write(f"{n},{a}\n")


# ---------- MAIN APPLICATION ----------

class BudgetApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Personal Budget Manager", size=(600, 550))

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel, size=(580, 520))

        self.tab1 = wx.Panel(notebook)
        self.tab2 = wx.Panel(notebook)
        self.tab3 = wx.Panel(notebook)

        notebook.AddPage(self.tab1, "Budget")
        notebook.AddPage(self.tab2, "Expenses")
        notebook.AddPage(self.tab3, "Report")

        self.create_tab1()
        self.create_tab2()
        self.create_tab3()

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(vbox)

        self.Centre()
        self.Show()

    # ---------- TAB 1 (Salary) ----------
    def create_tab1(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(wx.StaticText(self.tab1, label="Monthly Salary"),
                 0, wx.ALL | wx.CENTER, 10)

        self.salary_txt = wx.TextCtrl(self.tab1)
        vbox.Add(self.salary_txt, 0, wx.ALL | wx.CENTER, 5)

        save_btn = wx.Button(self.tab1, label="Save Salary")
        save_btn.Bind(wx.EVT_BUTTON, self.save_salary)
        vbox.Add(save_btn, 0, wx.ALL | wx.CENTER, 10)

        self.remaining_lbl = wx.StaticText(self.tab1, label="Remaining Salary: ₹0")
        font = self.remaining_lbl.GetFont()
        font.PointSize = 14
        font.Bold()
        self.remaining_lbl.SetFont(font)

        vbox.Add(self.remaining_lbl, 0, wx.ALL | wx.CENTER, 20)
        self.tab1.SetSizer(vbox)

    def save_salary(self, event):
        sal = self.salary_txt.GetValue()
        if not sal.isdigit():
            wx.MessageBox("Enter a valid salary", "Error")
            return
        salary, expenses = read_data()
        write_all(int(sal), expenses)
        self.update_status()

    # ---------- TAB 2 (Expenses) ----------
    def create_tab2(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(wx.StaticText(self.tab2, label="Expense Name"),
                 0, wx.ALL | wx.CENTER, 5)
        self.exp_name = wx.TextCtrl(self.tab2)
        vbox.Add(self.exp_name, 0, wx.ALL | wx.CENTER, 5)

        vbox.Add(wx.StaticText(self.tab2, label="Amount"),
                 0, wx.ALL | wx.CENTER, 5)
        self.exp_amt = wx.TextCtrl(self.tab2)
        vbox.Add(self.exp_amt, 0, wx.ALL | wx.CENTER, 5)

        add_btn = wx.Button(self.tab2, label="Add Expense")
        add_btn.Bind(wx.EVT_BUTTON, self.add_expense)
        vbox.Add(add_btn, 0, wx.ALL | wx.CENTER, 10)

        toggle_btn = wx.Button(self.tab2, label="Show / Hide Expenses")
        toggle_btn.Bind(wx.EVT_BUTTON, self.toggle_table)
        vbox.Add(toggle_btn, 0, wx.ALL | wx.CENTER, 10)

        # Grid Table
        self.grid = gridlib.Grid(self.tab2)
        self.grid.CreateGrid(0, 2)
        self.grid.SetColLabelValue(0, "Expense")
        self.grid.SetColLabelValue(1, "Amount")
        self.grid.Hide()

        vbox.Add(self.grid, 1, wx.EXPAND | wx.ALL, 10)

        rem_btn = wx.Button(self.tab2, label="Remove Selected")
        rem_btn.Bind(wx.EVT_BUTTON, self.remove_expense)
        vbox.Add(rem_btn, 0, wx.ALL | wx.CENTER, 10)

        self.table_visible = False
        self.tab2.SetSizer(vbox)

    def toggle_table(self, event):
        if self.table_visible:
            self.grid.Hide()
            self.table_visible = False
        else:
            self.refresh_table()
            self.grid.Show()
            self.grid.ForceRefresh()
            self.tab2.Layout()
            self.table_visible = True

    def refresh_table(self):
        salary, expenses = read_data()

        rows = self.grid.GetNumberRows()
        if rows > 0:
            self.grid.DeleteRows(0, rows)

        for name, amt in expenses:
            self.grid.AppendRows(1)
            row = self.grid.GetNumberRows() - 1
            self.grid.SetCellValue(row, 0, name)
            self.grid.SetCellValue(row, 1, str(amt))

        self.grid.AutoSize()
        self.grid.ForceRefresh()

    def add_expense(self, event):
        name = self.exp_name.GetValue()
        amt = self.exp_amt.GetValue()

        if not name or not amt.isdigit():
            wx.MessageBox("Invalid input", "Error")
            return

        salary, expenses = read_data()
        expenses.append((name, int(amt)))
        write_all(salary, expenses)

        self.exp_name.SetValue("")
        self.exp_amt.SetValue("")
        self.refresh_table()
        self.update_status()

    def remove_expense(self, event):
        if not self.table_visible:
            wx.MessageBox("Table is hidden", "Error")
            return

        row = self.grid.GetGridCursorRow()
        if row < 0:
            wx.MessageBox("Select a row", "Error")
            return

        name = self.grid.GetCellValue(row, 0)
        amt = int(self.grid.GetCellValue(row, 1))

        salary, expenses = read_data()
        removed = False
        new_list = []

        for n, a in expenses:
            if n == name and a == amt and not removed:
                removed = True
                continue
            new_list.append((n, a))

        write_all(salary, new_list)
        self.refresh_table()
        self.update_status()

    # ---------- TAB 3 (Report) ----------
    def create_tab3(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self.tab3, label="Expense vs Savings Report")
        font = title.GetFont()
        font.PointSize = 12
        font.Bold()
        title.SetFont(font)

        vbox.Add(title, 0, wx.ALL | wx.CENTER, 20)

        btn = wx.Button(self.tab3, label="View Pie Chart")
        btn.Bind(wx.EVT_BUTTON, self.show_pie)
        vbox.Add(btn, 0, wx.ALL | wx.CENTER, 10)

        self.tab3.SetSizer(vbox)

    # ---------- Status ----------
    def update_status(self):
        salary, expenses = read_data()
        spent = sum(a for _, a in expenses)
        remaining = salary - spent

        percent = (remaining / salary * 100) if salary else 0
        if remaining <= 0:
            color = wx.RED
        elif percent < 5:
            color = wx.Colour(255, 140, 0)
        elif percent < 10:
            color = wx.Colour(255, 215, 0)
        else:
            color = wx.GREEN

        self.remaining_lbl.SetForegroundColour(color)
        self.remaining_lbl.SetLabel(f"Remaining Salary: ₹{remaining}")

    # ---------- Pie Chart ----------
    def show_pie(self, event):
        salary, expenses = read_data()
        data = {}

        for n, a in expenses:
            data[n] = data.get(n, 0) + a

        savings = max(salary - sum(data.values()), 0)
        data["Savings"] = savings

        if sum(data.values()) == 0:
            wx.MessageBox("No data to display", "Error")
            return

        PieWindow(self, data)


# ---------- PIE CHART WINDOW (WORKING) ----------

class PieWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Expense Distribution", size=(520, 360))

        self.data = data
        self.panel = wx.Panel(self)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)

        self.Show()

    def on_paint(self, event):
        gc = wx.GraphicsContext.Create(wx.PaintDC(self.panel))

        total = sum(self.data.values())
        center_x, center_y = 150, 150
        radius = 120

        colors = [
            wx.Colour(255, 111, 97), wx.Colour(107, 91, 149),
            wx.Colour(136, 176, 75), wx.Colour(244, 162, 97),
            wx.Colour(146, 168, 209), wx.Colour(247, 202, 201)
        ]

        start_angle = -90  # start at top (12 o’clock)
        i = 0

        # Draw slices cleanly using arcs
        for label, value in self.data.items():
            fraction = value / total
            sweep = fraction * 360

            gc.SetBrush(wx.Brush(colors[i % len(colors)]))
            gc.SetPen(wx.Pen(colors[i % len(colors)]))

            path = gc.CreatePath()
            path.MoveToPoint(center_x, center_y)

            # outer arc
            path.AddArc(
                center_x, center_y,
                radius,
                math.radians(start_angle),
                math.radians(start_angle + sweep),
                True
            )

            path.CloseSubpath()
            gc.FillPath(path)

            start_angle += sweep
            i += 1

        # Draw legend
        gc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),
                   wx.BLACK)

        lx, ly = 320, 40
        i = 0

        for label, value in self.data.items():
            percent = (value / total) * 100

            gc.SetBrush(wx.Brush(colors[i % len(colors)]))
            gc.DrawRectangle(lx, ly, 18, 18)

            gc.DrawText(f"{label} – ₹{value} ({percent:.1f}%)",
                        lx + 25, ly - 2)

            ly += 28
            i += 1



# ---------- RUN APP ----------
if __name__ == "__main__":
    app = wx.App(False)
    BudgetApp()
    app.MainLoop()