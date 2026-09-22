from __future__ import annotations # Allows newer, more flexible behaviour for type annotations.
import tkinter as tk # Imports Tkinter and gives it the shorter name "tk".

from datetime import datetime # Imports datetime so the program can work with times and dates.
from pathlib import Path # Imports Path to easily work with file paths.

from tkinter import filedialog, messagebox, ttk # Imports file dialogs, pop-up messages, and themed Tkinter widgets.

# Allows a Matplotlib chart to be displayed inside a Tkinter window.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure # Imports Matplotlib's Figure object for creating charts.

# Imports the functions that perform the tariff calculations and data processing.
from tariff_functions import (
    calculate_flat_rate_breakdown,
    calculate_tiered_breakdown,
    calculate_tou_tariff,
    compare_tariffs,
    filter_usage_records,
    generate_saving_suggestions,
    load_usage_records,
)

class XPowerApp(tk.Tk): # Creates the main application class and makes it a Tkinter window.
    """Desktop prototype allowing non-technical users to run tariff analysis."""

    def __init__(self): # Defines what happens when the application is created.
        """Create the main application window and initialise application data."""

        super().__init__() # Sets up the Tkinter window inherited from tk.Tk.

        self.title("XPower Household Tariff Analysis") # Sets the title shown at the top of the window.

        self.geometry("1160x760") # Sets the starting window size to 1160 by 760 pixels.
        self.minsize(1000, 680) # Prevents the user from making the window smaller than 1000 by 680 pixels.

        self.records = [] # Creates an empty list to store all imported electricity records.
        self.selected_records = [] # Creates an empty list to store records selected for analysis.
        self.results = {} # Creates an empty dictionary to store calculation results.

        self._configure_style() # Calls the function that sets the application's visual style.
        self._build_interface() # Calls the function that creates the application's widgets.


    def _configure_style(self): # Defines a function for configuring the Tkinter appearance.
        """Configure the visual styling used throughout the application."""

        style = ttk.Style(self) # Creates a ttk Style object for changing widget appearance.

        # The Clam theme is a built-in Tkinter/ttk visual style that changes how widgets look.
        if "clam" in style.theme_names(): # Checks whether the Clam visual theme is available.
            style.theme_use("clam") # Changes the application to use the Clam theme.

        style.configure( # Creates a custom style for the application's main title.
            "Title.TLabel", # Gives the custom label style a name.
            font=("Segoe UI", 20, "bold"), # Sets the title font, size, and boldness.
            foreground="#17365d", # Sets the title text colour.
        )
        style.configure( # Creates a custom style for section headings.
            "Section.TLabelframe.Label", # Targets the label used on labelled frames.
            font=("Segoe UI", 11, "bold"), # Sets the section heading font, size, and boldness.
            foreground="#17365d", # Sets the section heading text colour.
        )
        style.configure( # Creates a custom style for the main analysis button.
            "Accent.TButton", # Gives the button style a name.
            font=("Segoe UI", 10, "bold"), # Sets the button font, size, and boldness.
        )


    def _build_interface(self): # Defines a function for creating the main window layout.
        """Create the main application layout and connect the interface sections."""

        ttk.Label( # Creates and places the main title label.
            self, # Places the label inside the main application window.
            text="XPower Household Tariff Analysis", # Sets the text displayed by the label.
            style="Title.TLabel", # Applies the custom title style to the label.
        ).pack(
            anchor="w", # Aligns the label to the left side of its space.
            padx=20, # Adds 20 pixels of horizontal outside space.
            pady=(16, 4), # Adds 16 pixels above and 4 pixels below the label.
        )
        ttk.Label( # Creates and places a short instruction label.
            self, # Places the label inside the main application window.
            text=("Upload usage data, select a period, configure tariffs, and compare estimated bills."), # Sets the instruction text.
        ).pack(
            anchor="w", # Aligns the instruction text to the left.
            padx=20, # Adds 20 pixels of horizontal outside space.
            pady=(0, 12), # Adds no space above and 12 pixels below the label.
        )
        body = ttk.Panedwindow( # Creates a container with two horizontally arranged, resizable sections.
            self, # Places the Panedwindow inside the main application window.
            orient=tk.HORIZONTAL, # Arranges the sections from left to right.
        )
        body.pack( # Places the Panedwindow and allows it to expand with the window.
            fill=tk.BOTH, # Makes the Panedwindow fill both available directions.
            expand=True, # Allows the Panedwindow to use extra available space.
            padx=16, # Adds 16 pixels of horizontal outside space.
            pady=(0, 16), # Adds no space above and 16 pixels below.
        )

        controls = ttk.Frame(body, padding=4) # Creates a frame to hold the input controls.
        output = ttk.Frame(body, padding=4) # Creates a frame to hold the results and charts.
        body.add(controls, weight=2) # Adds the controls frame and gives it a smaller share of the space.
        body.add(output, weight=3) # Adds the output frame and gives it a larger share of the space.

        self._build_controls(controls) # Builds the controls inside the controls frame.
        self._build_output(output) # Builds the output area inside the output frame.


    def _build_controls(self, parent): # Defines a function for creating the input controls.
        """Build the data-import, date-selection, and tariff configuration controls."""

        data = ttk.LabelFrame( # Creates a labelled box containing the usage-data controls.
            parent, # Places the labelled frame inside the given parent frame.
            text="1  Usage Data", # Sets the title shown on the labelled frame.
            style="Section.TLabelframe", # Applies the custom section heading style.
            padding=10, # Adds 10 pixels of internal space around the contents.
        )
        data.pack( # Places the usage-data section and stretches it horizontally.
            fill=tk.X, # Makes the section stretch across the available width.
            pady=(0, 10), # Adds no space above and 10 pixels below the section.
        )
        ttk.Button( # Creates an upload button and runs load_file when clicked.
            data, # Places the button inside the usage-data section.
            text="Upload CSV or Excel", # Sets the text displayed on the button.
            command=self.load_file, # Calls load_file when the button is clicked.
        ).grid(
            row=0, # Places the button in the first grid row.
            column=0, # Places the button in the first grid column.
            sticky="w", # Aligns the button to the left of its grid cell.
        )

        self.file_label = ttk.Label( # Creates a label that will show the selected file information.
            data, # Places the label inside the usage-data section.
            text="No file selected", # Sets the starting text shown by the label.
            wraplength=390, # Wraps the label text when it reaches about 390 pixels.
        )
        self.file_label.grid( # Places the file-information label beside the upload button.
            row=0, # Places the label in the first grid row.
            column=1, # Places the label in the second grid column.
            sticky="w", # Aligns the label to the left of its grid cell.
            padx=10, # Adds 10 pixels of horizontal space around the label.
        )

        ttk.Label( # Creates and places the start-date label.
            data, # Places the label inside the usage-data section.
            text="Start date (YYYY-MM-DD)", # Sets the text describing the start-date field.
        ).grid(
            row=1, # Places the label in the second grid row.
            column=0, # Places the label in the first grid column.
            sticky="w", # Aligns the label to the left of its grid cell.
            pady=(10, 2), # Adds 10 pixels above and 2 pixels below the label.
        )
        ttk.Label( # Creates and places the end-date label.
            data, # Places the label inside the usage-data section.
            text="End date (YYYY-MM-DD)", # Sets the text describing the end-date field.
        ).grid(
            row=2, # Places the label in the third grid row.
            column=0, # Places the label in the first grid column.
            sticky="w", # Aligns the label to the left of its grid cell.
            pady=2, # Adds 2 pixels of vertical space around the label.
        )

        self.start_date = tk.StringVar() # Creates a Tkinter variable for storing the start date.
        self.end_date = tk.StringVar() # Creates a Tkinter variable for storing the end date.

        ttk.Entry( # Creates an input box connected to the start-date variable.
            data, # Places the input box inside the usage-data section.
            textvariable=self.start_date, # Connects the input box to the start-date StringVar.
            width=18, # Sets the approximate width of the input box.
        ).grid(
            row=1, # Places the input box in the second grid row.
            column=1, # Places the input box in the second grid column.
            sticky="w", # Aligns the input box to the left of its grid cell.
            pady=(10, 2), # Adds 10 pixels above and 2 pixels below the input box.
        )
        ttk.Entry( # Creates an input box connected to the end-date variable.
            data, # Places the input box inside the usage-data section.
            textvariable=self.end_date, # Connects the input box to the end-date StringVar.
            width=18, # Sets the approximate width of the input box.
        ).grid(
            row=2, # Places the input box in the third grid row.
            column=1, # Places the input box in the second grid column.
            sticky="w", # Aligns the input box to the left of its grid cell.
            pady=2, # Adds 2 pixels of vertical space around the input box.
        )
        rates = ttk.LabelFrame( # Creates a labelled section for tariff settings.
            parent, # Places the tariff section inside the given parent frame.
            text="2  Tariff Settings", # Sets the title shown on the tariff section.
            style="Section.TLabelframe", # Applies the custom section heading style.
            padding=10, # Adds 10 pixels of internal space around the contents.
        )
        rates.pack( # Places the tariff section and lets it expand.
            fill=tk.BOTH, # Makes the section fill both available directions.
            expand=True, # Allows the section to use extra available space.
            pady=(0, 10), # Adds no space above and 10 pixels below the section.
        )

        self.fields = {} # Creates a dictionary to store all tariff input variables.

        definitions = [ # Stores each tariff field's label, dictionary key, and default value.
            ("Fixed fee ($)", "fixed_fee", "10.00"),
            ("Flat rate ($/kWh)", "flat_rate", "0.25"),
            ("Peak rate ($/kWh)", "peak_rate", "0.40"),
            ("Off-peak rate ($/kWh)", "offpeak_rate", "0.15"),
            ("Shoulder rate ($/kWh)", "shoulder_rate", "0.25"),
            ("Peak start (HH:MM)", "peak_start", "18:00"),
            ("Peak end (HH:MM)", "peak_end", "22:00"),
            ("Off-peak start (HH:MM)", "offpeak_start", "22:00"),
            ("Off-peak end (HH:MM)", "offpeak_end", "07:00"),
            ("Tier 1 limit (kWh)", "tier1_limit", "100"),
            ("Tier 1 rate ($/kWh)", "tier1_rate", "0.20"),
            ("Tier 2 limit (kWh)", "tier2_limit", "300"),
            ("Tier 2 rate ($/kWh)", "tier2_rate", "0.30"),
            ("Tier 3 rate ($/kWh)", "tier3_rate", "0.40"),
        ]

        # Loops through every tariff setting and gets its position.
        for index, (label, key, default) in enumerate(definitions):

            row, column = divmod(index, 2) # Converts the field number into a two-column row and column position.
            frame = ttk.Frame(rates) # Creates a small frame to hold one tariff setting.

            frame.grid( # Places the tariff field frame into the two-column grid.
                row=row, # Sets which grid row contains this tariff field.
                column=column, # Sets which grid column contains this tariff field.
                sticky="ew", # Makes the frame stretch from left to right.
                padx=(0 if column == 0 else 8, 8), # Adds horizontal space around the frame.
                pady=3, # Adds 3 pixels of vertical space around the frame.
            )
            ttk.Label( # Creates and places the label for the tariff field.
                frame, # Places the label inside the small tariff frame.
                text=label, # Uses the current tariff label as the displayed text.
            ).pack(
                anchor="w" # Aligns the tariff label to the left.
            )

            variable = tk.StringVar(value=default) # Creates a Tkinter variable containing the default value.
            self.fields[key] = variable # Stores the variable in the fields dictionary.

            ttk.Entry( # Creates and places an input box connected to the variable.
                frame, # Places the input box inside the tariff frame.
                textvariable=variable, # Connects the input box to its StringVar.
                width=18, # Sets the approximate width of the input box.
            ).pack(
                anchor="w", # Aligns the input box to the left.
                fill=tk.X, # Makes the input box stretch horizontally.
            )

        rates.columnconfigure(0, weight=1) # Allows the first tariff column to expand.
        rates.columnconfigure(1, weight=1) # Allows the second tariff column to expand.

        ttk.Button( # Creates the main button that starts the tariff analysis.
            parent, # Places the button inside the parent controls area.
            text="Run Tariff Analysis", # Sets the text displayed on the button.
            style="Accent.TButton", # Applies the custom button style.
            command=self.run_analysis, # Calls run_analysis when the button is clicked.
        ).pack(
            fill=tk.X, # Makes the button stretch across the available width.
        )


    def _build_output(self, parent): # Defines a function for creating the results and chart area.
        """Build the results and chart tabs used to display the analysis."""

        notebook = ttk.Notebook(parent) # Creates a Tkinter tabbed interface.

        notebook.pack( # Places the tabbed interface and lets it fill the available space.
            fill=tk.BOTH, # Makes the notebook fill horizontally and vertically.
            expand=True, # Allows the notebook to use extra available space.
        )

        results_tab = ttk.Frame( # Creates the frame that will contain the bill results.
            notebook, # Places the results frame inside the notebook.
            padding=12, # Adds 12 pixels of internal space around the results.
        )
        charts_tab = ttk.Frame( # Creates the frame that will contain the charts.
            notebook, # Places the charts frame inside the notebook.
            padding=8, # Adds 8 pixels of internal space around the charts.
        )

        notebook.add( # Adds the results frame as a tab named Bill Results.
            results_tab, # Uses the results frame as the contents of this tab.
            text="Bill Results", # Sets the text displayed on the tab.
        )
        notebook.add( # Adds the charts frame as a tab named Charts.
            charts_tab, # Uses the charts frame as the contents of this tab.
            text="Charts", # Sets the text displayed on the tab.
        )

        self.results_text = tk.Text( # Creates a multi-line text box for displaying the results.
            results_tab, # Places the text box inside the results tab.
            wrap=tk.WORD, # Wraps long text at complete words.
            font=("Consolas", 10), # Sets the font and size used for the results.
            state=tk.DISABLED, # Makes the text box read-only for the user.
        )

        scrollbar = ttk.Scrollbar( # Creates a scrollbar connected to the results text box.
            results_tab, # Places the scrollbar inside the results tab.
            command=self.results_text.yview, # Makes the scrollbar control the text box's vertical position.
        )

        self.results_text.configure( # Makes the text box update the scrollbar position.
            yscrollcommand=scrollbar.set, # Tells the text box to update the scrollbar as it moves.
        )
        self.results_text.pack( # Places the results text box on the left and lets it expand.
            side=tk.LEFT, # Places the text box on the left side of the available space.
            fill=tk.BOTH, # Makes the text box fill horizontally and vertically.
            expand=True, # Allows the text box to use extra available space.
        )
        scrollbar.pack( # Places the scrollbar on the right side of the results box.
            side=tk.RIGHT, # Places the scrollbar on the right side.
            fill=tk.Y, # Makes the scrollbar stretch vertically.
        )
        self.figure = Figure( # Creates a Matplotlib figure that will contain the charts.
            figsize=(7, 6), # Sets the figure width and height in inches.
            dpi=100, # Sets the figure resolution to 100 dots per inch.
        )
        self.canvas = FigureCanvasTkAgg( # Connects the Matplotlib figure to the Tkinter Charts tab.
            self.figure, # Gives the canvas the Matplotlib figure to display.
            master=charts_tab, # Places the Matplotlib canvas inside the Charts tab.
        )
        self.canvas.get_tk_widget().pack( # Gets the Tkinter chart widget and makes it fill the chart tab.
            fill=tk.BOTH, # Makes the chart fill horizontally and vertically.
            expand=True, # Allows the chart to use extra available space.
        )


    def load_file(self): # Defines the function that loads the user's electricity file.
        """Open a usage file, validate it, and populate the analysis period."""

        path = filedialog.askopenfilename( # Opens Tkinter's file-selection window.
            title="Select electricity usage data", # Sets the title of the file-selection window.
            filetypes=[ # Controls which file types can be selected.
                ("Usage data", "*.csv *.xlsx"), # Allows CSV and Excel files.
                ("CSV", "*.csv"), # Adds CSV as a selectable file type.
                ("Excel", "*.xlsx"), # Adds Excel as a selectable file type.
            ],
        )

        if not path: # Checks whether the user cancelled the file-selection window.
            return # Stops the function if no file was selected.

        try: # Starts a block that can catch errors while loading the file.
            self.records = load_usage_records(path) # Loads and validates the selected usage records.

        except Exception as exc: # Catches any error that occurs while importing the file.
            messagebox.showerror( # Opens a Tkinter error pop-up.
                "Unable to import file", # Sets the error pop-up title.
                str(exc), # Displays the error message.
            )
            return # Stops the function after showing the error.

        self.file_label.configure( # Updates the existing file-name label.
            text=f"{Path(path).name} - {len(self.records)} records" # Shows the file name and number of records.
        )

        dates = [ # Creates a list containing the dates from all records.
            record["timestamp"].date() # Gets only the date from each timestamp.
            for record in self.records # Repeats this for every imported record.
        ]

        self.start_date.set( # Updates the start-date input field.
            min(dates).isoformat() # Sets it to the earliest date in the dataset.
        )

        self.end_date.set( # Updates the end-date input field.
            max(dates).isoformat() # Sets it to the latest date in the dataset.
        )

        messagebox.showinfo( # Opens a Tkinter information pop-up.
            "Import successful", # Sets the information pop-up title.
            f"Loaded {len(self.records)} validated usage records.", # Displays the import success message.
        )


    @staticmethod # Makes this method usable without needing a class instance.
    def _parse_time(value): # Defines a function for converting text into a time.
        """Convert a user-entered HH:MM value into a datetime.time object."""

        try: # Starts a block that can catch invalid time input.
            return datetime.strptime( # Converts the entered text into a datetime object.
                value.strip(), # Removes unnecessary spaces from the entered time.
                "%H:%M", # Tells Python to expect 24-hour hour-and-minute format.
            ).time() # Extracts only the time portion from the datetime object.

        except ValueError as exc: # Catches the error caused by an invalid time format.
            raise ValueError( # Creates a clearer error message for the user.
                "TOU times must use 24-hour HH:MM format." # Explains the required time format.
            ) from exc # Keeps the original error as the cause.


    def _value(self, key): # Defines a function for getting a numeric tariff value.
        """Convert a numeric tariff setting from the interface into a float."""

        try: # Starts a block that can catch invalid number input.
            return float( # Converts the entered text into a decimal number.
                self.fields[key].get() # Gets the current value from the selected Tkinter variable.
            )

        except ValueError as exc: # Catches the error caused by non-numeric input.
            raise ValueError( # Creates a clearer error message for the user.
                f"{key.replace('_', ' ').title()} must be a number." # Names the setting that must contain a number.
            ) from exc # Keeps the original error as the cause.


    def run_analysis(self): # Defines the function that performs the tariff analysis.
        """Validate the selected data, calculate all tariffs, and update the interface."""

        if not self.records: # Checks whether any usage records have been loaded.
            messagebox.showwarning( # Opens a Tkinter warning pop-up.
                "Usage data required", # Sets the warning pop-up title.
                "Upload a CSV or Excel usage file first.", # Tells the user what they need to do.
            )
            return # Stops the analysis because there is no data.

        try: # Starts a block that can catch errors during analysis.
            selected = filter_usage_records( # Filters the records using the selected dates.
                self.records, # Provides all imported records.
                self.start_date.get(), # Gets the selected start date.
                self.end_date.get(), # Gets the selected end date.
            )

            total = sum( # Adds together the electricity usage values.
                record["kWh"] # Gets the kWh value from each record.
                for record in selected # Repeats the calculation for every selected record.
            )

            fee = self._value("fixed_fee") # Gets the fixed tariff fee entered by the user.

            flat = calculate_flat_rate_breakdown( # Calculates the flat-rate bill.
                total, # Provides the total electricity usage.
                self._value("flat_rate"), # Gets the flat electricity rate.
                fee, # Provides the fixed fee.
            )

            tou = calculate_tou_tariff( # Calculates the time-of-use bill.
                selected, # Provides the selected electricity records.
                self._value("peak_rate"), # Gets the peak electricity rate.
                self._value("offpeak_rate"), # Gets the off-peak electricity rate.
                self._value("shoulder_rate"), # Gets the shoulder electricity rate.
                fee, # Provides the fixed fee.
                self._parse_time( # Converts the peak-start text into a time.
                    self.fields["peak_start"].get() # Gets the entered peak-start time.
                ),
                self._parse_time( # Converts the peak-end text into a time.
                    self.fields["peak_end"].get() # Gets the entered peak-end time.
                ),
                self._parse_time( # Converts the off-peak-start text into a time.
                    self.fields["offpeak_start"].get() # Gets the entered off-peak-start time.
                ),
                self._parse_time( # Converts the off-peak-end text into a time.
                    self.fields["offpeak_end"].get() # Gets the entered off-peak-end time.
                ),
            )

            tiered = calculate_tiered_breakdown( # Calculates the tiered tariff bill.
                total, # Provides the total electricity usage.
                self._value("tier1_limit"), # Gets the usage limit for tier 1.
                self._value("tier1_rate"), # Gets the electricity rate for tier 1.
                self._value("tier2_limit"), # Gets the usage limit for tier 2.
                self._value("tier2_rate"), # Gets the electricity rate for tier 2.
                self._value("tier3_rate"), # Gets the electricity rate for tier 3.
                fee, # Provides the fixed fee.
            )

            comparison = compare_tariffs( # Compares the total costs of the tariff options.
                {
                    "Flat Rate": flat["total"], # Stores the flat-rate total bill.
                    "Time-of-Use": tou["total"], # Stores the time-of-use total bill.
                    "Tiered": tiered["total"], # Stores the tiered total bill.
                }
            )

            suggestions = generate_saving_suggestions( # Creates suggestions based on the analysis.
                selected, # Provides the selected electricity records.
                tou, # Provides the time-of-use results.
                comparison, # Provides the tariff comparison results.
            )

        except Exception as exc: # Catches any error that occurs during analysis.
            messagebox.showerror( # Shows a Tkinter error pop-up if analysis fails.
                "Analysis could not run", # Sets the error pop-up title.
                str(exc), # Displays the error message.
            )
            return # Stops the function after showing the error.

        self.selected_records = selected # Stores the records used in the latest analysis.

        self.results = { # Creates a dictionary containing all calculated results.
            "flat": flat, # Stores the flat-rate results.
            "tou": tou, # Stores the time-of-use results.
            "tiered": tiered, # Stores the tiered results.
            "comparison": comparison, # Stores the tariff comparison results.
        }

        self._show_results( # Displays the calculated results in the results area.
            total, # Passes the total electricity usage.
            flat, # Passes the flat-rate results.
            tou, # Passes the time-of-use results.
            tiered, # Passes the tiered results.
            comparison, # Passes the tariff comparison.
            suggestions, # Passes the saving suggestions.
        )

        self._draw_charts( # Draws the charts using the latest analysis.
            selected, # Passes the selected electricity records.
            flat, # Passes the flat-rate results.
            tou, # Passes the time-of-use results.
            tiered, # Passes the tiered results.
        )


    def _show_results( # Defines a function for displaying the analysis results.
        self, # Passes the current XPowerApp object.
        total, # Receives the total electricity usage.
        flat, # Receives the flat-rate results.
        tou, # Receives the time-of-use results.
        tiered, # Receives the tiered results.
        comparison, # Receives the tariff comparison.
        suggestions, # Receives the saving suggestions.
    ):
        """Format and display the calculated tariff results in the results tab."""

        lines = [ # Creates a list of text lines that will be displayed.
            f"SELECTED USAGE: {total:.2f} kWh", # Displays the total electricity usage.
            "", # Adds a blank line.
            "FLAT RATE", # Adds the flat-rate section heading.
            f"Energy fee: ${flat['energy_fee']:.2f}", # Displays the flat-rate energy fee.
            f"Fixed fee:  ${flat['fixed_fee']:.2f}", # Displays the flat-rate fixed fee.
            f"Total:      ${flat['total']:.2f}", # Displays the flat-rate total cost.
            "", # Adds a blank line.
            "TIME-OF-USE", # Adds the time-of-use section heading.
        ]

        for key in ( # Loops through each time-of-use period.
            "peak", # Selects the peak period.
            "off_peak", # Selects the off-peak period.
            "shoulder", # Selects the shoulder period.
        ):
            item = tou[key] # Gets the results for the current time-of-use period.

            lines.append( # Adds the current period's information to the output.
                f"{key.replace('_', ' ').title():10} " # Formats the period name.
                f"{item['usage_kwh']:8.2f} kWh x " # Formats the electricity usage.
                f"${item['rate']:.2f} = " # Formats the electricity rate.
                f"${item['cost']:.2f}" # Formats the calculated cost.
            )

        lines.extend([ # Adds more time-of-use results to the output.
            f"Energy fee: ${tou['energy_fee']:.2f}", # Displays the TOU energy fee.
            f"Fixed fee:  ${tou['fixed_fee']:.2f}", # Displays the TOU fixed fee.
            f"Total:      ${tou['total']:.2f}", # Displays the TOU total cost.
            "", # Adds a blank line.
            "TIERED", # Adds the tiered tariff section heading.
        ])

        for key in ( # Loops through each electricity usage tier.
            "tier1", # Selects tier 1.
            "tier2", # Selects tier 2.
            "tier3", # Selects tier 3.
        ):
            item = tiered[key] # Gets the results for the current tier.

            lines.append( # Adds the current tier's information to the output.
                f"{key.title():10} " # Formats the tier name.
                f"{item['usage_kwh']:8.2f} kWh x " # Formats the tier electricity usage.
                f"${item['rate']:.2f} = " # Formats the tier electricity rate.
                f"${item['cost']:.2f}" # Formats the tier cost.
            )

        lines.extend([ # Adds more tiered tariff results to the output.
            f"Energy fee: ${tiered['energy_fee']:.2f}", # Displays the tiered energy fee.
            f"Fixed fee:  ${tiered['fixed_fee']:.2f}", # Displays the tiered fixed fee.
            f"Total:      ${tiered['total']:.2f}", # Displays the tiered total cost.
            "", # Adds a blank line.
            "COMPARISON", # Adds the comparison section heading.
        ])

        for name, value in comparison["bills"].items(): # Loops through each tariff's calculated bill.
            lines.append( # Adds the current tariff's bill and savings to the output.
                f"{name:14} " # Formats the tariff name.
                f"${value:.2f}   " # Formats the tariff's total bill.
                f"savings vs this option: " # Adds the savings description.
                f"${comparison['savings'][name]:.2f}" # Displays the calculated savings.
            )

        lines.extend([ # Adds the suggestions section to the output.
            "", # Adds a blank line.
            "COST-SAVING SUGGESTIONS", # Adds the suggestions heading.
        ])

        lines.extend( # Adds every suggestion to the output list.
            f"- {item}" # Adds a dash before each suggestion.
            for item in suggestions # Repeats this for every suggestion.
        )

        self.results_text.configure( # Changes the text widget's settings.
            state=tk.NORMAL # Temporarily allows the program to edit the text.
        )

        self.results_text.delete( # Deletes the existing text from the widget.
            "1.0", # Starts at line 1, character 0.
            tk.END, # Ends at the end of the text.
        )

        self.results_text.insert( # Adds the new results to the text widget.
            tk.END, # Inserts the text at the end.
            "\n".join(lines), # Combines all output lines into one string.
        )

        self.results_text.configure( # Changes the text widget back to read-only.
            state=tk.DISABLED # Prevents the user from editing the results.
        )


    def _draw_charts( # Defines a function for creating the Matplotlib charts.
        self, # Passes the current XPowerApp object.
        records, # Receives the electricity records to plot.
        flat, # Receives the flat-rate results.
        tou, # Receives the time-of-use results.
        tiered, # Receives the tiered results.
    ):
        """Draw the electricity usage trend and tariff cost comparison charts."""

        self.figure.clear() # Removes all existing Matplotlib plots from the figure.

        # =========================================================
        # ELECTRICITY USAGE TREND
        # =========================================================

        usage_ax = self.figure.add_subplot(211) # Creates the first chart using a 2-row, 1-column layout.

        usage_ax.plot( # Draws a line chart showing electricity usage over time.
            [record["timestamp"] for record in records], # Uses each record's timestamp for the horizontal axis.
            [record["kWh"] for record in records], # Uses each record's kWh value for the vertical axis.
            linewidth=1, # Sets the thickness of the plotted line.
            color="#2f75b5", # Sets the colour of the plotted line.
        )

        usage_ax.set_title( # Sets the title displayed above the usage chart.
            "Electricity Usage Trend" # Provides the chart title text.
        )

        usage_ax.set_ylabel( # Sets the label displayed beside the vertical axis.
            "kWh" # Names the vertical axis as electricity usage.
        )

        usage_ax.grid( # Adds grid lines to the usage chart.
            alpha=0.25 # Makes the grid lines 25% opaque.
        )

        # =========================================================
        # BILL BREAKDOWN COMPARISON
        # =========================================================

        bill_ax = self.figure.add_subplot(212) # Creates the second chart below the first chart.

        names = [ # Creates the labels for the three tariff bars.
            "Flat Rate", # Names the flat-rate tariff.
            "Time-of-Use", # Names the time-of-use tariff.
            "Tiered", # Names the tiered tariff.
        ]

        energy = [ # Creates a list containing each tariff's energy cost.
            flat["energy_fee"], # Gets the flat-rate energy fee.
            tou["energy_fee"], # Gets the TOU energy fee.
            tiered["energy_fee"], # Gets the tiered energy fee.
        ]

        fixed = [ # Creates a list containing each tariff's fixed cost.
            flat["fixed_fee"], # Gets the flat-rate fixed fee.
            tou["fixed_fee"], # Gets the TOU fixed fee.
            tiered["fixed_fee"], # Gets the tiered fixed fee.
        ]

        bill_ax.bar( # Draws the energy-fee bars for each tariff.
            names, # Uses the tariff names as the horizontal bar labels.
            energy, # Uses the energy fees as the bar heights.
            label="Energy fee", # Gives the energy section a name for the legend.
            color="#2f75b5", # Sets the energy bar colour.
        )

        bill_ax.bar( # Draws the fixed-fee bars on top of the energy bars.
            names, # Uses the tariff names as the horizontal bar labels.
            fixed, # Uses the fixed fees as the bar heights.
            bottom=energy, # Starts each fixed-fee bar at the top of its energy bar.
            label="Fixed fee", # Gives the fixed section a name for the legend.
            color="#a5a5a5", # Sets the fixed-fee bar colour.
        )

        bill_ax.set_title( # Sets the title displayed above the bill chart.
            "Bill Breakdown and Comparison" # Provides the chart title text.
        )

        bill_ax.set_ylabel( # Sets the label displayed beside the vertical axis.
            "Cost ($)" # Names the vertical axis as cost in dollars.
        )

        bill_ax.legend() # Displays the labels for the different bar sections.

        self.figure.tight_layout() # Automatically adjusts the spacing between the charts.

        self.canvas.draw_idle() # Refreshes the Tkinter display with the updated Matplotlib figure.


if __name__ == "__main__": # Checks whether this Python file is being run directly.
    XPowerApp().mainloop() # Creates the Tkinter app and keeps its window running.