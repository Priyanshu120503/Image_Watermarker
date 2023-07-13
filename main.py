from PIL import Image, ImageFont, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import colorchooser, messagebox


def handle_save():
    with Image.open("./images/temp.png") as im:
        im.save(fileName.get())
        messagebox.showinfo(title="Success", message="Image Saved Succesfull!")


def handle_add_button():
    global img, og_img, text_img
    filetypes = (("PNG file", "*.png"), ("JPEG File", "*.jpg"))
    filename = fd.askopenfilename(title="Select an Image file", filetypes=filetypes, initialdir="./images/")
    print(filename)
    if filename:
        og_img = Image.open(filename)
        text_img = Image.new("RGBA", og_img.size, (255, 255, 255, 0))
        display_image(filename)
        x_position_scale.config(state=tk.ACTIVE, to=text_img.size[0], tickinterval=text_img.size[0]/10)
        y_position_scale.config(state=tk.ACTIVE, to=text_img.size[1], tickinterval=text_img.size[1]/10)
        for option in options:
            option.config(state=tk.NORMAL)
        fileName.set(filename[:-4] + "_watermarked" + filename[-4:])
        add_image_button.place_forget()
        add_image_label.place_forget()


def display_image(filename):
    img = Image.open(filename)

    if img.size[0] > label.winfo_width():
        rescale_factor = img.size[0] / label.winfo_width()
        img = img.resize((label.winfo_width(), int(img.size[1] / rescale_factor)))
    if img.size[1] > label.winfo_height():
        rescale_factor = img.size[1] / label.winfo_height()
        img = img.resize((int(img.size[0] / rescale_factor), label.winfo_height()))

    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    label.image = tk_img


def move_x(val):
    global img, WATERMARK_X, text_img
    img = text_img.copy()
    draw = ImageDraw.Draw(img)
    WATERMARK_X = int(val)
    bbox_coords = draw.multiline_textbbox((WATERMARK_X, WATERMARK_Y), text=watermark_text_entry.get("1.0", "end-1c"),
                                          align=align.get().lower(), stroke_width=stroke_width.get(),
                                          font=FONT)

    border_coords = [bbox_coords[0] - padx.get(),
                     bbox_coords[1] - pady.get(),
                     bbox_coords[2] + padx.get(),
                     bbox_coords[3] + pady.get()]

    if border_style.get() == "Rectangle":
        draw.rectangle(border_coords, outline=BORDER_COLOR, width=2, fill=BG_COLOR)
    elif border_style.get() == "Rounded Rectangle":
        draw.rounded_rectangle(border_coords, 15, outline=BORDER_COLOR, fill=BG_COLOR)
    elif border_style.get() == "Ellipse":
        draw.ellipse(border_coords, outline=BORDER_COLOR, fill=BG_COLOR)

    draw.multiline_text((WATERMARK_X, WATERMARK_Y), text=watermark_text_entry.get("1.0", "end-1c"),
                        align=align.get().lower(), stroke_width=stroke_width.get(), fill=COLOR_CODE,
                        font=FONT)

    img = img.rotate(TXT_ROTATION, center=((bbox_coords[0] + bbox_coords[2])/2, (bbox_coords[1] + bbox_coords[3])/2))
    out = Image.alpha_composite(og_img.convert("RGBA"), img)
    out.save("./images/temp.png")
    display_image("./images/temp.png")


def move_y(val):
    global img, WATERMARK_Y
    img = text_img.copy()
    draw = ImageDraw.Draw(img)
    # draw.rectangle([WATERMARK_X, int(val), WATERMARK_X + WATERMARK_WIDTH, int(val) + WATERMARK_HEIGHT],
    #                outline="black", width=2)
    WATERMARK_Y = int(val)
    bbox_coords = draw.multiline_textbbox((WATERMARK_X, WATERMARK_Y), text=watermark_text_entry.get("1.0", "end-1c"),
                                          align=align.get().lower(), stroke_width=stroke_width.get(),
                                          font=FONT)
    # draw.rectangle(bbox_coords, outline="black", width=2)

    border_coords = [bbox_coords[0] - padx.get(),
                     bbox_coords[1] - pady.get(),
                     bbox_coords[2] + padx.get(),
                     bbox_coords[3] + pady.get()]

    if border_style.get() == "Rectangle":
        draw.rectangle(border_coords, outline=BORDER_COLOR, width=2, fill=BG_COLOR)
    elif border_style.get() == "Rounded Rectangle":
        draw.rounded_rectangle(border_coords, 15, outline=BORDER_COLOR, fill=BG_COLOR, width=2)
    elif border_style.get() == "Ellipse":
        draw.ellipse(border_coords, outline=BORDER_COLOR, fill=BG_COLOR)

    draw.multiline_text((WATERMARK_X, WATERMARK_Y), text=watermark_text_entry.get("1.0", "end-1c"),
                        align=align.get().lower(), stroke_width=stroke_width.get(), fill=COLOR_CODE,
                        font=FONT)

    img = img.rotate(TXT_ROTATION, center=((bbox_coords[0] + bbox_coords[2])/2, (bbox_coords[1] + bbox_coords[3])/2))
    out = Image.alpha_composite(og_img.convert("RGBA"), img)
    out.save("./images/temp.png")
    display_image("./images/temp.png")


