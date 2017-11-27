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



class User():
    '''
    A user object which is used to interact with users' data,
    and perform actions that affect users' data
    '''
    def __init__(self, uid):
        '''
        uid is the user id of the student we want to create
        '''
        # get user details from database
        user = db.get_user_details(conn, uid)[0]
        # assign corresponding values to variables
        self.uid = user[0]
        self.role = user[1]
        self.name = user[2]
        self.email = user[3]
        self.password = user[4]
        self.grade = user[5] # LEADERBOARD
        self.time = user[6] # LEADERBOARD
        
    # getters and setters
    def get_uid(self):
        return self.uid
    def get_role(self):
        return self.role      
    def get_name(self):
        return self.name
    def get_email(self):
        return self.email
    def get_password(self):
        return self.password  

class UserInterface(GUISkeleton):
    '''
    Objects of this type are used to generate the GUI for the User Database
    Management screen
    '''
    def __init__(self, parent, controller):
        GUISkeleton.__init__(self, parent)
        self.cont = controller
        self.labels = ["Role", "Name", "Email"]
        # label at top of the frame
        new_label = self.create_label(self, "User Database Management\n",
                                      TITLE_FONT,
                                      "Red").grid(row=0, column=1,pady=10) 
       
        # create back button 
        back_button = self.create_button(self, "Back")
        back_button["command"] = lambda : controller.show_frame('HomeScreen')
        back_button.grid(row=0, column=3)
        self.init_window()
        
        
    def init_window(self):
        '''initialises the window of the screen'''
        self.create_list_box("users", 2, 1)
        self.create_entries(2, 0)
        self.user_db_buttons()
        self.init_users_in_lb()
        
        
    def user_db_buttons(self):
        '''create the buttons to interact with the database'''
        # create a button
        delete_button = self.create_button(self, "Delete")
        delete_button["command"] = lambda : self.del_user()
        delete_button.grid(row=3, column=1, stick="E")
        
        
    def init_users_in_lb(self):
        '''initialises the users and puts them in the list box'''
        lb = self.list_box["users"]
        # create a label_string
        label_string = "uid    role    name    email"
        lb.insert(END, label_string)
        # get all the user ids
        ids = db.get_user_ids(conn)
        for uid in ids:
            user_string = self.string_uid(uid)
            lb.insert(END, user_string)
    
    
    def string_uid(self, uid):
        '''creates a string to add to list box based on the uid'''
        user_string = "{:<3}    {:<7}    {:<10}    {:<15}"
        # get the user from the id
        user = User(uid)
        # create a string to hold the result of the user
        user_string = user_string.format(uid, user.get_role(), 
                           user.get_name(), user.get_email())
        # place the string inside the list_box
        return user_string
        
        
    def create_entries(self, row, column):
        '''creates the entry boxes where the user is going to add users into'''
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
            # create first row of entries for add_user function
            # set everything nicely on the grid            
            new_entry = self.create_entry(frame, label,
                                          REGULAR_FONT).grid(row=i, column=1)
            i += 1
        add_button = self.create_button(frame, "Add")
        add_button["command"] = lambda : self.add_user()
        add_button.grid(row=i, column=1, sticky="E")
        update_button = self.create_button(frame, "Update")
        update_button["command"] = lambda : self.up_user()
        update_button.grid(row=i, column=1, sticky="W")
        frame.grid(row=row, column=column, padx=10)
        

    def del_user(self):
        '''
        delete a user from the database and show a success popup
        '''
        lb = self.list_box["users"]
        selection = lb.curselection()
        if (selection != ()):
            # get the item for the current index
            selection = lb.get(selection[0]).split()
            # remove user from databse
            db.remove_user(selection[0], conn)
            lb.delete(selection[0])
            # show popup
            showinfo("Success", "User #" + str(selection[0]) + " has been deleted")
    
    
    def up_user(self):
        '''
        updates a user selected details in the database and show a success popup
        '''        
        # get the list box
        lb = self.list_box["users"]
        selection = lb.curselection()
        
        if (selection != ()):
            # get new parameters from entry widgets in the dictionaries
            new_role = self.entry_fields[self.labels[0]].get()
            new_name = self.entry_fields[self.labels[1]].get()
            new_email = self.entry_fields[self.labels[2]].get()
        
            verified = self.verify_user_input(new_role, new_name, new_email)
            
            if (verified):
                uid = lb.get(selection[0]).split()
                # otherwise update the database with new entries
                db.update_user_role(uid[0], new_role, conn)
                db.update_user_name(uid[0], new_name, conn)
                db.update_user_email(uid[0], new_email, conn)
                # get a string representation
                user_string = self.string_uid(uid[0])
                # clear the entry fields
                self.clear_entries()
                # update the list box
                lb.delete(selection[0])
                lb.insert(selection[0], user_string)
                # show popup
                showinfo("Success", "User #" + str(uid[0]) + " has been updated")
    
    
    def verify_user_input(self, role, name, email):
        '''verifies whether a user is a valid user'''
        result = True
        # if any of the entries is blank, return a msg
        if ((role == '') or (name == '') or (email == '')) :
            result = False
        # if role is invalid return a msg
        if ((role != 'student') and (role != 'admin')) :
            result = False
        return result
    
    
    def add_user(self):
        '''
        delete a user from the database and show a success popup
        '''
       # get new parameters from entry widgets in the dictionaries
        new_role = self.entry_fields[self.labels[0]].get()
        new_name = self.entry_fields[self.labels[1]].get()
        new_email = self.entry_fields[self.labels[2]].get()
        # check if any of the entries is blank
        verified = self.verify_user_input(new_role, new_name, new_email)
        # add new user to databse and save his id number
        if (verified):
            uid = db.add_user(new_role, new_name, new_email, "", conn)
            user_string = self.string_uid(uid)   
            # clear entries
            self.clear_entries()
            lb = self.list_box["users"]
            lb.insert(END, user_string)
            # show popup
            showinfo("Success", "User #" + str(uid ) + " has been added to database")
        
        
    def clear_entries(self):
        ''' clears the entry fields that have the information'''
        self.entry_fields["Role"].set('')
        self.entry_fields["Name"].set('')
        self.entry_fields["Email"].set('') 