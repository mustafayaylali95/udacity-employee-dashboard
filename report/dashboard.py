# pylint: disable=C0114, C0115, C0116, C0103
from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events.employee import Employee
from employee_events.team import Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):

    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, entity_id, model):
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name.title()

        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model)

    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(self, entity_id, model):
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        return model.names()


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(self, entity_id, model):

        # Using the model argument for this method
        # return a fasthtml H1 objects
        # containing the model's name attribute
        return H1(f"{model.name.title()} Dashboard")


# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):

    # Overwrite the parent class's `visualization`
    # method. Use the same parameters as the parent
    def visualization(self, asset_id, model):

        # Pass the `asset_id` argument to
        # the model's `event_counts` method
        df = model.event_counts(asset_id)

        # Initialize a pandas subplot
        fig, ax = plt.subplots()

        # EĞER TABLO BOŞ DEĞİLSE İŞLEMLERE DEVAM ET (GÜVENLİK AĞI)
        if not df.empty:
            df = df.fillna(0)
            df = df.set_index('event_date')
            df = df.sort_index()
            df = df.cumsum()
            df.columns = ['Positive', 'Negative']
            df.plot(ax=ax)
        else:
            # EĞER TABLO BOŞSA, EKRANA MESAJ YAZDIR VE ÇÖKMESİNİ ENGELLE
            ax.text(0.5, 0.5, "No data available for this selection",
                    horizontalalignment='center', verticalalignment='center', fontsize=12)

        # pass the axis variable to the `.set_axis_styling` method
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        # Set title and labels for x and y axis
        ax.set_title("Cumulative Event Counts")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Count")


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):

    # Create a `predictor` class attribute
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    def visualization(self, asset_id, model):

        # Pass the `asset_id` to the `.model_data` method
        df = model.model_data(asset_id)

        # Initialize a matplotlib subplot
        fig, ax = plt.subplots()

        # EĞER TABLO BOŞ DEĞİLSE TAHMİN YAP (GÜVENLİK AĞI)
        if not df.empty:
            pred_proba = self.predictor.predict_proba(df)
            risk_scores = pred_proba[:, 1]

            if model.name == 'team':
                pred = risk_scores.mean()
            else:
                pred = risk_scores[0]

            ax.barh([''], [pred])
            ax.set_xlim(0, 1)
        else:
            # EĞER TABLO BOŞSA MODELİ ÇALIŞTIRMA, EKRANA MESAJ YAZDIR
            ax.barh([''], [0])
            ax.set_xlim(0, 1)
            ax.text(0.5, 0, "No data available",
                    horizontalalignment='center', verticalalignment='center', fontsize=12)

        ax.set_title('Predicted Recruitment Risk', fontsize=20)
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
# Create a subclass of combined_components/CombinedComponent
# called Visualizations


class Visualizations(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    children = [LineChart(), BarChart()]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')

# Create a subclass of base_components/DataTable
# called `NotesTable`


class NotesTable(DataTable):

    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(self, entity_id, model):

        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes
        # method. Return the output
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection")
    ]

# Create a subclass of CombinedComponents
# called `Report`


class Report(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing initialized instances
    # of the header, dashboard filters,
    # data visualizations, and notes table
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]


# Initialize a fasthtml app
app, rt = fast_app()

# Initialize the `Report` class
report_instance = Report()

# Create a route for a get request
# Set the route's path to the root


@app.get('/')
def index():
    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return report_instance(1, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`.
# parameterize the employee ID
# to a string datatype


@app.get('/employee/{id}')
def get_employee(id: str):
    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return report_instance(id, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`.
# parameterize the team ID
# to a string datatype


@app.get('/team/{id}')
def get_team(id: str):
    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    return report_instance(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