def handle_color_change():
    global COLOR_CODE
    color_code = colorchooser.askcolor(title="Choose Color")
    if color_code != (None, None):
        COLOR_CODE = tuple([i for i in color_code[0]] + [int(txt_transparency.get())])
        if og_img:
            move_x(WATERMARK_X)


def handle_transparency(**kwargs):
    global COLOR_CODE

    try:
        if kwargs.get("trans") and kwargs["trans"].isnumeric() and 0 <= int(kwargs["trans"]) <= 255:
            COLOR_CODE = tuple([i for i in COLOR_CODE][:3] + [int(txt_transparency.get())])
            move_x(WATERMARK_X)
        elif 0 <= int(txt_transparency.get()) <= 255:
            COLOR_CODE = tuple([i for i in COLOR_CODE][:3] + [int(txt_transparency.get())])
            if og_img:
                move_x(WATERMARK_X)
    except Exception as e:
        print(e)


def handle_font_size_change(**kwargs):
    try:
        if kwargs.get("char") and kwargs["char"].isnumeric() and 0 <= int(kwargs["char"]) or 0 <= int(font_size.get()):
            handle_font_changes()
    except Exception as e:
        print(e)


def handle_font_changes():
    global FONT, fonts

    if bold_check.get() and italic_check.get():
        FONT = ImageFont.truetype(fonts[font_style.get()]['bold_italic'], int(font_size.get()))
    elif bold_check.get():
        FONT = ImageFont.truetype(fonts[font_style.get()]['bold'], int(font_size.get()))
    elif italic_check.get():
        FONT = ImageFont.truetype(fonts[font_style.get()]['italic'], int(font_size.get()))
    else:
        FONT = ImageFont.truetype(fonts[font_style.get()]['normal'], int(font_size.get()))
    move_x(WATERMARK_X)


def handle_rotation(val):
    global TXT_ROTATION
    TXT_ROTATION = int(val)
    move_x(WATERMARK_X)


def handle_pad(**kwargs):
    if kwargs.get("num") and kwargs["num"].isnumeric() or (0 <= padx.get() and 0 <= pady.get()):
        move_x(WATERMARK_X)


def handle_border_color():
    global BORDER_COLOR
    color = colorchooser.askcolor(title="Select Border Color", color="black")
    if color != (None, None):
        # BORDER_COLOR = color[0]
        BORDER_COLOR = tuple([i for i in color[0][:3]] + [int(txt_transparency.get())])
        move_x(WATERMARK_X)


def handle_bg_color():
    global BG_COLOR
    color = colorchooser.askcolor(title="Select Background Color", color=None)
    if color != (None, None):
        # BG_COLOR = color[0]
        BG_COLOR = tuple([i for i in color[0][:3]] + [int(txt_transparency.get())])
        move_x(WATERMARK_X)


# -------- Constants/Variables ---------------
img = Image.new("RGBA", (100, 100), 1)
og_img = img.copy()
text_img = img.copy()

