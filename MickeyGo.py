#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ----------------------------------------------------
# Author:  Cui Jian & Zhu Haoyue
# Program: GUI
# Version: v2.0.0 ALPHA
# ----------------------------------------------------
import os
os.environ["MPLBACKEND"] = "agg"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import csv
import time
import math
import copy
import numpy
import threading
import subprocess
import webbrowser
import configparser
import tkinter as tk
from multiprocessing import Process, freeze_support
from PIL import Image, ImageTk
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Notebook
from scipy.spatial import Delaunay
from ultralytics import YOLO
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import logging
logging.basicConfig(level = logging.ERROR)

class Task:
	dir = None
	name = None
	lock = None
	id = None
	frame_width_on_canvas = None
	frame_height_on_canvas = None
	box = None
	red_block = None
	blue_block = None
	ymaze_box = []
	ymaze_central_point = None
	ymaze_central_triangle = []
	
	normalized_box = None
	normalized_red_block = None
	normalized_blue_block = None
	normalized_ymaze_box = []
	normalized_ymaze_central_point = None
	
	def __init__(self, id):
		self.id = id
	
	def get_filename(self):
		items = table.get_children()
		for item in items:
			if int(table.item(item, 'values')[0]) == self.id:
				return table.item(item, 'values')[1]
		return None
	
	def get_state(self):
		items = table.get_children()
		for item in items:
			if int(table.item(item, 'values')[0]) == self.id:
				return table.item(item, 'values')[2]
		return None
		
	def get_type(self):
		items = table.get_children()
		for item in items:
			if int(table.item(item, 'values')[0]) == self.id:
				return table.item(item, 'values')[3]
		return None
	
	def set_state(self, value):
		items = table.get_children()
		for item in items:
			if int(table.item(item, 'values')[0]) == self.id:
				set_table_item(item, 2, value)
				return
	
	def normalize(self):
		if self.box is not None:
			self.normalized_box = [self.box[0] / self.frame_width_on_canvas, self.box[1] / self.frame_height_on_canvas, self.box[2] / self.frame_width_on_canvas, self.box[3] / self.frame_height_on_canvas]
			self.normalized_box[0] = self.normalized_box[0] if self.normalized_box[0] < 1.0 else 1.0
			self.normalized_box[1] = self.normalized_box[1] if self.normalized_box[1] < 1.0 else 1.0
			self.normalized_box[2] = self.normalized_box[2] if self.normalized_box[2] < 1.0 else 1.0
			self.normalized_box[3] = self.normalized_box[3] if self.normalized_box[3] < 1.0 else 1.0
			#print(self.normalized_box)
			content = 'Normalized : box = {}.\n'.format(self.normalized_box)
			text.insert('end', content)
		if self.red_block is not None:
			self.normalized_red_block = [self.red_block[0] / self.frame_width_on_canvas, self.red_block[1] / self.frame_height_on_canvas, self.red_block[2] / self.frame_width_on_canvas, self.red_block[3] / self.frame_height_on_canvas]
			self.normalized_red_block[0] = self.normalized_red_block[0] if self.normalized_red_block[0] < 1.0 else 1.0
			self.normalized_red_block[1] = self.normalized_red_block[1] if self.normalized_red_block[1] < 1.0 else 1.0
			self.normalized_red_block[2] = self.normalized_red_block[2] if self.normalized_red_block[2] < 1.0 else 1.0
			self.normalized_red_block[3] = self.normalized_red_block[3] if self.normalized_red_block[3] < 1.0 else 1.0
			#print(self.normalized_red_block)
			content = 'Normalized : red_block = {}.\n'.format(self.normalized_red_block)
			text.insert('end', content)
		if self.blue_block is not None:
			self.normalized_blue_block = [self.blue_block[0] / self.frame_width_on_canvas, self.blue_block[1] / self.frame_height_on_canvas, self.blue_block[2] / self.frame_width_on_canvas, self.blue_block[3] / self.frame_height_on_canvas]
			self.normalized_blue_block[0] = self.normalized_blue_block[0] if self.normalized_blue_block[0] < 1.0 else 1.0
			self.normalized_blue_block[1] = self.normalized_blue_block[1] if self.normalized_blue_block[1] < 1.0 else 1.0
			self.normalized_blue_block[2] = self.normalized_blue_block[2] if self.normalized_blue_block[2] < 1.0 else 1.0
			self.normalized_blue_block[3] = self.normalized_blue_block[3] if self.normalized_blue_block[3] < 1.0 else 1.0
			#print(self.normalized_blue_block)
			content = 'Normalized : blue_block = {}.\n'.format(self.normalized_blue_block)
			text.insert('end', content)
		if self.ymaze_central_point is not None:
			x1 = self.ymaze_central_point[0] / self.frame_width_on_canvas if self.ymaze_central_point[0] / self.frame_width_on_canvas < 1.0 else 1.0
			y1 = self.ymaze_central_point[1] / self.frame_height_on_canvas if self.ymaze_central_point[1] / self.frame_height_on_canvas < 1.0 else 1.0
			self.normalized_ymaze_central_point = (x1, y1)
			#print(self.normalized_ymaze_central_point)
			content = 'Normalized : ymaze_central_point = {}.\n'.format(self.normalized_ymaze_central_point)
			text.insert('end', content)
		if len(self.ymaze_box) > 0:
			self.normalized_ymaze_box.clear()
			for it in range(len(self.ymaze_box)):
				x2 = self.ymaze_box[it][0] / self.frame_width_on_canvas if self.ymaze_box[it][0] / self.frame_width_on_canvas < 1.0 else 1.0
				y2 = self.ymaze_box[it][1] / self.frame_height_on_canvas if self.ymaze_box[it][1] / self.frame_height_on_canvas < 1.0 else 1.0
				self.normalized_ymaze_box.append([x2, y2])
			#print(self.normalized_ymaze_box)
			content = 'Normalized : ymaze_box = {}.\n'.format(self.normalized_ymaze_box)
			text.insert('end', content)
		
	def is_preprocess_finished(self):
		test_type = self.get_type()
		if self.id is None or self.frame_width_on_canvas is None or self.frame_height_on_canvas is None:
			return False
		if test_type == 'OF' and self.box is None:
			return False
		if test_type == 'NOR' and (self.box is None or self.red_block is None or self.blue_block is None):
			return False
		if test_type == 'YMAZE' and (len(self.ymaze_box) == 0 or self.ymaze_central_point is None or len(self.ymaze_central_triangle) == 0):
			return False
		return True
	
	def draw(self):
		radius = 3
		if self.box is not None:
			canvas.create_rectangle(self.box[0], self.box[1], self.box[2], self.box[3], outline = 'black', width=2, tags = "box")
		if self.red_block is not None:
			canvas.create_rectangle(self.red_block[0], self.red_block[1], self.red_block[2], self.red_block[3], outline = 'red', width=2, tags = "red_block")
		if self.blue_block is not None:
			canvas.create_rectangle(self.blue_block[0], self.blue_block[1], self.blue_block[2], self.blue_block[3], outline = 'blue', width=2, tags = "blue_block")
		if len(self.ymaze_box) >= 3:
			canvas.create_line(self.ymaze_box[0][0], self.ymaze_box[0][1], self.ymaze_box[-1][0], self.ymaze_box[-1][1], fill = 'black', width = 3, tags = 'line')
			for it in range(len(self.ymaze_box)):
				canvas.create_oval(self.ymaze_box[it][0] - radius, self.ymaze_box[it][1] - radius, self.ymaze_box[it][0] + radius, self.ymaze_box[it][1] + radius, fill = 'black', tags = 'pt')
				if it > 0:
					canvas.create_line(self.ymaze_box[it][0], self.ymaze_box[it][1], self.ymaze_box[it - 1][0], self.ymaze_box[it - 1][1], fill = 'black', width = 3, tags = 'line')
		if self.ymaze_central_point is not None:
			canvas.create_oval(self.ymaze_central_point[0] - radius, self.ymaze_central_point[1] - radius, self.ymaze_central_point[0] + radius, self.ymaze_central_point[1] + radius, fill = 'red', tags = 'pt')
		if len(self.ymaze_central_triangle) == 3:
			canvas.create_line(self.ymaze_box[self.ymaze_central_triangle[0]][0], self.ymaze_box[self.ymaze_central_triangle[0]][1], self.ymaze_box[self.ymaze_central_triangle[1]][0], self.ymaze_box[self.ymaze_central_triangle[1]][1], fill = 'green', width = 3, tags = 'line')
			canvas.create_line(self.ymaze_box[self.ymaze_central_triangle[0]][0], self.ymaze_box[self.ymaze_central_triangle[0]][1], self.ymaze_box[self.ymaze_central_triangle[2]][0], self.ymaze_box[self.ymaze_central_triangle[2]][1], fill = 'green', width = 3, tags = 'line')
			canvas.create_line(self.ymaze_box[self.ymaze_central_triangle[1]][0], self.ymaze_box[self.ymaze_central_triangle[1]][1], self.ymaze_box[self.ymaze_central_triangle[2]][0], self.ymaze_box[self.ymaze_central_triangle[2]][1], fill = 'green', width = 3, tags = 'line')

