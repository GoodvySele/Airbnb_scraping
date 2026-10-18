import customtkinter as ctk
from tkcalendar import DateEntry
from all_logic import start_primary_thread
import datetime


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("600x780")
app.title("Airbnb SCRAPING")


scraping_process_label = ctk.CTkLabel(
    app,
    text="Adjust your search settings",
    font=("Arial", 18, "bold")
)
scraping_process_label.pack(pady=10)

entry_city = ctk.CTkEntry(app, placeholder_text="Enter the city (ex: Brazzaville)", width=250)
entry_city.pack(pady=10)

label_result1 = ctk.CTkLabel(app, text="")
label_result1.pack(pady=5)

date_options_frame = ctk.CTkFrame(app, fg_color="black")
date_options_frame.pack(fill="x", padx=30, pady=5)
date_options_frame.grid_columnconfigure(0, weight=1)
date_options_frame.grid_columnconfigure(1, weight=1)
date_options_frame.grid_columnconfigure(2, weight=1)


dates_frame = ctk.CTkFrame(date_options_frame, fg_color="transparent")
dates_frame.grid(row=0, column=0, sticky="w")



label_arrival_date = ctk.CTkLabel(dates_frame, text="Check-In date", font=("Arial", 12, "italic"))
label_arrival_date.pack(anchor="w", padx=(20, 0), pady=(0, 0))

arrival_date = DateEntry(
    dates_frame, width=17, background='#1F6AA5', foreground='white',
    headersbackground='#2B2B2B', headersforeground='white',
    showweeknumbers=False, date_pattern='yyyy-mm-dd',
    calendar_kwargs={'selectmode': 'day', 'year': 2026}
)
arrival_date.pack(anchor="w", padx=(20, 0), pady=(0, 0))

label_depart_date = ctk.CTkLabel(dates_frame, text="Check-Out date", font=("Arial", 12, "italic"))
label_depart_date.pack(anchor="w", padx=(20, 0), pady=(5, 0))

depart_date = DateEntry(
    dates_frame, width=17, background='#1F6AA5', foreground='white',
    headersbackground='#2B2B2B', headersforeground='white',
    showweeknumbers=False, date_pattern='yyyy-mm-dd',
    calendar_kwargs={'selectmode': 'day', 'year': 2026}
)

depart_date.pack(anchor="w", padx=(20, 0), pady=(0, 5))

# Cadre des options (Headless & Format)
options_frame = ctk.CTkFrame(date_options_frame, fg_color="transparent")
options_frame.grid(row=0, column=2, sticky="w", padx=(20, 0), pady=15)

switch_headless = ctk.CTkSwitch(options_frame, text="Mode Headless")
switch_headless.select()
switch_headless.pack(anchor="w", pady=0)

label_note = ctk.CTkLabel(
    options_frame,
    text="*Deselect the switch to see\nwhat's running in background.",
    font=("Arial", 9, "italic")
)
label_note.pack(anchor="w", pady=(5, 20))

label_format = ctk.CTkLabel(options_frame, text="Save format")
label_format.pack(anchor="w", pady=(0, 5))
menu_format = ctk.CTkOptionMenu(options_frame, values=["CSV", "JSON", "SQLite"])
menu_format.set("CSV")
menu_format.pack(anchor="w")

label_result2 = ctk.CTkLabel(app, text="")
label_result2.pack(anchor="w", padx=30, pady=10)


# Composant NumberStepper
class NumberStepper(ctk.CTkFrame):
    """A custom CustomTkinter component representing a numeric stepper widget 
    with decrement (-) and increment (+) buttons to control quantity values.
    """
    def __init__(self, frame_name, min_value=0, max_value=10, initial_value=0, validate_increase=None, **kwargs):
        super().__init__(frame_name, fg_color="transparent", **kwargs)
        self.value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.validate_increase = validate_increase

        self.btn_minus = ctk.CTkButton(
            self, text="-", width=25, height=25, 
            fg_color="#333333", hover_color="#444444", command=self.decrease
        )
        self.btn_minus.grid(row=0, column=0, padx=5)

        self.label_value = ctk.CTkLabel(self, text=str(self.value), width=30, font=("Arial", 14, "bold"))
        self.label_value.grid(row=0, column=1, padx=5)

        self.btn_plus = ctk.CTkButton(
            self, text="+", width=25, height=25, 
            fg_color="#333333", hover_color="#444444", command=self.increase
        )
        self.btn_plus.grid(row=0, column=2, padx=5)

    def decrease(self):
        if self.value > self.min_value:
            self.value -= 1
            self.label_value.configure(text=str(self.value))

    def increase(self):
        if self.value < self.max_value:
            if self.validate_increase is None or self.validate_increase():
                self.value += 1
                self.label_value.configure(text=str(self.value))

    def get(self) -> int:
        return self.value

travelers_frame = ctk.CTkFrame(date_options_frame, fg_color="transparent")
travelers_frame.grid(row=0, column=1, sticky="w", padx=(20, 0), pady=15)

label_adults = ctk.CTkLabel(travelers_frame, text="Adults", font=("Arial", 11, "bold"))
label_adults.pack(anchor="w", pady=(0, 2))
stepper_adults = NumberStepper(travelers_frame, min_value=1, max_value=16, initial_value=1)
stepper_adults.pack(anchor="w", pady=(0, 8))


label_kids = ctk.CTkLabel(travelers_frame, text="Children", font=("Arial", 11, "bold"))
label_kids.pack(anchor="w", pady=(0, 2))
stepper_kids = NumberStepper(travelers_frame, min_value=0, max_value=15, initial_value=0)
stepper_kids.pack(anchor="w", pady=(0, 8))


def check_total_guests():
    return (stepper_adults.get() + stepper_kids.get()) < 16

stepper_adults.validate_increase = check_total_guests
stepper_kids.validate_increase = check_total_guests


label_pets = ctk.CTkLabel(travelers_frame, text="Pets", font=("Arial", 11, "bold"))
label_pets.pack(anchor="w", pady=(0, 2))
stepper_pets = NumberStepper(travelers_frame, min_value=0, max_value=5, initial_value=0)
stepper_pets.pack(anchor="w")




start_button = ctk.CTkButton(
    app, text="Start Scraping", 
    command=lambda: start_primary_thread(
        app, entry_city, arrival_date, depart_date, switch_headless, 
        menu_format, stepper_adults, stepper_kids, stepper_pets, 
        label_result1, label_result2, label_timer, textbox, start_button
    ), 
    fg_color="green", hover_color="darkgreen"
)
start_button.pack(pady=10)


label_timer = ctk.CTkLabel(app, text="", font=("Arial", 12, "italic"))
label_timer.pack(pady=2)

textbox = ctk.CTkTextbox(app, width=500, height=200)
textbox.pack(pady=5)

label_note_explicative = ctk.CTkLabel(
    app,
    text="💡 Note: Average prices and selected listings may slightly vary\n"
         "between searches due to Airbnb's dynamic algorithm sampling\n"
         "on the initial pages.",
    font=("Arial", 10, "italic"),
    text_color="#3B82F6"
)
label_note_explicative.pack(pady=(5, 10))

if __name__ == "__main__":
    app.mainloop()