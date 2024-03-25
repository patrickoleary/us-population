
from trame.app import get_server
from trame.decorators import TrameApp, change, controller
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import html, markdown, matplotlib, plotly, trame, vega, vuetify3

import altair as alt
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas
import plotly.express as px
import numpy as np

about_content = """## About\n\
 - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).\n\
 - <span style="color:orange">**Components**</span>: Decade population change and the natural and migration additions and subtractions.\n\
 - <span style="color:orange">**Years**</span>: Individual years in the decade that spans 2010 to 2019.\n\
 - <span style="color:orange">**Gains/Losses**</span>: states with high and low annual population growth for selected year.\n\
 - <span style="color:orange">**States Growth**</span>: percentage of states with above 50K and below -50K annual population growth.\n"""
component_or_year = ["Change", "Natural", "Births", "Deaths", "Migration", "International", "Domestic",
                     "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"]
components_2010 = ["Change", "Natural", "Births", "Deaths", "Migration", "International", "Domestic", "2010"]
years = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"]
color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
table_headers = [
    { 'title': 'State', 'key': 'state', 'sortable': False },
    { 'title': 'Population', 'key': 'population', 'sortable': False }
    ]
population_labels = ['313M', '315M', '317M', '319M', '321M', '324M', '326M', '328M', '329M', '331M']
top5 = [
    { 'state': 'Alabama', 'population':  10, 'rank': 1},
    { 'state': 'Alaska', 'population': 9, 'rank': 2 },
    { 'state': 'Arizona', 'population': 8, 'rank': 3 },
    { 'state': 'Arkansas', 'population': 7, 'rank': 4 },
    { 'state': 'California', 'population': 6, 'rank': 5 }
]
bottom5 = [
    { 'state': 'Washington', 'population':  5, 'rank': 1},
    { 'state': 'West Virginia', 'population': 4, 'rank': 2 },
    { 'state': 'Wisconsin', 'population': 3, 'rank': 3 },
    { 'state': 'Wyoming', 'population': 2, 'rank': 4 },
    { 'state': 'Puerto Rico', 'population': 1, 'rank': 5 }
]

# ---------------------------------------------------------
# Engine class
# ---------------------------------------------------------

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation year-over-year population migrations
def calculate_population_difference(input_df, input_year):
    if (input_year in components_2010):
        return None
    else:
        selected_df = input_df[input_df['year'] == input_year].reset_index()
        previous_df = input_df[input_df['year'] == str(int(input_year) - 1)].reset_index()
        selected_df['difference'] = selected_df.population.sub(previous_df.population, 
                                                               fill_value=0)
        return pandas.concat([selected_df.states, 
                              selected_df.id, 
                              selected_df.population, 
                              selected_df.difference], 
                              axis=1).sort_values(by="difference", 
                                                  ascending=False)

# Gains
def make_gains(input_df, input_year):
    if (input_year in components_2010):
        name = 'N/A'
        population = '0 M'
        delta = '0 K'
        gains_md = ""+name+"  \n<span style='font-size:2.0em;'>"+population+"</span>  \n<span style='color:black'>&harr;"+delta+"</span>"
        return gains_md
    else:
        name = input_df.states.iloc[0]
        population = format_number(input_df.population.iloc[0])
        delta = format_number(input_df.difference.iloc[0])
        if delta[0] != '-':
            gains_md = ""+name+"  \n<span style='font-size:2.0em;'>"+population+"</span>  \n<span style='color:green'>&uarr;"+delta+"</span>"
        else:
            gains_md = ""+name+"  \n<span style='font-size:2.0em;'>"+population+"</span>  \n<span style='color:red'>&darr;"+delta+"</span>"
        return gains_md

# Gains
def make_losses(input_df, input_year):
    if (input_year in components_2010):
        name = 'N/A'
        population = '0 M'
        delta = '0 K'
        losses_md = ""+name+"  \n<span style='font-size:2.0em;'>"+population+"</span>  \n<span style='color:black'>&harr;"+delta+"</span>"
        return losses_md
    else:
        name = input_df.states.iloc[-1]
        population = format_number(input_df.population.iloc[-1])
        delta = format_number(input_df.difference.iloc[-1])
        if delta[0] != '-':
            losses_md = ""+name+"  \n<span style='font-size:2.0em;'>"+population+"</span>  \n<span style='color:green'>&uarr;"+delta+"</span>"
        else:
            losses_md = ""+name+"  \n<span style='font-size:2.0em;'>"+population+"</span>  \n<span style='color:red'>&darr;"+delta+"</span>"
        return losses_md