class ConfigEditor:
	def __init__(self, master):
		self.master = master
		self.notebook = Notebook(master)
		self.current_tab = None
		self.tabs = {}
		self.ini_file = get_program_path() + '\\config\\config.ini'
		self.load_ini()

	def load_ini(self):
		try:
			self.config = configparser.ConfigParser()
			self.config.read(self.ini_file)
			for section in self.config.sections():
				self.add_tab(section)
		except Exception as e:
			print(f'Error loading {self.ini_file}: {e}')
	
	def add_tab(self, section):
		tab = tk.Frame(self.notebook)
		tab.pack(fill = tk.BOTH, expand=True)
		section_entries = {}
		
		for key in self.config[section]:
			tk.Label(tab, text=key + ':').pack(side = tk.LEFT, padx = 5, pady = 10)
			entry = tk.Entry(tab, width=5)
			entry.insert(0, self.config[section][key])
			entry.pack(side = tk.LEFT, padx = 5, pady = 10)
			section_entries[key] = entry
				
		self.tabs[section] = section_entries
		self.notebook.add(tab, text=section)
	
	def save_ini(self):
		for section, entries in self.tabs.items():
			for key, entry in entries.items():
				self.config[section][key] = entry.get()
		with open(self.ini_file, 'w') as configfile:
			self.config.write(configfile)
		content = 'Configuration File Will Take Effect After the Program Restarts.\n'
		text.insert('end', content)

def settings():
	messagebox.showinfo(title = 'INFO', message = 'Configuration File Will Take Effect After the Program Restarts.\n')
	dialog = tk.Toplevel()
	dialog.title('Settings')
	dialog.iconbitmap(get_program_path() + r'\config\logo.ico')
	editor = ConfigEditor(dialog)
	editor.notebook.pack(fill = tk.BOTH, expand = True)
	f1 = tk.Frame(dialog)
	f1.pack(expand = 1,side = tk.BOTTOM)
	tk.Button(f1, text = 'Save', command = editor.save_ini).pack(side = tk.LEFT, padx = 5, pady = 10)
	tk.Button(f1, text = 'Close', command = dialog.destroy).pack(side = tk.LEFT, padx = 5, pady = 10)

def add():
	dialog = tk.Toplevel()
	dialog.title('Add')
	dialog.iconbitmap(get_program_path() + r'\config\logo.ico')
	dialog.resizable(False, False)
	
	label = tk.Label(dialog, text = 'Test Type : ')
	label.grid(column = 0, row = 0, padx = 10, pady = 5)
	combo_box = ttk.Combobox(dialog, values = ['OF', 'NOR', 'YMAZE'], width = 20)
	combo_box.set('OF')
	combo_box.state(['readonly'])
	combo_box.grid(column = 1, row = 0, padx = 10, pady = 5)
	
	def on_button_click():
		file_types = [('mp4', '*.mp4'), ('avi', '*.avi'), ('wmv', '*.wmv'), ('mov', '*.mov'), ('mpeg', '*.mepg'), ('All files', '*')]
		file_paths = filedialog.askopenfilenames(filetypes = file_types)
		count = len(table.get_children())
		if count > 0:
			count = int(table.item(table.get_children()[count - 1], 'values')[0])
		for file_path in file_paths:
			count = count + 1
			table.insert('', tk.END, values=(count, file_path, 'Waiting to Pre-process', combo_box.get()))
			experiment_task = Task(count)
			experiment_task_dict.update({str(count) : experiment_task})
		jump_to_line(1)
		dialog.destroy()

	button = tk.Button(dialog, text="Choose Files", width = 20, command=on_button_click)
	button.grid(column = 0, row = 1, columnspan = 2, padx = 10, pady = 5)

def line_id(line_number):
	if line_number < 1 or line_number > len(table.get_children()):
		messagebox.showerror(title = 'ERROR', message = 'Index Out of Bounds.')
		return None
	else:
		return int(table.item(table.get_children()[line_number - 1], 'values')[0])

def line_filename(line_number):
	if line_number < 1 or line_number > len(table.get_children()):
		messagebox.showerror(title = 'ERROR', message = 'Index Out of Bounds.')
		return None
	else:
		return table.item(table.get_children()[line_number - 1], 'values')[1]

def line_state(line_number):
	if line_number < 1 or line_number > len(table.get_children()):
		messagebox.showerror(title = 'ERROR', message = 'Index Out of Bounds.')
		return None
	state = table.item(table.get_children()[line_number - 1], 'values')[2]
	if state == 'Waiting to Pre-process':
		return 1
	if state == 'Waiting to Analyze':
		return 2
	if state == 'Analyzing':
		return 3
	if state == 'Done':
		return 4
	return -1

def jump_to_line(line_number):
	if line_number < 1:
		canvas.delete('all')
		return
	if line_number > len(table.get_children()):
		return
	item = table.get_children()[line_number-1]
	table.selection_set(item)
	table.focus(item)

def on_treeview_select(event):
	if len(table.selection()) < 1:
		return
	selected_item = table.selection()[0]
	line_number = table.index(selected_item) + 1
	w, h = load_init_frame(line_filename(line_number))
	content = 'Adjusted Frame 1 to Adapt to Canvas: frame_width_on_canvas = {}, frame_height_on_canvas = {}.\n'.format(w, h)
	text.insert('end', content)
	experiment_task_dict[str(line_id(line_number))].frame_width_on_canvas = w
	experiment_task_dict[str(line_id(line_number))].frame_height_on_canvas = h
	experiment_task_dict[str(line_id(line_number))].draw()
	start_x, start_y = (0, 0)
	pts.clear()
	point_id_list.clear()
	line_id_list.clear()

def load_init_frame(videopath):
	global background, image, photo
	video = cv2.VideoCapture(videopath)
	ret, frame = video.read()
	if not ret:
		messagebox.showerror(title = 'ERROR', message = 'Cannot Load the Video.')
		return -1, -1
	image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image = Image.fromarray(image)
	canvas_width = canvas.winfo_width()
	canvas_height = canvas.winfo_height()	
	aspect_ratio = image.width / image.height
	content = 'Loaded Frame 1 of the Video : frame_width = {}, frame_height = {}.\n'.format(image.width, image.height)
	text.insert('end', content)
	new_width = canvas_width
	new_height = int(new_width / aspect_ratio)
	if new_height > canvas_height:
		new_height = canvas_height
		new_width = int(new_height * aspect_ratio)
	image = image.resize((new_width, new_height), 4)
	photo = ImageTk.PhotoImage(image)
	canvas.delete('all')
	background = canvas.create_image(0, 0, image = photo, anchor = tk.NW)
	video.release()
	return new_width, new_height

def delete():
	if not table.selection():
		messagebox.showinfo(title = 'INFO', message = 'Please Select the Video to be Deleted.')
		return
	selected_item = table.selection()[0]
	if str(table.item(selected_item, 'values')[2]) == 'Analyzing':
		messagebox.showerror(title = 'ERROR', message = 'Task Analyzing, Permission Denied.')
		return
	del experiment_task_dict[table.item(selected_item, 'values')[0]]
	table.delete(selected_item)
	if len(table.get_children()) < 1:
		canvas.delete('all')
	else:
		jump_to_line(1)

def clear():
	if is_any_task_analyzing():
		messagebox.showerror(title = 'ERROR', message = 'Task Analyzing, Permission Denied.')
		return
	items = table.get_children()
	for item in items:
		table.delete(item)
	canvas.delete('all')
	experiment_task_dict.clear()

def first_video():
	if len(table.get_children()) == 0:
		messagebox.showinfo(title = 'INFO', message = 'Video List is Empty.')
		return
	selected_item = table.selection()[0]
	if table.index(selected_item) == 0:
		messagebox.showinfo(title = 'INFO', message = 'Already the First One.')
		return	
	jump_to_line(1)

def previous_video():
	if len(table.get_children()) == 0:
		messagebox.showinfo(title = 'INFO', message = 'Video List is Empty.')
		return
	selected_item = table.selection()[0]
	if table.index(selected_item) == 0:
		messagebox.showinfo(title = 'INFO', message = 'Already the First One.')
		return
	jump_to_line(table.index(selected_item))

def next_video():
	if len(table.get_children()) == 0:
		messagebox.showinfo(title = 'INFO', message = 'Video List is Empty.')
		return
	selected_item = table.selection()[0]
	if table.index(selected_item) + 1 == len(table.get_children()):
		messagebox.showinfo(title = 'INFO', message = 'Already the Last One.')
		return
	jump_to_line(table.index(selected_item) + 2)

def last_video():
	if len(table.get_children()) == 0:
		messagebox.showinfo(title = 'INFO', message = 'Video List is Empty.')
		return
	selected_item = table.selection()[0]
	if table.index(selected_item) + 1 == len(table.get_children()):
		messagebox.showinfo(title = 'INFO', message = 'Already the Last One.')
		return
	jump_to_line(len(table.get_children()))

