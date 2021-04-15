import random

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from detect import imd_movie_picker 
 
 
class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Movie Picker")
        self.minsize(600, 300) 
        self.labelFrame = ttk.LabelFrame(self, text = "Open File")
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 20)
        self.labelFrame2 = ttk.LabelFrame(self, text = "Movie Name")
        self.labelFrame2.grid(column = 0, row = 5, padx = 20, pady = 20) 
        self.v = StringVar()
        self.vS = StringVar()
        self.first = True
        self.first2 = True
        self.button()
    
    def get_imd_summary(self,url):
        movie_page = requests.get(url)
        soup = BeautifulSoup(movie_page.text, 'html.parser')
        return soup.find("div", class_="summary_text").contents[0].strip()

    def oneMain(self):
        le = len(self.movieList)
        val = self.movieList[random.randint(0,le - 1)]
        self.v.set(val)
        # movie_url = 'http://www.imdb.com' + val
        # movie_summary = self.get_imd_summary(self.movie_url)
        if self.first:
            self.w = ttk.Label(self.labelFrame2, textvariable=self.v)
            self.w.grid(column = 1, row = 1)
            self.first = False    
 
    def imdbM(self):
        name, year, summary = imd_movie_picker()
        self.v.set(name+year)
        self.vS.set(summary)
        if self.first:
            self.w = ttk.Label(self.labelFrame2, textvariable=self.v)
            self.w.grid(column = 1, row = 1)
            self.first = False
        # self.wS =  ttk.Label(self.w,textvariable = self.vS)
        # self.wS.grid(column = 0,row = 6)

    def button(self):
        self.button = ttk.Button(self.labelFrame, text = "Browse A File",command = self.fileDialog)
        self.button.grid(column = 1, row = 1)
        self.button1 = ttk.Button(self, text = "Generate a Top Imdb movie",command = self.imdbM)
        self.button1.grid(column = 1, row = 3)
 
    def fileDialog(self):
        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("text files","*.txt"),("all files","*.*")) )
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = self.filename)
        with open(self.filename) as f:
            self.movieList = f.readlines()
        self.button2 = ttk.Button(self, text = "Generate a random movie",command = self.oneMain)
        self.button2.grid(column = 0, row = 3)
 
root = Root()
root.mainloop()