import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Seepage Flow Around a Deep Excavation with Flow Net"),

    # Sliders for controlling simulation parameters
    html.Div([
        html.Label("Total Depth of the Soil Layer (H)"),
        dcc.Slider(id='depth-slider', min=5, max=20, step=0.5, value=10),

        html.Label("Width of the Section (W)"),
        dcc.Slider(id='width-slider', min=10, max=50, step=1, value=20),

        html.Label("Hydraulic Conductivity (K) [m/s]"),
        dcc.Slider(id='k-slider', min=1e-6, max=1e-4, step=1e-6, value=1e-5,
                   marks={1e-6: '1e-6', 1e-5: '1e-5', 1e-4: '1e-4'}),

        html.Label("Head on the Left Side [m]"),
        dcc.Slider(id='head-left-slider', min=5, max=20, step=0.5, value=8),

        html.Label("Head on the Right Side [m]"),
        dcc.Slider(id='head-right-slider', min=0, max=10, step=0.5, value=5),

        html.Label("Excavation Depth on Right [m]"),
        dcc.Slider(id='excavation-depth-right-slider', min=1, max=10, step=0.5, value=5),

        html.Label("Excavation Depth on Left [m]"),
        dcc.Slider(id='excavation-depth-left-slider', min=0, max=5, step=0.5, value=0),

    ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}),

    # Graph area
    html.Div([
        dcc.Graph(id='seepage-graph')
    ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top'}),
])


# Function to calculate hydraulic head
def hydraulic_head(X, Y, W, head_left, head_right):
    return head_left - (head_left - head_right) * X / W  # Linear gradient of head


# Update the figure based on slider inputs
@app.callback(
    Output('seepage-graph', 'figure'),
    Input('depth-slider', 'value'),
    Input('width-slider', 'value'),
    Input('k-slider', 'value'),
    Input('head-left-slider', 'value'),
    Input('head-right-slider', 'value'),
    Input('excavation-depth-right-slider', 'value'),
    Input('excavation-depth-left-slider', 'value')
)
def update_figure(H, W, K, head_left, head_right, excavation_depth_right, excavation_depth_left):
    # Create mesh grid
    x = np.linspace(0, W, 100)
    y = np.linspace(0, H, 100)
    X, Y = np.meshgrid(x, y)

    # Calculate hydraulic head
    head = hydraulic_head(X, Y, W, head_left, head_right)

    # Plotly setup
    fig = go.Figure()

    # Add excavation box on the right (lower)
    fig.add_shape(type="rect", x0=W / 2, x1=W, y0=H, y1=H-excavation_depth_right,
                  line=dict(color="Black", width=2), fillcolor="white", layer="below")

    # Add excavation box on the left (shallower or non-excavated)
    fig.add_shape(type="rect", x0=0, x1=W / 2, y0=H, y1=H-excavation_depth_left,
                  line=dict(color="Black", width=2), fillcolor="white", layer="below")

    # Add sheetpile (vertical line separating the two sides)
    fig.add_shape(type="rect", x0=(W / 2) - 0.5, x1=W / 2, y0=H, y1=H- (excavation_depth_right+ (0.1*(H-excavation_depth_right))),
                  line=dict(color="gray", width=1,), fillcolor="gray")

    # Add equipotential lines (contours)
    fig.add_trace(go.Contour(
        z=head, x=x, y=y,
        contours=dict(coloring='lines'),
        showscale=False,
        line_width=1,
        line=dict(color='blue'),
    ))

    # Add flow lines (manually specified for illustration)
    flow_lines_x = np.linspace(0, W, 5)  # 5 vertical flow lines
    for x_coord in flow_lines_x:
        fig.add_shape(type="line", x0=x_coord, x1=x_coord, y0=0, y1=H,
                      line=dict(color="orange", width=1.5))

    # Set the axis limits
    fig.update_layout(
        title="Seepage Flow Around a Deep Excavation with Flow Net",
        xaxis_title="Width (m)",
        yaxis_title="Depth (m)",
        xaxis=dict(range=[0, W]),
        yaxis=dict(range=[0, H]),  # Reverse y-axis to start from top to bottom
        height=600,
        width=900
    )

    # Add water level on the left (head_left) as a horizontal line
    fig.add_shape(type="line", x0=0, x1=W / 2, y0=head_left, y1=head_left,
                  line=dict(color="blue", width=2), layer="above")
    fig.add_annotation(x=W / 4, y=head_left, text=f"Water Level (Left): {head_left} m", showarrow=False,
                       font=dict(color="blue"))

    # Add water level on the right (head_right) as a horizontal line
    fig.add_shape(type="line", x0=W / 2, x1=W, y0=head_right, y1=head_right,
                  line=dict(color="blue", width=2), layer="above")
    fig.add_annotation(x=3 * W / 4, y=head_right, text=f"Water Level (Right): {head_right} m", showarrow=False,
                       font=dict(color="blue"))

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