def set_table_item(selected_item, column, value):
	if column > 3:
		messagebox.showerror(title = 'ERROR', message = 'Index Out of Bounds.')
		return
	item = table.item(selected_item)
	values = item['values']
	values[column] = value
	table.item(selected_item, values = values)

def on_drag_start(event):
	if select_mode == 4:
		on_mouse_left_down_polygen(event)
		return
	global start_x, start_y
	canvas.delete("rectangle")
	start_x = canvas.canvasx(event.x)
	start_y = canvas.canvasy(event.y)
 
def on_drag_motion(event):
	global rectangle_id
	end_x = canvas.canvasx(event.x)
	end_y = canvas.canvasy(event.y)
	canvas.delete("rectangle")
	rectangle_id = canvas.create_rectangle(start_x, start_y, end_x, end_y, outline = 'black', width = 2, tags = "rectangle")
 
def on_drag_release(event):
	global rectangle_id, select_mode
	end_x = canvas.canvasx(event.x)
	end_y = canvas.canvasy(event.y)
	canvas.delete("rectangle")
	
	if len(table.get_children()) == 0:
		return
	
	if select_mode == 1:
		rectangle_id = canvas.create_rectangle(start_x, start_y, end_x, end_y, outline = 'black', width = 2, tags = 'box')
		selected_item = table.selection()[0]
		w = experiment_task_dict[table.item(selected_item, 'values')[0]].frame_width_on_canvas
		h = experiment_task_dict[table.item(selected_item, 'values')[0]].frame_height_on_canvas	
		if w is None or h is None or w == -1 or h == -1:
			messagebox.showerror(title = 'ERROR', message = 'Illegal Value : frame_width_on_canvas / frame_height_on_canvas.')
			return
		experiment_task_dict[table.item(selected_item, 'values')[0]].box = [start_x, start_y, end_x, end_y]
		content = 'Selected the Box (Normalized) : ({}, {}, {}, {}).\n'.format(start_x / w, start_y / h, end_x / w, end_y / h)
		text.insert('end', content)
		if experiment_task_dict[table.item(selected_item, 'values')[0]].is_preprocess_finished():
			set_table_item(selected_item, 2, 'Waiting to Analyze')
			content = 'Complete the Pre-process Job.\n'
			text.insert('end', content)
		select_mode = 0
	
	if select_mode == 2:
		rectangle_id = canvas.create_rectangle(start_x, start_y, end_x, end_y, outline = 'red', width=2, tags = 'red_block')
		selected_item = table.selection()[0]
		w = experiment_task_dict[table.item(selected_item, 'values')[0]].frame_width_on_canvas
		h = experiment_task_dict[table.item(selected_item, 'values')[0]].frame_height_on_canvas	
		if w is None or h is None or w == -1 or h == -1:
			messagebox.showerror(title = 'ERROR', message = 'Illegal Value : frame_width_on_canvas / frame_height_on_canvas.')
			return
		experiment_task_dict[table.item(selected_item, 'values')[0]].red_block = [start_x, start_y, end_x, end_y]
		content = 'Selected the Red Block (Normalized) : ({}, {}, {}, {}).\n'.format(start_x / w, start_y / h, end_x / w, end_y / h)
		text.insert('end', content)
		if experiment_task_dict[table.item(selected_item, 'values')[0]].is_preprocess_finished():
			set_table_item(selected_item, 2, 'Waiting to Analyze')
			content = 'Complete the Pre-process Job.\n'
			text.insert('end', content)
		select_mode = 0
	
	if select_mode == 3:
		rectangle_id = canvas.create_rectangle(start_x, start_y, end_x, end_y, outline = 'blue', width=2, tags = 'blue_block')
		selected_item = table.selection()[0]
		w = experiment_task_dict[table.item(selected_item, 'values')[0]].frame_width_on_canvas
		h = experiment_task_dict[table.item(selected_item, 'values')[0]].frame_height_on_canvas	
		if w is None or h is None or w == -1 or h == -1:
			messagebox.showerror(title = 'ERROR', message = 'Illegal Value : frame_width_on_canvas / frame_height_on_canvas.')
			return
		experiment_task_dict[table.item(selected_item, 'values')[0]].blue_block = [start_x, start_y, end_x, end_y]
		content = 'Selected the Blue Block (Normalized) : ({}, {}, {}, {}).\n'.format(start_x / w, start_y / h, end_x / w, end_y / h)
		text.insert('end', content)
		if experiment_task_dict[table.item(selected_item, 'values')[0]].is_preprocess_finished():
			set_table_item(selected_item, 2, 'Waiting to Analyze')
			content = 'Complete the Pre-process Job.\n'
			text.insert('end', content)
		select_mode = 0

def calc_distance_between_points(pointA, pointB):
	xA, yA = pointA
	xB, yB = pointB
	return float(((xA - xB) ** 2.0 + (yA - yB) ** 2.0)**0.5)

def calculate_centroid(contour):
	M = cv2.moments(contour)
	if M['m00'] != 0:
		centroid_x = int(M['m10'] / M['m00'])
		centroid_y = int(M['m01'] / M['m00'])
	else:
		centroid_x, centroid_y = 0, 0
	return centroid_x, centroid_y

def delaunay_mesh(ptsA):
	if(len(ptsA) < 3):
		return
	radius = 3
	cx_polygen, cy_polygen = calculate_centroid(numpy.array(ptsA))
	triangles = Delaunay(ptsA)
	distance = None
	dest_tri = None
	dest_cx_tri = None
	dest_cy_tri = None
	for tri in triangles.simplices:
		cx_tri, cy_tri = calculate_centroid(numpy.array([(ptsA[tri[0]][0], ptsA[tri[0]][1]), (ptsA[tri[1]][0], ptsA[tri[1]][1]), (ptsA[tri[2]][0], ptsA[tri[2]][1])]))
		new_distance = calc_distance_between_points((cx_tri, cy_tri), (cx_polygen, cy_polygen))
		if distance is None:
			distance = new_distance
			dest_tri = tri
			dest_cx_tri = cx_tri
			dest_cy_tri = cy_tri
			continue
		if distance > new_distance:
			distance = new_distance
			dest_tri = tri
			dest_cx_tri = cx_tri
			dest_cy_tri = cy_tri
	canvas.create_oval(dest_cx_tri - radius, dest_cy_tri - radius, dest_cx_tri + radius, dest_cy_tri + radius, fill = 'red', tags = 'pt')
	canvas.create_line(ptsA[dest_tri[0]][0], ptsA[dest_tri[0]][1], ptsA[dest_tri[1]][0], ptsA[dest_tri[1]][1], fill = 'green', width = 3, tags = 'line')
	canvas.create_line(ptsA[dest_tri[0]][0], ptsA[dest_tri[0]][1], ptsA[dest_tri[2]][0], ptsA[dest_tri[2]][1], fill = 'green', width = 3, tags = 'line')
	canvas.create_line(ptsA[dest_tri[1]][0], ptsA[dest_tri[1]][1], ptsA[dest_tri[2]][0], ptsA[dest_tri[2]][1], fill = 'green', width = 3, tags = 'line')
	selected_item = table.selection()[0]
	experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_central_triangle = [dest_tri[0], dest_tri[1], dest_tri[2]]
	experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_central_point = (dest_cx_tri, dest_cy_tri)

def delete_all_lines_points():
	global point_id_list, line_id_list
	for point_id in point_id_list:
		canvas.delete(point_id)
	for line_id in line_id_list:
		canvas.delete(line_id)
	point_id_list.clear()
	line_id_list.clear()

def on_mouse_left_down_polygen(event):
	global select_mode, is_polygen_exist, start_x, start_y, pts, point_id_list, line_id_list
	selected_item = table.selection()[0]
	if select_mode != 4:
		return
	if is_polygen_exist:
		return
	start_x, start_y = (event.x, event.y)
	radius = 3
	point_id_list.append(canvas.create_oval(start_x - radius, start_y - radius, start_x + radius, start_y + radius, fill = 'black', tags = 'pt'))
	if len(pts) >= 3 and calc_distance_between_points((start_x, start_y), (pts[0][0], pts[0][1])) < 4:
		line_id_list.append(canvas.create_line(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], fill = 'black', width = 3, tags = 'line'))
		canvas.delete('tmp_pt')
		canvas.delete('tmp_line')
		if messagebox.askokcancel(title = 'INFO', message = 'Press OK to Confirm.'):
			is_polygen_exist = True
			delaunay_mesh(pts)
			experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_box = pts.copy()
			task_tmp = experiment_task_dict[table.item(selected_item, 'values')[0]]
			content = 'Selected the Y Maze Box : vertices = {}, central_point = {}, abc_entrance_index = {}.\n'.format(task_tmp.ymaze_box, task_tmp.ymaze_central_point, task_tmp.ymaze_central_triangle)
			text.insert('end', content)
			pts.clear()
			point_id_list.clear()
			line_id_list.clear()
			if experiment_task_dict[table.item(selected_item, 'values')[0]].is_preprocess_finished():
				set_table_item(selected_item, 2, 'Waiting to Analyze')
				content = 'Complete the Pre-process Job.\n'
				text.insert('end', content)
		else:
			experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_box.clear()
			experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_central_point = None
			experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_central_triangle.clear()
			delete_all_lines_points()
		return
	elif len(pts) > 0:
		line_id_list.append(canvas.create_line(start_x, start_y, pts[-1][0], pts[-1][1], fill = 'black', width = 3, tags = 'line'))
	pts.append((event.x, event.y))

