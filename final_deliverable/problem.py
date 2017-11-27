import tkinter as tk
from tkinter import ttk, font,  Tk, Label, Button, Entry,\
                    StringVar, DISABLED, NORMAL, END, W, E
from tkinter.messagebox import showinfo
import database_api as db
from assignments import *
from gui_skeleton import *

APP_HIGHLIGHT_FONT = ("Helvetica", 14, "bold")
REGULAR_FONT = ("Helvetica", 12, "normal")
TITLE_FONT = ("Helvetica", 14, "normal")
NICE_BLUE = "#3399FF"
HOME_FONT = ("Comic Sans", 26, "bold")

conn = sqlite3.connect('ace.db')

class Problem():
    '''
    A problem object which is used to interact with problems' data,
    and perform actions that affect problems' data
    '''
    def __init__(self, qid):
        '''
        qid is the problem id of the student we want to create
        '''
        # get problem details from database
        problem = db.get_problem_details(conn, qid)[0]
        # assign corresponding values to variables
        self.qid = problem[0]
        self.subject = problem[1]
        self.question = problem[2]
        self.answer = problem[3]
        
    # getters and setters
    def get_qid(self):
        return self.qid
    def get_subject(self):
        return self.subject      
    def get_question(self):
        return self.question
    def get_answer(self):
        return self.answer
    

class ProblemInterface(GUISkeleton):
    '''
    Objects of this type are used to genereate the GUI for the problem Database
    Management screen
    '''
    def __init__(self, parent, controller):
        GUISkeleton.__init__(self, parent)
        self.cont = controller
        self.labels = ["Subject", "Question", "Answer"]
        # label at top of the frame
        title = self.create_label(self, "Problem Database Management\n",
                                  TITLE_FONT,
                                  "Red").grid(row=0, column=1, pady=10)
        # dictionaries to contain the widgets and associate widget to
        # correspondin problem id
        
        back_button = self.create_button(self, "Back")
        # set button method to add_problem
        back_button["command"] = lambda: controller.show_frame('HomeScreen')
        back_button.grid(row=0, column=3)
        self.init_window()
        # generate all the dynamically generated widget rows
        #self.gen_rows()
        
        # enable clicking functionality for all the buttons
       # self.enable_buttons()
       
    def init_window(self):
        '''intialises the GUI window'''
        self.create_list_box("problems", 2, 1)
        self.create_entries(2,0)
        self.problem_db_buttons()
        self.init_problems_in_lb()
        
        
    def create_entries(self, row, column):
        '''creates the entry boxes where the problem is going to add problems into'''
        # create a new_frame
        frame = ttk.Frame(self)
        # create an entry for each 
        # the 3 static lables that are always there
        i = 0
        for label in self.labels:
            new_label = self.create_label(frame, label, REGULAR_FONT,
                                          NICE_BLUE).grid(row=i, column=0,
                                                          padx=10)
            # create first row of entries for add_problem function
            # set everything nicely on the grid
            # create first row of entries for add_problem function
            # set everything nicely on the grid            
            new_entry = self.create_entry(frame, label,
                                          REGULAR_FONT).grid(row=i, column=1)
            i += 1
            # add the buttons to the frame
        add_button = self.create_button(frame, "Add")
        add_button["command"] = lambda : self.add_problem()
        add_button.grid(row=i, column=1, sticky="E")
        update_button = self.create_button(frame, "Update")
        update_button["command"] = lambda : self.up_problem()
        update_button.grid(row=i, column=1, sticky="W")
        frame.grid(row=row, column=column, padx=10)        
    
            
    def problem_db_buttons(self):
        '''create the buttons to interact with the database'''
        # create a button
        delete_button = self.create_button(self, "Delete")
        delete_button["command"] = lambda : self.del_problem()
        delete_button.grid(row=3, column=1, stick="E")
        
        
    def init_problems_in_lb(self):
        '''initialises the problems and puts them in the list box'''
        lb = self.list_box["problems"]
        # create a label_string
        label_string = "qid    subject    question    answer"
        lb.insert(END, label_string)
        # get all the problem ids
        ids = db.get_problem_ids(conn)
        for qid in ids:
            problem_string = self.string_qid(qid)
            lb.insert(END, problem_string)
    
    
    def string_qid(self, qid):
        '''creates a string to add to list box based on the uid'''
        problem_string = "{:<3}    {:<7}    {:<10}    {:<15}"
        # get the problem from the id
        problem = Problem(qid)
        # create a string to hold the result of the problem
        problem_string = problem_string.format(qid, problem.get_subject(), 
                           problem.get_question(), problem.get_answer())
        # place the string inside the list_box
        return problem_string    
        
 
    def del_problem(self):
        '''
        delete a problem from the database and show a success popup
        '''
        lb = self.list_box["problems"]
        # get the index of the selected item
        selection = lb.curselection()
        if (selection != ()):
            # get the item at the index
            problem = lb.get(selection[0]).split()
            # remove problem from database
            db.remove_problem(problem[0], conn)
            # remove from the list box
            lb.delete(selection[0])
            # show popup
            showinfo("Success", "problem #" + 
                     str(problem[0]) + " has been deleted")
    
    
    def up_problem(self):
        '''
        updates a problem details in the database and show a success popup
        '''        
        lb = self.list_box["problems"]
        selection = lb.curselection()
        
        # check to make sure that we have something selected
        if (selection != ()):
            # get new parameters from entry widgets in the dictionaries
            new_subject = self.entry_fields[self.labels[0]].get()
            new_question = self.entry_fields[self.labels[1]].get()
            new_answer = self.entry_fields[self.labels[2]].get()
            
            verified = self.verify_problem_input(new_subject, new_question,
                                                 new_answer)
            if (verified):
                qid = lb.get(selection[0]).split()
                # update the database with new entries
                db.update_problem_subject(qid[0], new_subject, conn)
                db.update_problem_question(qid[0], new_question, conn)
                db.update_problem_answer(qid[0], new_answer, conn)
                # create a string representation to put in the listbox
                problem_string = self.string_qid(qid[0])
                # clear entry boxes
                self.clear_entries()
                # delete from listbox and readd at same index
                lb.delete(selection[0])
                lb.insert(selection[0], problem_string)
                # show popup
                showinfo("Success", "problem #" + str(qid[0]) + " has been updated")


    def verify_problem_input(self, subject, question, answer):
        '''verifies whether a problem is a valid problem'''
        result = True
        # if any of the entries is blank, return a msg
        if ((subject == '') or (question == '') or (answer == '')) :
            result = False
        return result
    
    def clear_entries(self):
        ''' clears the entry fields that have the information'''
        self.entry_fields[self.labels[0]].set('')
        self.entry_fields[self.labels[1]].set('')
        self.entry_fields[self.labels[2]].set('')  
    
    
    def add_problem(self):
        '''
        add a problem from the database and show a success popup
        '''
        lb = self.list_box["problems"]  
        # get new parameters from entry widgets in the dictionaries
        new_subject = self.entry_fields[self.labels[0]].get()
        new_question = self.entry_fields[self.labels[1]].get()
        new_answer = self.entry_fields[self.labels[2]].get() 
        verified = self.verify_problem_input(new_subject, new_question,
                                             new_answer)
        if (verified):
            # add new problem to databse and save his id number
            qid = db.add_problem(new_subject, new_question, new_answer, conn)
            # create a string representation to put in the listbox
            problem_string = self.string_qid(qid)
            # clear entry boxes
            self.clear_entries()
            # add problem to list box
            lb.insert(END, problem_string)
            # show popup
            showinfo("Success", "problem #" +
                     str(qid) + " has been added to database")