# Donut chart
def make_donut(input_value, input_text, option):
  if option == "above":
      chart_color = ['#27AE60', '#12783D']
  else:
      chart_color = ['#E74C3C', '#781F16']
    
  source = pandas.DataFrame({ "Topic": ['', input_text], "% value": [100-input_value, input_value]})
  source_bg = pandas.DataFrame({"Topic": ['', input_text], "% value": [100, 0]})
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
            theta="% value",
            color= alt.Color("Topic:N",scale=alt.Scale(domain=[input_text, ''],
                                                       range=chart_color),
                                                       legend=None),
         ).properties(width=130, height=130)
  text = plot.mark_text(align='center', color=chart_color[0], font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_value} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
                theta="% value",
                color= alt.Color("Topic:N",scale=alt.Scale(domain=[input_text, ''],
                                                           range=chart_color),
                                                           legend=None),
            ).properties(width=130, height=130)
  return plot_bg + plot + text

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, 
                            locationmode="USA-states", color_continuous_scale=input_color_theme,
                            range_color=(min(input_df.population), max(input_df.population)),
                            scope="usa", labels={'population':''}
                        )
    choropleth.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme, width, height, **kwargs):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(
            width=int(width-60),
            height=int(height-130)
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        )
    return heatmap
    
# Line
def make_line(input_years, input_population, width, height, dpi, pixelRatio, **kwargs):
    w = (width - 10)/dpi
    h = (height - 5)/dpi
    plt.figure(figsize=(w,h),layout="compressed")
    plt.plot(np.asarray(input_years, int), np.asarray(input_population, int))
    fig = plt.gcf()
    ax = plt.gca()
    ax.set_xticks([])
    return fig

# Top 5
def make_top5(input_df):
    np_input = input_df.to_numpy()
    top5 = []
    population_max = float(max(input_df['population']))
    population_min = float(min(input_df['population']))
    if abs(population_min) > population_max:
        population_max = abs(population_min)
    for i in range(0, 5):
        percent = round(100*float(np_input[i][5])/population_max)
        top5.append({'state': np_input[i][1], 
                     'population': percent, 
                     'rank': i
                    }
                   )
    return top5

# Bottom 5
def make_bottom5(input_df):
    df_reverse_rows = input_df.iloc[::-1]
    np_input = df_reverse_rows.to_numpy()
    bottom5 = []
    population_max = float(max(input_df['population']))
    population_min = float(min(input_df['population']))
    if abs(population_min) > population_max:
        population_max = abs(population_min)    
    for i in range(0, 5):
        percent = round(100*float(np_input[i][5])/population_max)
        bottom5.append({'state': np_input[i][1], 
                        'population': percent, 
                        'rank': i
                       }
                      )
    return bottom5