WINDOW_HEIGHT = 700
WINDOW_WIDTH = 1100
IMAGE_FRAME_WIDTH = 600
IMAGE_FRAME_HEIGHT = WINDOW_HEIGHT
OPTION_FRAME_WIDTH = WINDOW_WIDTH - IMAGE_FRAME_WIDTH
OPTION_FRAME_HEIGHT = WINDOW_HEIGHT
WATERMARK_X = 0
WATERMARK_Y = 0
WATERMARK_WIDTH = 100
WATERMARK_HEIGHT = 100
fonts = {
    "FreeMono": {
        'normal': "./fonts/freemono/FreeMono.ttf",
        'bold': "./fonts/freemono/FreeMonoBold.ttf",
        'italic': "./fonts/freemono/FreeMonoOblique.ttf",
        'bold_italic': "./fonts/freemono/FreeMonoBoldOblique.ttf",
    },
    "OpenSans": {
        'normal': "./fonts/open-sans/OpenSans-Regular.ttf",
        'bold': "./fonts/open-sans/OpenSans-Bold.ttf",
        'italic': "./fonts/open-sans/OpenSans-Italic.ttf",
        'bold_italic': "./fonts/open-sans/OpenSans-BoldItalic.ttf",
    },
    "Pacifico": {
        'normal': "./fonts/pacifico/Pacifico.ttf",
        'bold': "./fonts/pacifico/Pacifico.ttf",
        'italic': "./fonts/pacifico/Pacifico.ttf",
        'bold_italic': "./fonts/pacifico/Pacifico.ttf"
    },
    "RaleWay": {
        'normal': "./fonts/raleway/Raleway-Regular.ttf",
        'bold': "./fonts/raleway/Raleway-Bold.ttf",
        'italic': "./fonts/raleway/Raleway-Italic.ttf",
        'bold_italic': "./fonts/raleway/Raleway-BoldItalic.ttf",
    },
    "Roboto": {
        'normal': "./fonts/roboto/Roboto-Regular.ttf",
        'bold': "./fonts/roboto/Roboto-Bold.ttf",
        'italic': "./fonts/roboto/Roboto-Italic.ttf",
        'bold_italic': "./fonts/roboto/Roboto-BoldItalic.ttf",
    }
}
FONT = ImageFont.truetype(fonts["FreeMono"]["normal"], 20)
COLOR_CODE = (0, 0, 0, 128)
TXT_ROTATION = 0
BORDER_COLOR = (0, 0, 0)
BG_COLOR = None


window = tk.Tk()

window.title = "Image Watermarking"
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
window.wm_title('Image WaterMarker')

# ---------------------- Image Frame -------------------------------------
# Make a non-resizable frame and put the label in it
# Because when label has text, it is sized relative to text-content and
# When it has an image, then it is sized in pixels
img_label_frame = tk.Frame(window, width=IMAGE_FRAME_WIDTH, height=IMAGE_FRAME_HEIGHT)
img_label_frame.pack_propagate(0)

label = tk.Label(img_label_frame, bg='white', borderwidth=2, relief="solid")
label.pack(fill="both", expand=1)
add_image_label = tk.Label(label, text="Add Image", font=("Arial", 30, "bold"), bg="white")
add_image_button = tk.Button(label, width=3, text="+", font=("Arial", 40, "bold"), relief="solid", borderwidth=3,
                             command=handle_add_button)

add_image_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
add_image_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
img_label_frame.place(x=0, y=0)

# --------------------------- Option Frame ----------------------------------
watermark_text = tk.StringVar()

align = tk.StringVar()
align.set("Center")

stroke_width = tk.IntVar()
stroke_width.set(1)

font_size = tk.IntVar()
font_size.set(20)

txt_transparency = tk.StringVar()
txt_transparency.set("128")

font_style = tk.StringVar()
font_style.set("FreeMono")

bold_check = tk.IntVar()
bold_check.set(0)

italic_check = tk.IntVar()
italic_check.set(0)

border_style = tk.StringVar()
border_style.set("None")

padx = tk.IntVar()
padx.set(0)

pady = tk.IntVar()
pady.set(0)

fileName = tk.StringVar()
fileName.set("")

option_frame = tk.Frame(window, width=OPTION_FRAME_WIDTH, height=OPTION_FRAME_HEIGHT + 100)

font_label = tk.Label(option_frame, text="Font: ", font=('Arial', 10, 'normal'))
font_dropdown = tk.OptionMenu(option_frame, font_style, *[key for key in fonts.keys()],
                              command=lambda x: handle_font_changes())

bold_checkbox = tk.Checkbutton(option_frame, text="𝐁", font=("Arial", 20, 'normal'), variable=bold_check,
                               command=handle_font_changes)
italic_checkbox = tk.Checkbutton(option_frame, text="𝐼", font=("Arial", 20, 'normal'), variable=italic_check,
                                 command=handle_font_changes)

color_choose_button = tk.Button(option_frame, text="Select Text Color", command=handle_color_change, state=tk.DISABLED)

stroke_width_label = tk.Label(option_frame, text="Stroke Width", font=("Arial", 10, 'normal'))
stroke_width_dropdown = tk.OptionMenu(option_frame, stroke_width, *[i for i in range(5)],
                                      command=lambda x: move_x(WATERMARK_X))

watermark_text_entry = tk.Text(option_frame, width=30, height=5, state=tk.DISABLED)
watermark_text_entry.bind("<KeyRelease>", lambda e: move_x(WATERMARK_X))

txt_align_label = tk.Label(option_frame, text="Text Align", font=("Arial", 10, 'normal'))
align_dropdown = tk.OptionMenu(option_frame, align, *["Left", "Center", "Right"],
                               command=lambda x: move_x(WATERMARK_X))

