"""
Compare Directories.

This tool will binary compare all files of a directory recursively to all
files of a reference directory. Erroneous (not readable), differing, missing,
new and identical files are reported.

"""


__author__ = "Florian Krause <fladd@fladd.de>"
__version__ = "0.1.0"


import sys
import os
import filecmp

if sys.version[0] == '3':
    from tkinter import *
    from tkinter import ttk
    from tkinter import scrolledtext
    from tkinter import filedialog
else:
    from Tkinter import *
    import ttk
    import ScrolledText as scrolledtext
    import tkFileDialog as filedialog


class App:

    def __init__(self):
        self.reference_dir = ""
        self.test_dir = ""
        self.missing = []
        self.new = []
        self.common = []
        self.match = []
        self.mismatch = []
        self.error = []

    def get_files(self, d):
        all_files = []
        for path, subdirs, files in os.walk(d):
            for name in files:
                all_files.append(os.path.join(path, name).replace(d, ''))
        return all_files

    def compare(self):
        if not self.reference_dir.endswith(os.path.sep):
            self.reference_dir += os.path.sep
        if not self.test_dir.endswith(os.path.sep):
            self.test_dir += os.path.sep
        self.reference_files = self.get_files(self.reference_dir)
        self.test_files = self.get_files(self.test_dir)
        self.missing = list(set(self.reference_files).difference(
            set(self.test_files)))
        self.new = list(set(self.test_files).difference(
            set(self.reference_files)))
        self.common = list(set(self.reference_files).intersection(
            set(self.test_files)))
        self.match = []
        self.mismatch = []
        self.error = []
        try:
            self._progress["maximum"] = len(self.common)
        except:
            pass
        for c, f in enumerate(self.common):
            try:
                if filecmp.cmp(self.reference_dir + f, self.test_dir + f,
                               shallow=False):
                    self.match.append(f)
                else:
                    self.mismatch.append(f)
            except:
                self.error.append(f)
            try:
                self._progress["value"] = c + 1
                self._status.set(f)
                self._root.update()
            except:
                pass
        try:
            self._status.set("Done")
            self._show_report()
            self._reset_gui()
        except:
            pass

    def get_report(self):
        rtn = ""
        rtn += "Reference: {0}\nComparing: {1}\n\n".format(self.reference_dir,
                                                           self.test_dir)
        for x in self.error:
            rnt += "[ERROR]     {0}\n".format(x)
        for x in self.mismatch:
            rtn += "[DIFFERENT] {0}\n".format(x)
        for x in self.missing:
            rtn += "[MISSING]   {0}\n".format(x)
        for x in self.new:
            rtn += "[NEW]       {0}\n".format(x)
        if not self.error == [] and self.mismatch == [] and \
           self.missing == [] and self.new == []:
            rtn += ""
        for x in self.match:
            rtn += "[SAME]      {0}\n".format(x)
        return rtn

    def add_reference(self):
        self.reference_dir = filedialog.askdirectory(parent=self._root)
        try:
            self._reference.set(self.reference_dir)
            if self._test.get() != "":
                self._status.set("Ready")
                self._go.state(["!disabled"])
        except:
            pass

    def add_test(self):
        self.test_dir = filedialog.askdirectory(parent=self._root)
        try:
            self._test.set(self.test_dir)
            if self._reference.get() != "":
                self._status.set("Ready")
                self._go.state(["!disabled"])
        except:
            pass

    def _show_gui(self):
        self._root = Tk()
        self._root.title("Compare Directories")
        self._root.resizable(0, 0)
        if sys.platform.startswith("linux"):
            s = ttk.Style()
            s.theme_use("clam")

        self._reference = StringVar()
        self._test = StringVar()
        self._status = StringVar("")

        self._topframe = ttk.Frame(self._root, padding="5 5 5 5")
        self._topframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self._topframe.columnconfigure(0, weight=1)
        self._topframe.rowconfigure(0, weight=1)

        self._bottomframe = ttk.Frame(self._root, padding="5 5 5 5")
        self._bottomframe.grid(column=0, row=1, sticky=(N, W, E, S))
        self._bottomframe.columnconfigure(0, weight=1)
        self._bottomframe.rowconfigure(0, weight=1)

        ttk.Label(self._topframe, text="Reference:").grid(column=0, row=0,
                                                         sticky=(S, W))
        self._reference_entry = ttk.Entry(self._topframe, width=50,
                                         textvariable=self._reference,
                                         state="readonly")
        self._reference_entry.grid(column=0, row=1, sticky=(N, S, E, W))
        ttk.Button(self._topframe, text="Open",
                   command=self.add_reference).grid(column=1, row=1,
                                                    sticky=(N, S, E, W))

        ttk.Label(self._topframe, text="Comparing:").grid(column=0, row=2,
                                                         sticky=(S, W))
        self._test_entry = ttk.Entry(self._topframe, width=50,
                                    textvariable=self._test,
                                    state="readonly")
        self._test_entry.grid(column=0, row=3, sticky=(N, S, E, W))
        ttk.Button(self._topframe, text="Open", command=self.add_test).grid(
            column=1, row=3, sticky=(N, S, E, W))

        self._go = ttk.Button(self._bottomframe, text="Go", state="disabled",
                              command=self.compare)
        self._go.grid(column=0, row=0, sticky=(N, S))
        self._progress = ttk.Progressbar(self._bottomframe)
        self._progress.grid(column=0, row=1, sticky=(N, S, E, W))
        ttk.Label(self._bottomframe, textvariable=self._status,
                  foreground="darkgrey", width=50,
                  anchor=W).grid(column=0, row=2, sticky=(N, S, E, W))

        for child in self._topframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        for child in self._bottomframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self._reset_gui()
        self._root.mainloop()

    def _reset_gui(self):
        self._status.set("Set directories")
        self._progress["value"] = 0
        self._go.state(["disabled"])
        self._reference.set("")
        self._test.set("")

    def _show_report(self):
        report = ReportDialogue(self._root, self.get_report())
        report.show()


class ReportDialogue:

    def __init__(self, master, message):
        self.master = master
        top = self.top = Toplevel(master)
        top.title("Report")
        top.transient(master)
        top.grab_set()
        top.focus_set()

        self.text = scrolledtext.ScrolledText(top, width=77)
        self.text.pack(fill=BOTH, expand=YES)
        self.text.insert(END, message)
        self.text["state"] = "disabled"
        self.text.bind("<1>", lambda event: self.text.focus_set())

        b = ttk.Button(top, text="Close", command=self.close)
        b.pack(pady=10)

    def show(self):
        self.master.wait_window(self.top)

    def close(self):
        self.top.destroy()


if __name__ == "__main__":
    app = App()
    app._show_gui()