@TrameApp()
class MyTrameApp:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")

        self.state.selectedComponentOrYear = "2011"
        self.state.selectedColorTheme = 'blues'
        self.line = None

        self.df_raw = pandas.read_csv('data/us-population.csv')
        self.df_years = self.df_raw[self.df_raw.year.str.contains('20')]

        self.years = years
        self.population = []
        self.population_labels = []
        for i in range(2010,2020):
            year = str(i)
            df_time = self.df_raw[self.df_raw.year == year]
            total = df_time['population'].sum()
            self.population.append(int(total))
 
        if self.server.hot_reload:
            self.ctrl.on_server_reload.add(self._build_ui)
        self.ui = self._build_ui()

        # Set state variable
        self.state.trame__title = "US Population"

        self.update_population_title()
        self.calculate_dataframes()
        self.update_donuts()
        self.update_choropleth()
        self.update_gains_losses()
        self.update_top_bottom_5()

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    @controller.set("reset_resolution")
    def reset_resolution(self):
        self.state.resolution = 6

    def calculate_dataframes(self):
        self.df_selected_cmp_or_yr = self.df_raw[self.df_raw.year == self.state.selectedComponentOrYear]
        self.df_selected_sorted = self.df_selected_cmp_or_yr.sort_values(by="population", ascending=False)
        self.df_difference_sorted = calculate_population_difference(self.df_raw, self.state.selectedComponentOrYear)

    def update_population_title(self):
        self.ctrl.population_md.update("### Population "+self.state.selectedComponentOrYear)

    def update_top_bottom_5(self):
        self.state.top5 = make_top5(self.df_selected_sorted)
        self.state.bottom5 = make_bottom5(self.df_selected_sorted)

    def update_gains_losses(self):
        self.ctrl.gains_md.update(make_gains(self.df_difference_sorted, self.state.selectedComponentOrYear))
        self.ctrl.losses_md.update(make_losses(self.df_difference_sorted, self.state.selectedComponentOrYear))

    def update_donuts(self):
        if (self.state.selectedComponentOrYear in components_2010):
            states_above = 0
            states_below = 0
            donut_above = make_donut(states_above, 'Above', 'above')
            donut_below = make_donut(states_below, 'Below', 'below')
        else:
            df_greater_50000 = self.df_difference_sorted[self.df_difference_sorted.difference > 50000]
            df_less_50000 = self.df_difference_sorted[self.df_difference_sorted.difference < -50000]
            states_above = round((len(df_greater_50000)/self.df_difference_sorted.states.nunique())*100)
            states_below = round((len(df_less_50000)/self.df_difference_sorted.states.nunique())*100)
            donut_above = make_donut(states_above, 'Above', 'above')
            donut_below = make_donut(states_below, 'Below', 'below')
        self.ctrl.above_view_update(donut_above)
        self.ctrl.below_view_update(donut_below)
    
    def update_choropleth(self):
        choropleth = make_choropleth(self.df_selected_cmp_or_yr, 'states_code', 'population', self.state.selectedColorTheme)
        self.ctrl.choropleth_view_update(choropleth)
        self.state.figure_ready = True

    def update_heatmap(self):
        self.update_heatmap_size(self.state.heatmap_size)

    @change("heatmap_size")
    def update_heatmap_size(self, heatmap_size, **kwargs):
        if heatmap_size is None:
            return
        heatmap = make_heatmap(self.df_years, 'year', 'states', 'population', self.state.selectedColorTheme, **heatmap_size.get("size"))
        self.server.controller.heatmap_view_update(heatmap)

    @change("line_size")
    def update_line_size(self, line_size, **kwargs):
        if self.line != None:
                plt.close(self.line)
        if line_size is None:
            self.line = make_line(self.years, self.population, 300, 300, 192, 2)
            self.server.controller.line_view_update(self.line)
            return
        size = line_size.get("size")
        width = size.get("width")
        height = size.get("height")
        dpi = line_size.get("dpi")
        pixelRatio = line_size.get("pixelRatio")
        self.line = make_line(self.years, self.population, width, height, dpi, pixelRatio)
        self.server.controller.line_view_update(self.line)

    @change("selectedComponentOrYear")
    def on_component_or_year_change(self, selectedComponentOrYear, **kwargs):
        self.update_population_title()
        self.calculate_dataframes()
        self.update_donuts()
        self.update_choropleth()
        self.update_gains_losses()
        self.update_top_bottom_5()

    @change("selectedColorTheme")
    def on_color_change(self, selectedColorTheme, **kwargs):
        self.update_choropleth()
        self.update_heatmap()

    def _build_ui(self, *args, **kwargs):
        with SinglePageWithDrawerLayout(self.server) as layout:
            # Toolbar
            layout.title.set_text("&#x1f1fa;&#x1f1f8; US Population")
            with layout.toolbar:
                vuetify3.VSpacer()
            # Drawer content
            with layout.drawer:
                with vuetify3.VRow(classes="px-2 py-2", style="font-size: 40px; font-weight:bold;",
                                    dense=True, hide_details=True):
                    with vuetify3.VCol(cols="12"):
                        markdown.Markdown("""## Settings""")
                with vuetify3.VRow(classes="px-0 py-5", dense=True, hide_details=True):
                    with vuetify3.VCol(cols="12"):
                        vuetify3.VSelect(
                            v_model=("selectedComponentOrYear", "Change"),
                            items=("component_year", component_or_year),
                            label="Select data component or year",
                            dense=True,
                            hide_details=True,
                            outlined=True,
                        )
                with vuetify3.VRow(classes="px-0 py-5", dense=True, hide_details=True):
                    with vuetify3.VCol(cols="12"):
                        vuetify3.VSelect(
                            v_model=("selectedColorTheme", "blues"),
                            items=("color_theme", color_theme_list),
                            label="Select color theme",
                            dense=True,
                            hide_details=True,
                            outlined=True,
                        )
                with vuetify3.VRow(classes="px-2 py-5", dense=True, hide_details=True):
                    about_md = markdown.Markdown(about_content)
            # Main content
            with layout.content:
                with vuetify3.VContainer(
                    fluid=True,
                ):
                    with vuetify3.VRow():
                        with vuetify3.VCol(cols=3, classes="pa-0"):
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    markdown.Markdown("""### Population over time""")
                            with vuetify3.VRow(classes="pa-0, px-2", style="height: 40%;",):
                                with trame.SizeObserver("line_size"):
                                    line_view = matplotlib.Figure(
                                        figure=None
                                        )
                                    self.ctrl.line_view_update = line_view.update
                            with vuetify3.VRow(classes="pa-0 py-4",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    markdown.Markdown("""### Gains/Losses""")
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12", classes="pa-0 px-8"):
                                    gains_md = markdown.Markdown("#### -\n### -\n#### -")
                                    self.server.controller.gains_md.update = gains_md.update
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12", classes="pa-0 px-8 py-4"):
                                    losses_md = markdown.Markdown("#### -\n### -\n#### -")
                                    self.server.controller.losses_md.update = losses_md.update
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    markdown.Markdown("""### States Growth""")
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="6"):
                                    with vuetify3.VRow(classes="pa-0 px-4"):
                                        markdown.Markdown("Above")
                                    with vuetify3.VRow(classes="pa-0 px-4",style="height: 40%;",):
                                        above_view = vega.Figure(style="width: 100%;")
                                        self.ctrl.above_view_update = above_view.update
                                with vuetify3.VCol(cols="6"):
                                    with vuetify3.VRow(classes="pa-0 px-4"):
                                        markdown.Markdown("Below")
                                    with vuetify3.VRow(classes="pa-0 px-4",style="height: 40%;",):
                                        below_view = vega.Figure(style="width: 100%;")
                                        self.ctrl.below_view_update = below_view.update
                        with vuetify3.VCol(cols=6, classes="pa-0"):
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    population_md = markdown.Markdown("### Population")
                                    self.ctrl.population_md.update = population_md.update
                            with vuetify3.VRow(classes="pa-0", style="height: 40%;",):
                                self.server.controller.choropleth_view_update = plotly.Figure(
                                            display_mode_bar=("false",),
                                            v_show=("figure_ready", False),
                                            ).update
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    markdown.Markdown("""### Heatmap""")
                            with vuetify3.VRow(classes="pa-0",style="height: 40%;",):
                                with trame.SizeObserver("heatmap_size"):
                                    heatmap_view = vega.Figure(style="width: 100%;")
                                    self.server.controller.heatmap_view_update = heatmap_view.update
                        with vuetify3.VCol(cols=3, classes="pa-0 px-2",):
                            with vuetify3.VRow(classes="pa-0",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    markdown.Markdown("""### Top 5 States""")
                            with vuetify3.VRow(classes="pa-0 px-2",):
                                with vuetify3.VDataTable(
                                    headers=("table_headers", table_headers), 
                                    items=("top5", top5),
                                    density="compact",
                                ):
                                    with vuetify3.Template(raw_attrs=['v-slot:item.population="{ value }"']):
                                        with vuetify3.VProgressLinear(model_value=("value",),
                                                                color=("value>0 ? 'green':'red'",),
                                                                height="25"):
                                            with vuetify3.Template(raw_attrs=['v-slot:default="{ value }"']):
                                                html.Div("<strong>{{Math.round(value)}}%</strong>")
                                    vuetify3.Template(raw_attrs=["v-slot:bottom"])
                            with vuetify3.VRow(classes="pa-0 px-2",dense=True, hide_details=True):
                                with vuetify3.VCol(cols="12"):
                                    markdown.Markdown("""### Bottom 5 States""")
                            with vuetify3.VRow(classes="pa-0 px-2",):
                                with vuetify3.VDataTable(
                                    headers=("table_headers", table_headers), 
                                    items=("bottom5", bottom5),
                                    density="compact",
                                ) as table:
                                    with vuetify3.Template(raw_attrs=['v-slot:item.population="{ value }"']):
                                        with vuetify3.VProgressLinear(model_value=("Math.abs(value)",),
                                                                color=("value>0 ? 'green':'red'",),
                                                                reverse=("value>0 ? false : true",),
                                                                height="25"):
                                            with vuetify3.Template(raw_attrs=['v-slot:default="{ value }"']):
                                                html.Div("<strong>{{Math.round(value)}}%</strong>")
                                    vuetify3.Template(raw_attrs=["v-slot:bottom"])
            # Footer
            # layout.footer.hide()

            return layout