def on_mouse_right_down_polygen(event):
	global select_mode, pts, point_id_list, line_id_list
	if select_mode != 4:
		return
	if len(point_id_list) > 0:
		canvas.delete(point_id_list[-1])
		point_id_list.pop()
	if len(line_id_list) > 0:
		canvas.delete(line_id_list[-1])
		line_id_list.pop()
	if len(pts) > 0:
		pts.pop()

def on_mouse_move_polygen(event):
	global select_mode, is_polygen_exist, canvas, start_x, start_y
	if select_mode != 4:
		return
	if is_polygen_exist:
		return
	radius = 4
	canvas.delete('tmp_pt')
	canvas.delete('tmp_line')
	start_x, start_y = (start_x, start_y) if start_x else (event.x, event.y)
	end_x, end_y = (event.x, event.y)
	if len(pts) > 0:
		canvas.create_line(pts[-1][0], pts[-1][1], end_x, end_y, fill = 'grey', width = 3, tags = 'tmp_line')
	if len(pts) >= 3 and calc_distance_between_points((end_x, end_y), (pts[0][0], pts[0][1])) < 4:
		canvas.create_oval(pts[0][0] - radius, pts[0][1] - radius, pts[0][0] + radius, pts[0][1] + radius, fill = 'red', tags = 'tmp_pt')

def select_box():
	global select_mode
	canvas.delete('box')
	if len(table.get_children()) == 0:
		return
	selected_item = table.selection()[0]
	experiment_task_dict[table.item(selected_item, 'values')[0]].box = None
	select_mode = 1
	messagebox.showinfo(title = 'INFO', message = 'Please Press the Left Mouse Button and Drag the Cursor to Select Box.')

def select_red_block():
	global select_mode
	canvas.delete('red_block')
	if len(table.get_children()) == 0:
		return
	selected_item = table.selection()[0]
	experiment_task_dict[table.item(selected_item, 'values')[0]].red_block = None
	select_mode = 2
	messagebox.showinfo(title = 'INFO', message = 'Please Press the Left Mouse Button and Drag the Cursor to Select Red Block.')

def select_blue_block():
	global select_mode
	canvas.delete('blue_block')
	if len(table.get_children()) == 0:
		return
	selected_item = table.selection()[0]
	experiment_task_dict[table.item(selected_item, 'values')[0]].blue_block = None
	select_mode = 3
	messagebox.showinfo(title = 'INFO', message = 'Please Press the Left Mouse Button and Drag the Cursor to Select Blue Block.')

def select_ymaze_box():
	global select_mode, start_x, start_y, pts, is_polygen_exist
	canvas.delete('pt')
	canvas.delete('line')
	if len(table.get_children()) == 0:
		return
	start_x, start_y = (0, 0)
	pts.clear()
	delete_all_lines_points()
	selected_item = table.selection()[0]
	experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_box.clear()
	experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_central_point = None
	experiment_task_dict[table.item(selected_item, 'values')[0]].ymaze_central_triangle.clear()
	is_polygen_exist = False
	select_mode = 4
	messagebox.showinfo(title = 'INFO', message = 'Please Press the Left Mouse Button to Select the Contour of Y Maze Box, Press the Right Mouse Button to Cancel Deselect.')

def send_email():
	webbrowser.open('mailto:cuijianlawyer@126.com')

def help():
	webbrowser.open(get_program_path() + r'\config\MickeyGoV2.0Help.mp4')

def open_workdir():
	webbrowser.open(workdir_label2.cget('text'))

def contact_dialog():
	dialog = tk.Toplevel()
	dialog.title('Contact Us')
	dialog.iconbitmap(get_program_path() + r'\config\logo.ico')
	dialog.geometry('500x215')
	dialog.resizable(False, False)
	version_label1 = tk.Label(dialog, text = 'Version:')
	version_label1.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = 'W')
	version_label2 = tk.Label(dialog, text = 'MickeyGo v2.0.0 Alpha')
	version_label2.grid(column = 1, row = 0, padx = 10, pady = 5, sticky = 'W')
	author_label1 = tk.Label(dialog, text = 'Author:')
	author_label1.grid(column = 0, row = 1, padx = 10, pady = 5, sticky = 'W')
	author_label2 = tk.Label(dialog, text = 'Cui Jian, Now a Lawyer & Used to be an Engineer.')
	author_label2.grid(column = 1, row = 1, padx = 10, pady = 5, sticky = 'W')	
	email_label1 = tk.Label(dialog, text = 'E-mail:')
	email_label1.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = 'W')
	email_label2 = tk.Label(dialog, text = 'cuijianlawyer@126.com', fg = 'blue', cursor = 'hand2')
	email_label2.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = 'W')
	email_label2.bind("<Button-1>", lambda event: send_email())
	wechat_label1 = tk.Label(dialog, text = 'WeChat:')
	wechat_label1.grid(column = 0, row = 3, padx = 10, pady = 5, sticky = 'W')
	wechat_label2 = tk.Label(dialog, text = 'jinyubb2018')
	wechat_label2.grid(column = 1, row = 3, padx = 10, pady = 5, sticky = 'W')
	declaration_label = tk.Label(dialog, text = 'Declaration:')
	declaration_label.grid(column = 0, row = 4, padx = 10, pady = 5, sticky = 'W')
	declaration_text = tk.Text(dialog, width = 55, height = 5)
	declaration_text.grid(column = 1, row = 4, padx = 10, pady = 5, sticky = 'EW')
	content = 'All rights reserved.\n\nThis software is prohibited from being used for any commercial purposes without the author\'s permission.'
	declaration_text.insert('end', content)
	declaration_text.config(state = 'disable')

def is_any_task_analyzing():
	items = table.get_children()
	for item in items:
		if str(table.item(item, 'values')[2]) == 'Analyzing':
			return True
	return False

def plot_heatmap_tracking(data, task_dir, task_name, video_width_margin, video_height_margin, fps, scale):
	global size_heatmap, v_min, v_max
	locationX = []
	locationY = []
	dataHeatmap = numpy.zeros([size_heatmap, size_heatmap],dtype = float)
	for i in range(1, len(data) - 1):
		locationX.append(float(data[i][1]))
		locationY.append(float(data[i][2]))
		xBar = float(data[i][1] / (video_width_margin * scale))
		yBar = float(data[i][2] / (video_height_margin * scale))
		row = int(math.ceil(xBar * size_heatmap) - 1)
		if row >= size_heatmap:
			row = size_heatmap - 1
		elif row < 0:
			row = 0
		line = int(math.ceil(yBar * size_heatmap) - 1)
		if line >= size_heatmap:
			line = size_heatmap - 1
		elif line < 0:
			line = 0
		dataHeatmap[line][row] = dataHeatmap[line][row] + 1.0 / fps
	with open(task_dir + r'\\' + task_name + '-data-heatmap.csv', 'w', newline = '') as file:
		writer = csv.writer(file)
		writer.writerows(dataHeatmap)
	fig1, ax = plt.subplots()
	im = ax.imshow(dataHeatmap, cmap='jet', interpolation = 'gaussian', vmin = v_min, vmax = v_max)
	plt.gca().invert_yaxis()
	plt.axis('off')
	pos = ax.get_position()
	ax.set_position([pos.x0, pos.y0 + 0.1, pos.width, pos.height])
	cbar_ax = fig1.add_axes([0.23, 0.1, 0.57, 0.03])
	cbar = fig1.colorbar(im, cax = cbar_ax, orientation='horizontal')
	cbar.ax.xaxis.set_tick_params(direction = 'in')
	#plt.show()
	fig1.savefig(task_dir + r'\\' + task_name + '-heatmap.jpg')
	fig2 = plt.figure()
	plt.plot(locationX, locationY)
	plt.title('Tracking Plot')
	plt.xlabel('X (mm)')
	plt.ylabel('Y (mm)')
	#plt.show()
	fig2.savefig(task_dir + r'\\' + task_name + '-tracking.jpg')
	plt.close('all')