font_size_label = tk.Label(option_frame, text="Font Size: ", font=("Arial", 10, 'normal'))
font_size_spinbox = tk.Spinbox(option_frame, textvariable=font_size, from_=1, to=300, width=5,
                               command=handle_font_size_change, state=tk.DISABLED)
font_size_spinbox.bind("<KeyRelease>", lambda e: handle_font_size_change(char=e.char))

transparency_label = tk.Label(option_frame, text="Opacity: ", font=("Arial", 10, 'normal'))
transparency_spinbox = tk.Spinbox(option_frame, from_=0, to=255, textvariable=txt_transparency, width=5,
                                  command=handle_transparency, state=tk.DISABLED)
transparency_spinbox.bind("<KeyRelease>", lambda e: handle_transparency(trans=e.char))

txt_rotation_scale = tk.Scale(option_frame, from_=-360, to=360, orient=tk.HORIZONTAL, label='Text Rotation',
                              state=tk.DISABLED, length=200, tickinterval=90, command=handle_rotation)

border_style_label = tk.Label(option_frame, text="Border Style", font=("Arial", 10, 'normal'))
border_style_dropdown = tk.OptionMenu(option_frame, border_style,
                                      *["None", "Rectangle", "Rounded Rectangle", "Ellipse"],
                                      command=lambda x: move_x(WATERMARK_X))

padx_label = tk.Label(option_frame, text="Pad-X", font=("Arial", 10, 'normal'))
padx_spinbox = tk.Spinbox(option_frame, from_=0, to=40, textvariable=padx, state=tk.DISABLED, width=4,
                          command=handle_pad)
padx_spinbox.bind("<KeyRelease>", lambda e: handle_pad(num=e.char))

pady_label = tk.Label(option_frame, text="Pad-Y", font=("Arial", 10, 'normal'))
pady_spinbox = tk.Spinbox(option_frame, from_=0, to=40, textvariable=pady, state=tk.DISABLED, width=4,
                          command=handle_pad)
pady_spinbox.bind("<KeyRelease>", lambda e: handle_pad(num=e.char))

border_color_button = tk.Button(option_frame, text="Border Color", font=("Arial", 10, 'normal'),
                                command=handle_border_color)
bg_color_button = tk.Button(option_frame, text="BG Color", font=("Arial", 10, 'normal'),
                            command=handle_bg_color)

x_position_scale = tk.Scale(option_frame, from_=0, to=img.size[0], orient=tk.HORIZONTAL, label='X Position',
                            state=tk.DISABLED, length=300, tickinterval=img.size[0]/2, command=move_x)
y_position_scale = tk.Scale(option_frame, from_=0, to=img.size[1], orient=tk.HORIZONTAL, label='Y Position',
                            state=tk.DISABLED, length=300, tickinterval=img.size[1]/2, command=move_y)

options = [font_size_spinbox, transparency_spinbox, txt_rotation_scale, color_choose_button, watermark_text_entry,
           x_position_scale, y_position_scale, padx_spinbox, pady_spinbox]

save_entry = tk.Entry(option_frame, textvariable=fileName, font=("Arial", 10, 'normal'), width=30)
save_button = tk.Button(option_frame, text="Save", command=handle_save)

stroke_width_label.place(x=415, y=32)
stroke_width_dropdown.place(x=430, y=55)
font_label.place(x=50, y=60)
font_dropdown.place(x=90, y=55)
bold_checkbox.place(x=200, y=50)
italic_checkbox.place(x=260, y=50)
color_choose_button.place(x=320, y=60)
watermark_text_entry.place(x=50, y=90)
txt_align_label.place(x=320, y=105)
align_dropdown.place(x=390, y=95)
font_size_label.place(x=320, y=135)
font_size_spinbox.place(x=400, y=135)
transparency_label.place(x=320, y=165)
transparency_spinbox.place(x=400, y=165)
border_style_label.place(x=280, y=220)
border_style_dropdown.place(x=360, y=210)
padx_label.place(x=280, y=250)
padx_spinbox.place(x=360, y=250)
border_color_button.place(x=405, y=245)
pady_label.place(x=280, y=280)
pady_spinbox.place(x=360, y=280)
bg_color_button.place(x=405, y=275)
txt_rotation_scale.place(x=50, y=200)
x_position_scale.place(x=50, y=300)
y_position_scale.place(x=50, y=400)
save_entry.place(x=100, y=550)
save_button.place(x=330, y=550)
option_frame.place(x=600, y=0)
# ---------------------------------------------------------------


window.mainloop()