def of_analysis(key):
	global work_directory, max_processes
	global vid_stride, video_margin, second_delay, second_termination
	global box_size_of, confidence_threshold
	global semaphore
	global model
	global lock
	global experiment_task_dict
	with semaphore:
		lock.acquire()
		progressbar.start()
		task = experiment_task_dict[key]
		filePath = task.get_filename()
		task.dir = work_directory + r'\\' +  str(task.id) + '-' + os.path.splitext(os.path.basename(filePath))[0] + '-' + time.strftime('%Y%m%d%H%M%S')
		os.makedirs(task.dir, exist_ok = True)
		task.name = os.path.splitext(os.path.basename(filePath))[0] + '-OF-ANALYSIS'
		destFilePath = task.dir + r'\\' + task.name + '.mp4'
		cap = cv2.VideoCapture(filePath)
		video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		fps = cap.get(cv2.CAP_PROP_FPS)
		frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
		skipFramesCount = int(second_delay * fps)
		cap.set(cv2.CAP_PROP_POS_FRAMES, skipFramesCount)
		roi_x, roi_y, roi_width, roi_height = int(task.normalized_box[0] * video_width), int(task.normalized_box[1] * video_height), int((task.normalized_box[2] - task.normalized_box[0]) * video_width), int((task.normalized_box[3] - task.normalized_box[1]) * video_height)
		scale = float(box_size_of / (0.5 * (roi_width + roi_height)))
		print('video_scale = %0.2f : 1.' % scale)
		roi_x_start = roi_x - video_margin if roi_x > video_margin else 0
		roi_y_start = roi_y - video_margin if roi_y > video_margin else 0
		roi_x_end = roi_x + roi_width + video_margin if roi_x + roi_width + video_margin < video_width else video_width
		roi_y_end = roi_y + roi_height + video_margin if roi_y + roi_height + video_margin < video_height else video_height
		video_width_margin = roi_width + 2 * video_margin if roi_width + 2 * video_margin < video_width else video_width
		video_height_margin = roi_height + 2 * video_margin if roi_height + 2 * video_margin < video_height else video_height
		out = cv2.VideoWriter(destFilePath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (video_width_margin, video_height_margin))
		count = 0
		number = 0
		distance = 0.0
		x1, y1 = 0.0, 0.0
		data = [['No.', 'Location-X-mm', 'Location-Y-mm', 'Distance-mm', 'Accumulated-Distance-mm']]
		lock.release()
		while True:
			count = count + 1
			if count % vid_stride != 0:
				continue
			if frameCount - count < fps * second_termination:
				break
			ret, frame = cap.read()
			if not ret:
				break
			image_tmp = frame[roi_y_start : roi_y_end, roi_x_start : roi_x_end]
			results = model.predict(source = image_tmp, imgsz = 320, conf = confidence_threshold, max_det = 4, verbose = False)
			for result in results:
				boxes = result.boxes.xyxy
				scores = result.boxes.conf
				classes = result.boxes.cls
				class_names = [model.names[int(cls)] for cls in classes]
				for box, score, class_name in zip(boxes, scores, class_names):
					#print(f'Class: {class_name}, Score: {score:.2f}, Box: {box}')
					if class_name == 'mouse_body':
						cv2.rectangle(image_tmp, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
						cv2.putText(image_tmp, class_name, (int(box[0]), int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
						number = number + 1
						if number == 1:
							step_distance = 0.0
							x1 = float((box[0] + box[2]) * 0.5 * scale)
							y1 = float((video_height_margin - (box[1] + box[3]) * 0.5)* scale)
							distance = 0.0
							data.append([number, x1, y1, step_distance, distance])
							#print("step_distance: %f mm." % step_distance)
						else:
							x2 = float((box[0] + box[2]) * 0.5 * scale)
							y2 = float((video_height_margin - (box[1] + box[3]) * 0.5)* scale)
							step_distance = float(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
							distance = distance + step_distance
							x1, y1 = x2, y2
							data.append([number, x2, y2, step_distance, distance])
							#print("step_distance: %f mm." % step_distance)
						out.write(image_tmp)
						break
				break
		#print("total_distance: %f mm." % distance)
		cap.release()
		out.release()
		lock.acquire()
		data.append(['task_name = {}'.format(task.name), 'video_path = {}'.format(filePath), 'task_id = {}'.format(task.id), 'distance = {}'.format(distance), ''])
		content = 'task_name = {}, '.format(task.name) + 'video_path = {}, '.format(filePath) + 'task_id = {}, '.format(task.id) + 'distance = {}.'.format(distance)
		text.insert('end', content)
		print(content)
		with open(task.dir + r'\\' + task.name + '-data-raw.csv', 'w', newline = '') as file:
			writer = csv.writer(file)
			writer.writerows(data)
		plot_heatmap_tracking(data, task.dir, task.name, video_width_margin, video_height_margin, fps, scale)
		task.set_state('Done')
		if not is_any_task_analyzing():
			progressbar.stop()
		lock.release()

def is_rectangle_intersect(rect1A, rect2A):
	x1A, y1A, w1A, h1A = rect1A
	x2A, y2A, w2A, h2A = rect2A
	if x1A > x2A + w2A or x2A > x1A + w1A:
		return False
	if y1A > y2A + h2A or y2A > y1A + h1A:
		return False
	return True

def nor_analysis(key):
	global work_directory, max_processes
	global vid_stride, video_margin, second_delay, second_termination
	global box_size_nor, size_exploration, size_red_block, size_blue_block, confidence_threshold
	global semaphore
	global model
	global lock
	global experiment_task_dict
	with semaphore:
		lock.acquire()
		progressbar.start()
		task = experiment_task_dict[key]
		filePath = task.get_filename()
		task.dir = work_directory + r'\\' +  str(task.id) + '-' + os.path.splitext(os.path.basename(filePath))[0] + '-' + time.strftime('%Y%m%d%H%M%S')
		os.makedirs(task.dir, exist_ok = True)
		task.name = os.path.splitext(os.path.basename(filePath))[0] + '-NOR-ANALYSIS'
		destFilePath = task.dir + r'\\' + task.name + '.mp4'
		cap = cv2.VideoCapture(filePath)
		video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		fps = cap.get(cv2.CAP_PROP_FPS)
		frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
		skipFramesCount = int(second_delay * fps)
		cap.set(cv2.CAP_PROP_POS_FRAMES, skipFramesCount)
		ret, frame = cap.read()
		roi_x, roi_y, roi_width, roi_height = int(task.normalized_box[0] * video_width), int(task.normalized_box[1] * video_height), int((task.normalized_box[2] - task.normalized_box[0]) * video_width), int((task.normalized_box[3] - task.normalized_box[1]) * video_height)
		scale = float(box_size_nor / (0.5 * (roi_width + roi_height)))
		print('video_scale = %0.2f : 1.' % scale)
		roi_x_start = roi_x - video_margin if roi_x > video_margin else 0
		roi_y_start = roi_y - video_margin if roi_y > video_margin else 0
		roi_x_end = roi_x + roi_width + video_margin if roi_x + roi_width + video_margin < video_width else video_width
		roi_y_end = roi_y + roi_height + video_margin if roi_y + roi_height + video_margin < video_height else video_height
		video_width_margin = roi_width + 2 * video_margin if roi_width + 2 * video_margin < video_width else video_width
		video_height_margin = roi_height + 2 * video_margin if roi_height + 2 * video_margin < video_height else video_height
		out = cv2.VideoWriter(destFilePath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (video_width_margin, video_height_margin))
		normalized_red_block_center = (0.5 * (task.normalized_red_block[0] + task.normalized_red_block[2]), 0.5 * (task.normalized_red_block[1] + task.normalized_red_block[3]))
		normalized_blue_block_center = (0.5 * (task.normalized_blue_block[0] + task.normalized_blue_block[2]), 0.5 * (task.normalized_blue_block[1] + task.normalized_blue_block[3]))
		red_block_exploration_rect_xywh = (int(normalized_red_block_center[0] * video_width - 0.5 * size_exploration / scale) - roi_x_start,
											int(normalized_red_block_center[1] * video_height - 0.5 * size_exploration / scale) - roi_y_start,
											int(size_exploration / scale),
											int(size_exploration / scale))
		blue_block_exploration_rect_xywh = (int(normalized_blue_block_center[0] * video_width - 0.5 * size_exploration / scale) - roi_x_start,
											int(normalized_blue_block_center[1] * video_height - 0.5 * size_exploration / scale) - roi_y_start,
											int(size_exploration / scale),
											int(size_exploration / scale))
		red_block_exploration_rect_xyxy = (int(normalized_red_block_center[0] * video_width - 0.5 * size_exploration / scale) - roi_x_start,
											int(normalized_red_block_center[1] * video_height - 0.5 * size_exploration / scale) - roi_y_start,
											int(normalized_red_block_center[0] * video_width + 0.5 * size_exploration / scale) - roi_x_start,
											int(normalized_red_block_center[1] * video_height + 0.5 * size_exploration / scale) - roi_y_start)
		blue_block_exploration_rect_xyxy = (int(normalized_blue_block_center[0] * video_width - 0.5 * size_exploration / scale) - roi_x_start,
											int(normalized_blue_block_center[1] * video_height - 0.5 * size_exploration / scale) - roi_y_start,
											int(normalized_blue_block_center[0] * video_width + 0.5 * size_exploration / scale) - roi_x_start,
											int(normalized_blue_block_center[1] * video_height + 0.5 * size_exploration / scale) - roi_y_start)
		count = 0
		number = 0
		redBlockCount = 0
		blueBlockCount = 0
		explorationRedCount = 0
		explorationBlueCount = 0
		data = [['No.', 'Location-X-mm', 'Location-Y-mm', 'Feedback', 'Accumulated-Red-Block-Time-s', 'Accumulated-Blue-Block-Time-s', 'Accumulated-Red-Block-Count', 'Accumulated-Blue-Block-Count']]
		lock.release()
		while True:
			count = count + 1
			if count % vid_stride != 0:
				continue
			if frameCount - count < fps * second_termination:
				break
			ret, frame = cap.read()
			if not ret:
				break
			image_tmp = frame[roi_y_start : roi_y_end, roi_x_start : roi_x_end]
			results = model.predict(source = image_tmp, imgsz = 320, conf = confidence_threshold, max_det = 4, verbose = False)
			for result in results:
				boxes = result.boxes.xyxy
				scores = result.boxes.conf
				classes = result.boxes.cls
				class_names = [model.names[int(cls)] for cls in classes]
				for box, score, class_name in zip(boxes, scores, class_names):
					#print(f'Class: {class_name}, Score: {score:.2f}, Box: {box}')
					if class_name == 'mouse_head':
						number = number + 1
						feedback = None
						mouse_head_rect = (int(box[0]), int(box[1]), int(box[2] - box[0]), int(box[3] - box[1]))
						x = float((box[0] + box[2]) * 0.5 * scale)
						y = float((video_height_margin - (box[1] + box[3]) * 0.5)* scale)
						cv2.rectangle(image_tmp, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
						cv2.putText(image_tmp, class_name, (int(box[0]), int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
						cv2.rectangle(image_tmp, (red_block_exploration_rect_xyxy[0], red_block_exploration_rect_xyxy[1]), (red_block_exploration_rect_xyxy[2], red_block_exploration_rect_xyxy[3]), (0, 0, 255), 2)
						cv2.rectangle(image_tmp, (blue_block_exploration_rect_xyxy[0], blue_block_exploration_rect_xyxy[1]), (blue_block_exploration_rect_xyxy[2], blue_block_exploration_rect_xyxy[3]), (255, 0, 0), 2)
						if is_rectangle_intersect(mouse_head_rect, red_block_exploration_rect_xywh):
							feedback = 'Red-Block'
							cv2.putText(image_tmp, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
							explorationRedCount = explorationRedCount + 1
							if len(data) == 1:
								redBlockCount = redBlockCount + 1
							elif len(data) > 1 and data[-1][3] != 'Red-Block':
								redBlockCount = redBlockCount + 1
						elif is_rectangle_intersect(mouse_head_rect, blue_block_exploration_rect_xywh):
							feedback = 'Blue-Block'
							cv2.putText(image_tmp, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
							explorationBlueCount = explorationBlueCount + 1
							if len(data) == 1:
								blueBlockCount = blueBlockCount + 1
							elif len(data) > 1 and data[-1][3] != 'Blue-Block':
								blueBlockCount = blueBlockCount + 1
						else:
							feedback = 'No-Block'
						data.append([number, x, y, feedback, float(explorationRedCount / fps), float(explorationBlueCount / fps), redBlockCount, blueBlockCount])
						out.write(image_tmp)
						break
				break
		cap.release()
		out.release()
		lock.acquire()
		explorationRedDuration = float(explorationRedCount / fps)
		explorationBlueDuration = float(explorationBlueCount / fps)
		explorationRatio = None if explorationRedCount + explorationBlueCount == 0 else float( explorationBlueCount / (explorationRedCount + explorationBlueCount))
		explorationScore = explorationBlueDuration - explorationRedDuration
		data.append(['task_name = {}'.format(task.name), 'video_path = {}'.format(filePath), 'task_id = {}'.format(task.id), 'explorationRedDuration = {}'.format(explorationRedDuration), 'explorationBlueDuration = {}'.format(explorationBlueDuration), 'explorationRatio = {}'.format(explorationRatio), 'explorationScore = {}'.format(explorationScore), ''])
		content = 'task_name = {}, '.format(task.name) + 'video_path = {}, '.format(filePath) + 'task_id = {}, '.format(task.id) + 'explorationRedDuration = {}, '.format(explorationRedDuration) + 'explorationBlueDuration = {}, '.format(explorationBlueDuration) + 'explorationRatio = {}, '.format(explorationRatio) + 'explorationScore = {}.'.format(explorationScore)
		text.insert('end', content)
		print(content)
		with open(task.dir + r'\\' + task.name + '-data-raw.csv', 'w', newline = '') as file:
			writer = csv.writer(file)
			writer.writerows(data)
		plot_heatmap_tracking(data, task.dir, task.name, video_width_margin, video_height_margin, fps, scale)
		task.set_state('Done')
		if not is_any_task_analyzing():
			progressbar.stop()
		lock.release()

def calc_circle_times(statesA):
	if len(statesA) < 3:
		return 0
	numCircle = 0
	for index in range(len(statesA) - 2):
		strCircle = statesA[index] + statesA[index + 1] + statesA[index + 2]
		if strCircle == 'ABC' or strCircle == 'ACB' or strCircle == 'BAC' or strCircle == 'BCA' or strCircle == 'CAB' or strCircle == 'CBA':
			numCircle = numCircle + 1
	return numCircle

def is_two_points_same_side_of_line(p0, p1, p2, p3):
	vec1 = numpy.array([p3[0] - p2[0], p3[1] - p2[1]])
	vec2 = numpy.array([p0[0] - p2[0], p0[1] - p2[1]])
	vec3 = numpy.array([p1[0] - p2[0], p1[1] - p2[1]])
	cross1 = numpy.cross(vec2, vec1)
	cross2 = numpy.cross(vec3, vec1)
	return cross1 * cross2 > 0

def is_in_arm(box_xyxy, center_point, pt1, pt2):
	box_corner1 = (box_xyxy[0], box_xyxy[1])
	box_corner2 = (box_xyxy[2], box_xyxy[3])
	box_corner3 = (box_xyxy[0], box_xyxy[3])
	box_corner4 = (box_xyxy[2], box_xyxy[1])
	return ((not is_two_points_same_side_of_line(box_corner1, center_point, pt1, pt2)) and (not is_two_points_same_side_of_line(box_corner2, center_point, pt1, pt2)) and (not is_two_points_same_side_of_line(box_corner3, center_point, pt1, pt2)) and (not is_two_points_same_side_of_line(box_corner4, center_point, pt1, pt2)))

def ymaze_analysis(key):
	global work_directory, max_processes
	global vid_stride, video_margin, second_delay, second_termination
	global arm_length, arm_width, confidence_threshold
	global semaphore
	global model
	global lock
	global experiment_task_dict
	with semaphore:
		lock.acquire()
		progressbar.start()
		task = experiment_task_dict[key]
		task.normalize()
		filePath = task.get_filename()
		task.dir = work_directory + r'\\' +  str(task.id) + '-' + os.path.splitext(os.path.basename(filePath))[0] + '-' + time.strftime('%Y%m%d%H%M%S')
		os.makedirs(task.dir, exist_ok = True)
		task.name = os.path.splitext(os.path.basename(filePath))[0] + '-YMAZE-ANALYSIS'
		destFilePath = task.dir + r'\\' + task.name + '.mp4'
		cap = cv2.VideoCapture(filePath)
		video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		fps = cap.get(cv2.CAP_PROP_FPS)
		frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
		skipFramesCount = int(second_delay * fps)
		cap.set(cv2.CAP_PROP_POS_FRAMES, skipFramesCount)
		ymaze_box_tmp = numpy.array(task.normalized_ymaze_box)
		ymaze_box_tmp[:, 0] = ymaze_box_tmp[:, 0] * video_width
		ymaze_box_tmp[:, 1] = ymaze_box_tmp[:, 1] * video_height
		roi_x, roi_y, roi_width, roi_height = cv2.boundingRect(ymaze_box_tmp.astype(int))
		roi_x_start = roi_x - video_margin if roi_x > video_margin else 0
		roi_y_start = roi_y - video_margin if roi_y > video_margin else 0
		roi_x_end = roi_x + roi_width + video_margin if roi_x + roi_width + video_margin < video_width else video_width
		roi_y_end = roi_y + roi_height + video_margin if roi_y + roi_height + video_margin < video_height else video_height
		video_width_margin = roi_width + 2 * video_margin if roi_width + 2 * video_margin < video_width else video_width
		video_height_margin = roi_height + 2 * video_margin if roi_height + 2 * video_margin < video_height else video_height
		#boxWidth = arm_width + arm_length * math.sqrt(3.0)
		#boxHeight = 1.5 * arm_length + 0.5 * arm_width * math.sqrt(3.0)
		ret, frame = cap.read()
		#mask = numpy.zeros_like(frame)
		ymaze_box_tmp = numpy.array(ymaze_box_tmp, dtype = numpy.int32)
		#cv2.polylines(mask, [ymaze_box], True, (255, 255, 255), 1)
		center_point_frame_cropped = (int(task.normalized_ymaze_central_point[0]* video_width - roi_x_start), int(task.normalized_ymaze_central_point[1]* video_height - roi_y_start))
		ymaze_box_frame_cropped = ymaze_box_tmp.copy()
		ymaze_box_frame_cropped[:, 0] -= roi_x_start
		ymaze_box_frame_cropped[:, 1] -= roi_y_start
		arm1_width_pixel = calc_distance_between_points(ymaze_box_frame_cropped[task.ymaze_central_triangle[0]], ymaze_box_frame_cropped[task.ymaze_central_triangle[1]])
		arm2_width_pixel = calc_distance_between_points(ymaze_box_frame_cropped[task.ymaze_central_triangle[0]], ymaze_box_frame_cropped[task.ymaze_central_triangle[2]])
		arm3_width_pixel = calc_distance_between_points(ymaze_box_frame_cropped[task.ymaze_central_triangle[1]], ymaze_box_frame_cropped[task.ymaze_central_triangle[2]])
		scale = arm_width / ((arm1_width_pixel + arm2_width_pixel + arm3_width_pixel) / 3)
		print('video_scale = %0.2f : 1.' % scale)
		out = cv2.VideoWriter(destFilePath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (video_width_margin, video_height_margin))
		count = 0
		number = 0
		states = []
		data = [['No.', 'Location-X-mm', 'Location-Y-mm', 'State-A/B/C/N', 'Accumulated-Number-of-Cycles', 'Accumulated-Rate-of-Cycles']]
		lock.release()
		while True:
			count = count + 1
			if count % vid_stride != 0:
				continue
			if frameCount - count < fps * second_termination:
				break
			ret, frame = cap.read()
			if not ret:
				break
			#cropped = cv2.bitwise_and(frame, mask)
			image_tmp = frame[roi_y_start : roi_y_end, roi_x_start : roi_x_end]
			results = model.predict(source = image_tmp, imgsz = 320, conf = confidence_threshold, max_det = 4, verbose = False)
			for result in results:
				boxes = result.boxes.xyxy
				scores = result.boxes.conf
				classes = result.boxes.cls
				class_names = [model.names[int(cls)] for cls in classes]
				for box, score, class_name in zip(boxes, scores, class_names):
					#print(f'Class: {class_name}, Score: {score:.2f}, Box: {box}')
					if class_name == 'mouse_body':
						cv2.circle(image_tmp, center_point_frame_cropped, 1, (0, 0, 255), 2)
						cv2.line(image_tmp, ymaze_box_frame_cropped[task.ymaze_central_triangle[0]], ymaze_box_frame_cropped[task.ymaze_central_triangle[1]], (0, 0, 255), 2)
						cv2.line(image_tmp, ymaze_box_frame_cropped[task.ymaze_central_triangle[0]], ymaze_box_frame_cropped[task.ymaze_central_triangle[2]], (0, 0, 255), 2)
						cv2.line(image_tmp, ymaze_box_frame_cropped[task.ymaze_central_triangle[1]], ymaze_box_frame_cropped[task.ymaze_central_triangle[2]], (0, 0, 255), 2)
						cv2.rectangle(image_tmp, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
						cv2.putText(image_tmp, class_name, (int(box[0]), int(box[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
						cv2.polylines(image_tmp, [ymaze_box_frame_cropped], True, (255, 0, 255), 1)
						number = number + 1
						mouse_head_rect = (int(box[0]), int(box[1]), int(box[2] - box[0]), int(box[3] - box[1]))
						x = float((box[0] + box[2]) * 0.5 * scale)
						y = float((video_height_margin - (box[1] + box[3]) * 0.5)* scale)
						state = 'N'
						if is_in_arm(box, center_point_frame_cropped, ymaze_box_frame_cropped[task.ymaze_central_triangle[0]], ymaze_box_frame_cropped[task.ymaze_central_triangle[1]]):
							state = 'A'
						elif is_in_arm(box, center_point_frame_cropped, ymaze_box_frame_cropped[task.ymaze_central_triangle[0]], ymaze_box_frame_cropped[task.ymaze_central_triangle[2]]):
							state = 'B'
						elif is_in_arm(box, center_point_frame_cropped, ymaze_box_frame_cropped[task.ymaze_central_triangle[1]], ymaze_box_frame_cropped[task.ymaze_central_triangle[2]]):
							state = 'C'
						if state != 'N':
							cv2.putText(image_tmp, state, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
						if len(states):
							if states[-1] != state and state != 'N':
								states.append(state)
						else:
							if state != 'N':
								states.append(state)
						inArmTimes = len(states) if len(states) > 0 else 1
						data.append([number, x, y, state, calc_circle_times(states), float(calc_circle_times(states) / inArmTimes)])
						out.write(image_tmp)
						break
				break
		cap.release()
		out.release()
		lock.acquire()
		inArmTimes = len(states) if len(states) > 0 else 1
		effStates = ''.join(str(it) for it in states)
		effCircleTimes = calc_circle_times(states)
		effCircleRate = float(calc_circle_times(states) / inArmTimes)
		data.append(['task_name = {}'.format(task.name), 'video_path = {}'.format(filePath), 'task_id = {}'.format(task.id), 'effStates = {}'.format(effStates), 'effCircleTimes = {}'.format(effCircleTimes), 'effCircleRate = {}'.format(effCircleRate)])
		content = 'task_name = {}, '.format(task.name) + 'video_path = {}, '.format(filePath) + 'task_id = {}, '.format(task.id) + 'effStates = {}, '.format(effStates) + 'effCircleTimes = {}, '.format(effCircleTimes) + 'effCircleRate = {}.'.format(effCircleRate)
		text.insert('end', content)
		print(content)
		with open(task.dir + r'\\' + task.name + '-data-raw.csv', 'w', newline = '') as file:
			writer = csv.writer(file)
			writer.writerows(data)
		plot_heatmap_tracking(data, task.dir, task.name, video_width_margin, video_height_margin, fps, scale)
		task.set_state('Done')
		if not is_any_task_analyzing():
			progressbar.stop()
		lock.release()

def start_this():
	if len(table.get_children()) == 0:
		return
	selected_item = table.selection()[0]
	experiment_task_dict[table.item(selected_item, 'values')[0]].normalize()
	task_tmp = experiment_task_dict[table.item(selected_item, 'values')[0]]
	test_type = task_tmp.get_type()
	if not task_tmp.is_preprocess_finished():
		messagebox.showerror(title = 'ERROR', message = 'Task {} should be Pre-process before Starting.'.format(table.item(selected_item, 'values')[0]))
		return
	task_tmp.set_state('Analyzing')
	if test_type == 'OF':
		thread = threading.Thread(target = of_analysis, args = ((table.item(selected_item, 'values')[0], )))
		thread .start()
	if test_type == 'NOR':
		thread = threading.Thread(target = nor_analysis, args = ((table.item(selected_item, 'values')[0], )))
		thread .start()
	if test_type == 'YMAZE':
		thread = threading.Thread(target = ymaze_analysis, args = ((table.item(selected_item, 'values')[0], )))
		thread .start()
	messagebox.showinfo(title = 'INFO', message = 'Task {} Start.'.format(table.item(selected_item, 'values')[0]))

def start_all():
	global experiment_task_dict
	if len(table.get_children()) == 0:
		return
	ids = ''
	items = table.get_children()
	for item in items:
		experiment_task_dict[table.item(item, 'values')[0]].normalize()
		test_type = table.item(item, 'values')[3]
		test_state = table.item(item, 'values')[2]
		task_tmp = experiment_task_dict[table.item(item, 'values')[0]]
		if test_state == 'Analyzing' or test_state == 'Done':
			continue
		if task_tmp.is_preprocess_finished():
			task_tmp.set_state('Analyzing')
			ids += str(task_tmp.id) + ' '
			if test_type == 'OF':
				thread = threading.Thread(target = of_analysis, args = ((table.item(item, 'values')[0], )))
				thread .start()
			if test_type == 'NOR':
				thread = threading.Thread(target = nor_analysis, args = ((table.item(item, 'values')[0], )))
				thread .start()
			if test_type == 'YMAZE':
				thread = threading.Thread(target = ymaze_analysis, args = ((table.item(item, 'values')[0],)))
				thread .start()
	messagebox.showinfo(title = 'INFO', message = 'Task {}Start.'.format(ids))

def get_program_path():
	#path = os.path.dirname(os.path.abspath(__file__))
	path = os.path.dirname(os.path.realpath(sys.executable))
	return path

def initialize():
	config_path = get_program_path() + r'\config\config.ini'
	config = configparser.ConfigParser()
	config.read(config_path)
	text.insert('end', 'MICKEYGO-V2.0.0 ALPHA INITIALIZE...\n')
	content = 'Load Configuration File, Initialize Global Variables...\n'
	text.insert('end', content)
	print(content)
	
	global work_directory, max_processes, confidence_threshold
	global vid_stride, video_margin, second_delay, second_termination
	global box_size_of
	global box_size_nor, size_exploration, size_red_block, size_blue_block
	global arm_length, arm_width
	global size_heatmap, v_min, v_max
	global semaphore
	global model
	work_directory = get_program_path() if str(config['TASK']['work_directory']) == r'/' else str(config['TASK']['work_directory'])
	workdir_label2.config(text = work_directory)
	max_processes = int(config['TASK']['max_processes'])
	confidence_threshold = float(config['TASK']['confidence_threshold'])
	vid_stride = int(config['VIDEO']['vid_stride'])
	video_margin = int(config['VIDEO']['video_margin'])
	second_delay = int(config['VIDEO']['second_delay'])
	second_termination = int(config['VIDEO']['second_termination'])
	box_size_of = float(config['OF']['box_size_of'])
	box_size_nor = float(config['NOR']['box_size_nor'])
	size_exploration = float(config['NOR']['size_exploration'])
	size_red_block = float(config['NOR']['size_red_block'])
	size_blue_block = float(config['NOR']['size_blue_block'])
	arm_length = float(config['YMAZE']['arm_length'])
	arm_width = float(config['YMAZE']['arm_width'])
	size_heatmap = int(config['HEATMAP']['size_heatmap'])
	v_min = int(config['HEATMAP']['v_min'])
	v_max = int(config['HEATMAP']['v_max'])
	
	content = 'work_directory : {}, max_processes : {}, confidence_threshold : {}.\n'.format(work_directory, str(max_processes), str(confidence_threshold))
	text.insert('end', content)
	print(content)
	content = 'vid_stride : {}, video_margin : {}, second_delay : {}, second_termination : {}.\n'.format(str(vid_stride), str(video_margin), str(second_delay), str(second_termination))
	text.insert('end', content)
	print(content)
	content = 'box_size_of : {}.\n'.format(str(box_size_of))
	text.insert('end', content)
	print(content)
	content = 'box_size_nor : {}, size_exploration : {}, size_red_block : {}, size_blue_block : {}.\n'.format(str(box_size_nor), str(size_exploration), str(size_red_block), str(size_blue_block))
	text.insert('end', content)
	print(content)
	content = 'arm_length : {}, arm_width : {}.\n'.format(str(arm_length), str(arm_width))
	text.insert('end', content)
	print(content)
	content = 'size_heatmap : {}, v_min : {}, v_max : {}.\n'.format(str(size_heatmap), str(v_min), str(v_max))
	text.insert('end', content)
	print(content)
	semaphore = threading.Semaphore(max_processes)
	content = 'Loading Machine Vision System.\n'
	text.insert('end', content)
	print(content)
	model = YOLO(get_program_path() + r'\config\best.pt')
	content = 'Loaded Machine Vision System.\n'
	text.insert('end', content)
	print(content)
	content = 'MICKEYGO-V2.0.0 ALPHA SUCCESSFULLY LAUNCHED.\n'
	text.insert('end', content)
	print(content)

if __name__ == '__main__':
	freeze_support()
	print('\nMICKEYGO-V2.0.0 ALPHA INITIALIZE...\n')
	root = tk.Tk()
	root.title('MickeyGo - Behavioral Analysis of Mouse')
	root.iconbitmap(get_program_path() + r'\config\logo.ico')
	root.geometry('1210x650')
	root.resizable(False, False)
	
	group_box_step1 = ttk.LabelFrame(root, text = 'Step1 - Import Videos')
	group_box_step1.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	add_button = tk.Button(group_box_step1, text = 'Add', command = add)
	add_button.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	delete_button = tk.Button(group_box_step1, text = 'Delete', command = delete)
	delete_button.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	clear_button = tk.Button(group_box_step1, text = 'Clear', command = clear)
	clear_button.grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	group_box_step2 = ttk.LabelFrame(root, text = 'Step2 - Select Video')
	group_box_step2.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	first_button = tk.Button(group_box_step2, text = '|<', command = first_video)
	first_button.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	pre_button = tk.Button(group_box_step2, text = '<<', command = previous_video)
	pre_button.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	next_button = tk.Button(group_box_step2, text = '>>', command = next_video)
	next_button.grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	last_button = tk.Button(group_box_step2, text = '>|', command = last_video)
	last_button.grid(column = 3, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	group_box_step3 = ttk.LabelFrame(root, text = 'Step3 - Select ROI')
	group_box_step3.grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	select_box_button = tk.Button(group_box_step3, text = 'Box', command = select_box)
	select_box_button.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	select_red_block_button = tk.Button(group_box_step3, text = 'Red Block', command = select_red_block)
	select_red_block_button.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	select_blue_block_button = tk.Button(group_box_step3, text = 'Blue Block', command = select_blue_block)
	select_blue_block_button.grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	select_ymaze_box_button = tk.Button(group_box_step3, text = 'Y Maze Box', command = select_ymaze_box)
	select_ymaze_box_button.grid(column = 3, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	group_box_step4 = ttk.LabelFrame(root, text = 'Step4 - Analyze')
	group_box_step4.grid(column = 3, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	start_button = tk.Button(group_box_step4, text = 'Start This', command = start_this)
	start_button.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	start_all_button = tk.Button(group_box_step4, text = 'Start', command = start_all)
	start_all_button.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	group_box_others = ttk.LabelFrame(root, text = 'Others')
	group_box_others.grid(column = 4, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	settings_button = tk.Button(group_box_others, text = 'Settings', command = settings)
	settings_button.grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	help_button = tk.Button(group_box_others, text = 'Help', command = help)
	help_button.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	contact_us_button = tk.Button(group_box_others, text = 'Contact Us', command = contact_dialog)
	contact_us_button.grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'EW')
	
	group_box_list = ttk.LabelFrame(root, text = 'Video List')
	group_box_list.grid(column = 0, row = 2, columnspan = 3, padx = 10, pady = 10, sticky = 'EW')
	
	columns = ['ID', 'Filename', 'State', 'Type']
	table = ttk.Treeview(master = group_box_list, selectmode = 'browse', columns = columns, height = 15, show = 'headings')
	
	scrollbar1 = ttk.Scrollbar(group_box_list, orient = "vertical", command = table.yview)
	scrollbar1.pack(side = 'right', fill = 'y')
	table.configure(yscrollcommand = scrollbar1.set)
	
	table.heading(column = 'ID', text = 'ID', anchor = 'w')
	table.heading('Filename', text = 'Filename', anchor = 'w')
	table.heading('State', text = 'State', anchor = 'w')
	table.heading('Type', text = 'Type', anchor = 'w')
	
	table.column('ID', width = 20, anchor = 'w')
	table.column('Filename', anchor = 'w')
	table.column('State', anchor = 'w')
	table.column('Type', anchor = 'w')
	table.pack(padx = 10, pady = 10, fill = 'both')
	
	table.bind('<<TreeviewSelect>>', on_treeview_select)
	
	group_box_canvas = ttk.LabelFrame(root, text = 'Canvas')
	group_box_canvas.grid(column = 3, row = 2, columnspan = 2, padx = 10, pady = 10, sticky = 'EW')
	
	canvas = tk.Canvas(group_box_canvas, height = 320)
	canvas.pack(padx = 10, pady = 10, fill = 'both')
	
	canvas.bind('<Button-1>', on_drag_start)
	canvas.bind('<B1-Motion>', on_drag_motion)
	canvas.bind('<ButtonRelease-1>', on_drag_release)
	canvas.bind('<Button-3>', on_mouse_right_down_polygen)
	canvas.bind('<Motion>', on_mouse_move_polygen)
	
	group_box_console = ttk.LabelFrame(root, text = 'Console')
	group_box_console.grid(column = 0, row = 3, columnspan = 5, padx = 10, pady = 10, sticky = 'EW')
	
	text = tk.Text(group_box_console, height = 5)
	scrollbar2 = ttk.Scrollbar(group_box_console, orient = "vertical", command = text.yview)
	scrollbar2.pack(side = 'right', fill = 'y')
	text.configure(yscrollcommand = scrollbar2.set)
	text.pack(padx = 10, pady = 10, fill = 'both')
	
	progressbar = ttk.Progressbar(root, mode = 'determinate')
	progressbar.grid(column = 0, row = 4, columnspan = 2, padx = 10, pady = 10, sticky = 'EW')
	
	workdir_label1 = tk.Label(root, text = 'Work Directory : ')
	workdir_label1.grid(column = 3, row = 4, padx = 10, pady = 10, sticky = 'E')
	workdir_label2 = tk.Label(root, text = '', fg = 'blue', cursor = 'hand2')
	workdir_label2.grid(column = 4, row = 4, padx = 10, pady = 10, sticky = 'E')
	workdir_label2.bind("<Button-1>", lambda event: open_workdir())
	
	select_mode = 0
	start_x, start_y = (0, 0)
	pts = []
	point_id_list = []
	line_id_list = []
	is_polygen_exist = False
	
	experiment_task_dict = dict({})
	experiment_task_dict.clear()
	
	work_directory, max_processes, confidence_threshold = None, None, None
	vid_stride, video_margin, second_delay, second_termination = None, None, None, None
	box_size_of = None
	box_size_nor, size_exploration, size_red_block, size_blue_block = None, None, None, None
	arm_length, arm_width = None, None
	size_heatmap, v_min, v_max = None, None, None
	semaphore = None
	model = None
	lock = threading.Lock()
	
	initialize()
	
	root.mainloop()
