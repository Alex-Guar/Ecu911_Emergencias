from dash import Dash, dcc, html, Input, Output, callback, State

import plotly.express as px

import pandas as pd

import geopandas as gpd

import json 

import duckdb

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app =  Dash(__name__)

server = app.server


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        
        {%app_entry%}
        <div>
        </div>

           
        
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <scrip
        
    </body>
</html>
'''

df = pd.read_parquet('data_months.parquet')    #data base

df_services = (
            df
            .groupby(by=['Cod_Parroquia','xcoord','ycoord','Canton','provincia','Servicio','Fecha','Parroquia'],dropna=False,observed=True)
            ["total"]
            .sum()
            .unstack('Servicio',fill_value = 0)
            .reset_index()
            )

df_top_services_provincia = (
                            df
                            .groupby(["provincia","Servicio",'Fecha'],dropna=False,observed=True,sort=True)
                            ["total"]
                            .sum()
                            .reset_index()
                            )

df_top_canton = (
                df
                .groupby(["provincia","Servicio",'Fecha','Canton'],dropna=False,sort=True,observed=True)
                ["total"]
                .sum()
                .reset_index()
                )

df_top_parroquias = (
                    df
                    .groupby(["provincia","Servicio",'Fecha','Canton','Parroquia'],dropna=False,sort=True,observed=True)
                    ['total']
                    .sum()
                    .reset_index()
                    )

df_top_subservices = (
                    df
                    .groupby(["Subtipo","Servicio",'Fecha'],dropna=False,sort=True,observed=True)
                    ["total"]
                    .sum()
                    .reset_index()
                    )

df_top_subservices_provincia = (
                                df
                                .groupby(["Subtipo","Servicio",'Fecha','provincia'],dropna=False,sort=True,observed=True)
                                ["total"]    
                                .sum()
                                .reset_index()
                                )

df_top_subservices_canton  = (
                            df
                            .groupby(["provincia","Servicio",'Subtipo','Fecha','Canton'],dropna=False,sort=True,observed=True)
                            ["total"]
                            .sum()
                            .reset_index()
                            )

#_____________data para linea de tendencia

data_line_provincia = (
                                df
                                .groupby(by=["Fecha","Servicio","provincia",],dropna=False,observed=True)["total"]
                                .sum()
                                .unstack('Servicio', fill_value=0)
                                .reset_index()
                                )


data_line_canton = (
                    df
                    .groupby(by=["Fecha","Servicio","provincia","Canton"],dropna=False,observed=True)["total"]
                    .sum()
                    .unstack('Servicio', fill_value=0)
                    .reset_index()
                    )


data_line_parroquia = (
                        df
                        .groupby(by=["Fecha","Servicio","provincia","Canton","Parroquia"],dropna=False,observed=True)
                        ['total']
                        .sum()
                        .unstack('Servicio',fill_value=0)
                        .reset_index()                       
                        )        


# map----------------------
map_pro = gpd.read_file('map_ec_pro.geojson')

mi_geojson = map_pro.__geo_interface__

df_map = (df.groupby(by=['provincia','Servicio','Fecha'],dropna=False,observed=True)
        ["total"]
        .sum()
        .unstack('Servicio',fill_value = 0)
        .reset_index()
        )



fechas = sorted(df.Fecha.unique())

slider_marks = { i : fecha.strftime('%Y-%m')
                for i, fecha in enumerate(fechas)
                if i % 4 == 0                  
}
#-------------------------------------------

print("funciona")
#This is the layout
app.layout = html.Div([

          
    
    html.Div(),
    
    html.H1('Reporte de Emergencias del Servicio Integrado de Seguridad de Ecuador',
        style={
        'textAlign': 'center',       # Centrado para dar equilibrio al dashboard
        'color': '#1a2a3a',          # Azul muy oscuro (casi negro) para legibilidad
        'fontSize': '28px',          # Tamaño prominente pero no exagerado
        'fontWeight': 'bold',        # Peso fuerte para jerarquía visual
        'fontFamily': '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        'padding': '30px 0px',       # Espacio arriba y abajo para que respire
        'letterSpacing': '0.5px',    # Un toque de elegancia en el espaciado de letras
        'borderBottom': '2px solid #3498db', # Línea delgada azul SIS para conectar con los gráficos
        'display': 'inline-block',   # Permite que la línea del borde se ajuste al texto
        'width': '100%'              # Asegura que el centrado funcione en toda la página
        }),
    
    html.Div([

        # CrossFilter Services
        html.Div([
            dcc.Dropdown(
                df['Servicio'].cat.categories,
                'Seguridad Ciudadana',
                id = 'crossfilter-xaxis-column',
            )],style= {'with':'60%','display':'inline-block'}),
          

         html.Div([   
        # CrossFilter Pronvincia
            dcc.Dropdown(
                df['provincia'].unique(),                
                id = 'dro-provincia',    
            )],style= {'with':'60%','display':'inline-block'}),

        html.Div([    
        # Selectdrodown
            dcc.Dropdown(
                  id = 'dro-canton'
            )],

            
            style= {'with':'60%','display':'inline-block'}
        )],
        
        style={
                'backgroundColor': 'white',
                'borderRadius': '12px',
                'padding': '25px',
                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.05)', # Sombra muy suave
                'margin': '20px',
                'border': '1px solid #f0f0f0',
                'fontFamily': '"Segoe UI", Roboto, Helvetica, Arial, sans-serif'
                        }
        
    ),

    #slider time
    

    html.Div([
            dcc.Slider(
                        id = 'slider-time',
                        min = 0,
                        max = len(fechas)-1,
                        marks = slider_marks,
                        value = len(fechas)-1,
                        tooltip={"always_visible":False},
                        updatemode='drag',
                        allow_direct_input=False
                        
            )]  

            ),

    
    
    # Graph Map   
    html.Div([
        dcc.Graph(
            id= 'map-scatter-service',
            hoverData = {'points': [{'customdata':'Japan'}]}
        )],
        
        
       # style={}
         style={'width': '51%', 'display': 'inline-block', 'padding': '0 30',
                            'backgroundColor': 'white',
                            'borderRadius': '12px',
                            'padding': '25px',
                            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.05)', # Sombra muy suave
                            'margin': '20px',
                            'border': '1px solid #f0f0f0',
                            'fontFamily': '"Segoe UI", Roboto, Helvetica, Arial, sans-serif'
                            }
            
               
    ),

    # Grap bar

    html.Div([
        dcc.Graph(
            id= 'bar-top-provincia',
            
        )],
        
        
        
         style={'width': '41%', 'float':'right', 'display': 'inline-block',
                'backgroundColor': 'white',
                'borderRadius': '1px',
                'padding': '2px',
                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.05)', # Sombra muy suave
                'margin': '2px',
                'border': '1px solid #f0f0f0',
                'fontFamily': '"Segoe UI", Roboto, Helvetica, Arial, sans-serif'
                        }
           
         
    ), 

    html.Div([
        dcc.Graph(
            id = "bar-subservices",
        )
    ]),

    html.Div([dcc.Graph(id="tendencia")]),
  ## Section Mensajes
    html.Section([
                html.H2('Información',id="seccition-question",
                        style={
                        'borderBottom': '2px solid #2c3e50', 
                        'paddingBottom': '10px',
                        'color': '#2c3e50'
                        }
                        ),

                html.Ul([
                        html.Li('¿Cómo funciona la herramienta'),
                        html.P('''El primer recuadro permite seleccionar el tipo de servicio;
                        el segundo una provincia que activará un conjunto de opciones de para el tercer recuadro (cantón).
                        Si coloca el cursor sobre unos de los puntos del mapa, obtendrá información sobre la parroquía
                        donde se registran eventos. El último recuadro le permite analizar la tendencia de los diferentes servicios. 
                        Si da doble click sobre una de opciones del panel derecho, obtendra una linea de tendencia indivual para esa 
                        opción. Además, si seguidamente da click sobre otra opción, obtendra un comparación entre las opciones selccionadas.                        
                        '''),
                        html.Li('¿Cuál es la fuente de los datos?'),
                        html.P(["Toda la información es parte del portal de ",html.Em("datosabiertos.presidencia.gob.ec")]),
                        html.Li('¿Quién es el creador de estea dashbord?'),
                        html.P("El creador es Alexander Urgiles"),
                        html.Li("¿Cuál es el objetivo de este dashbord"),
                        html.P("El objetivo es brindar una manera gráfica los reportes de ECU91")],
                        style={'listStyleType': 'disc'}
                ),
                        ],
                        id="contact-form",
                        className= "form-group",
                        style={
                        'backgroundColor': '#f9f9f9',
                        'padding': '20px',
                        'borderRadius': '10px',
                        'marginTop': '20px',
                        'fontFamily': 'Arial, sans-serif',
                        'lineHeight': '1.6'
                        }
                )
    
                   
])

# cantones
@callback(
    Output('dro-canton','options'),
    Input('dro-provincia','value')
)
def parroq(provinc):
    opt = df_services[df_services['provincia']==provinc].Canton.unique()
    return opt

#map    
@callback(
    Output('map-scatter-service','figure'),
    Input( 'slider-time',"value"),    #fecha
    Input('dro-provincia','value'),
    Input('crossfilter-xaxis-column','value')    
)
def update_figmap(Mes,Province,Services):

    tiempo = fechas[Mes] 
   

    if Province is None:
        df_scatter = df_services[(df_services[Services]>0) & (df_services['Fecha'] ==tiempo)]
       # df_chro =  df_map[ (df_map[Services]>0)]
    else :
        df_scatter = df_services[(df_services[Services]>0) 
                                & (df_services['provincia'] == Province) 
                                & (df_services['Fecha'] ==tiempo)]
       # df_chro =  df_map[ (df_map[Services]>0) & (df_map['provincia'] == Province) & (df_services['Fecha'] ==tiempo)]   

    #fig = px.choropleth_map(
          #                  data_frame = df_chro,
         #                   geojson=mi_geojson,
        #                    locations='provincia',
                           # color = Services,
       #                     color_continuous_scale  = px.colors.sequential.YlGnBu,
      #                     # animation_frame='Fecha',  
     #                       featureidkey = "properties.DPA_DESPRO" 
                                                     
    
    #)
    
    fig = px.scatter_map(df_scatter,
                        lat='ycoord',
                        lon='xcoord',
                        #animation_frame='Fecha',
                        color_discrete_sequence = ['orangered'],
                        opacity = 0.8,
                        hover_name = "provincia",
                        hover_data = {"Canton": True,'Parroquia':True,'xcoord' : False,'ycoord' : False,"Fecha":False}                                           
                        )

    #fig.add_traces(fig_1.data[0])

   
                        
    #for i in range(len(fig.frames)):

     #   lista_trazas = list(fig.frames[i].data)

      #  lista_trazas.append(fig_1.frames[i].data[0])

       # fig.frames[i].data = lista_trazas
                
            
    
    fig.update_layout(

            map_style = "carto-positron",
            map_center = {'lat' :-1.83,'lon': -78.18},
            map_zoom=5,

            
           
          
        )
    fig.update_layout(
        margin={"r":0,"t":23,"l":0,"b":0}
        )
        
    fig.update_layout(title = dict(text = "Ubicación parroquial", font = dict(size= 16)))
    
    return fig
    
#bar
@callback(
    Output('bar-top-provincia','figure'),
    Input('slider-time','value'),
    Input('dro-canton','value'),
    Input('dro-provincia','value'),
    Input('crossfilter-xaxis-column','value')    
)
def update_bar(Mes,canton,provincia,service):

    tiempo = fechas[Mes] 
        
    
    if provincia == None:

        dff = (
                df_top_services_provincia[(df_top_services_provincia["Servicio"] == service) &
                                         (df_top_services_provincia['Fecha'] ==tiempo) ]
                .sort_values(by=['Fecha', 'total'], ascending=[True, False])
                )

        data_x = 'provincia'
    else :
        if canton == None: 
            dff = ( df_top_canton[(df_top_canton["Servicio"] == service) &
                                 (df_top_canton["provincia"] == provincia) &
                                 (df_top_canton['Fecha'] ==tiempo)]
                    .sort_values(by=['Fecha', 'total'], ascending=[True, False]) 
                    )
            data_x = 'Canton'
        else :
            dff = (df_top_parroquias[(df_top_parroquias.Servicio == service ) & 
                                    (df_top_parroquias.provincia == provincia) &
                                     (df_top_parroquias.Canton == canton) &
                                      (df_top_parroquias['Fecha'] ==tiempo)]
                    .sort_values(by=['Fecha', 'total'], ascending=[True, False])
                    )
            data_x = 'Parroquia'
            
    fig = px.bar(
        dff,
        x = 'total',
        y = data_x,
        #animation_frame = 'Fecha',
        range_x = [0,dff.total.max()],
        range_y = [-1,15.5],
        
    )
    fig.update_yaxes(type='category',
        range=[9.5, -0.5],
        autorange=False,
        showgrid = False,
        side = 'top',
        automargin = True)

    fig.update_layout(
        margin={"r":0,"t":25,"l":0,"b":0}
                     )

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white'
    )


    if provincia == None:
        titl_e = "Províncias con más emergencias de {}".format(service)
    else :
        if canton == None:
            titl_e = "Cantónes de la provincia del {} con mas emergencias de {} ".format(provincia,service)            
        else :
            titl_e = "Parroquías del cantón {} de la provincia del {} con mas emergencias de {}".format(canton,provincia,service)     
        
    fig.update_layout(title = dict(text = titl_e, font = dict(size= 12)))
    

    
    


    #fig = px.bar(
    #        dff,
    #        x=data_x,
    #        y="total",
    #        animation_frame='Fecha',
    #        range_x = [-1,15.5],
    #        range_y = [0,dff.total.max()],
    #        )
    #fig.update_layout(barmode='stack',yaxis={"categoryorder":"category ascending"})
        
    return fig

@callback(
    Output('bar-subservices','figure'),
    Input('slider-time','value'),
    Input('dro-canton','value'),
    Input('dro-provincia','value'),
    Input('crossfilter-xaxis-column','value')
)
def update_bar_sub(Mes,canton,province,service):

        tiempo = fechas[Mes] 
          

        if province == None:
        
            dff = (df_top_subservices[(df_top_subservices["Servicio"] == service) &
                                        (df_top_subservices['Fecha'] ==tiempo)]                                        
                    .sort_values(by=['Fecha', 'total'], ascending=[True, False]))
            data_x = 'Subtipo'
        else :
            if canton == None:
            
                dff = (df_top_subservices_provincia[(df_top_subservices_provincia['Servicio'] == service) &
                                                     (df_top_subservices_provincia['provincia'] == province) & 
                                                     (df_top_subservices_provincia['Fecha'] == tiempo)]
                        .sort_values(by=['Fecha', 'total'], ascending=[True, False]))
            else :
            
                dff = (df_top_subservices_canton[(df_top_subservices_canton['Servicio'] == service) & 
                                                 (df_top_subservices_canton['provincia'] == province) &
                                                 (df_top_subservices_canton['Canton']== canton) &
                                                 (df_top_subservices_canton['Fecha'] == tiempo)]
                        .sort_values(by=['Fecha', 'total'], ascending=[True, False]))

            
        fig = px.bar(
            dff,
            x = 'total',
            y = 'Subtipo',
            #animation_frame = 'Fecha',
            height = 480,
            
            range_x = [0,dff.total.max()],
            range_y =  [0,-2],
            orientation = 'h',
        )
        #fig = px.bar(
        #    dff,
        #    x = "Subtipo",
        #    y = 'total',
        #    animation_frame='Fecha',
        #    height=980,
        #    range_x = [-1,30],
        #    range_y = [0,dff.total.max()],
        #    orientation = 'v',
            
        #)

        fig.update_layout(
                     margin={"r":0,"t":30,"l":500,"b":0},
                     autosize = False
                     )
     
        
   
        fig.update_yaxes(type='category',
                         range=[9.5, -0.5],
                         autorange=False,
                         showgrid = False,
                         side = 'top',
                         automargin = False,
                         tickprefix = " ",
                         ticksuffix = "  ")

        
        
        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white'
        )


        if province == None:
            titl_e = "Categorías de subservicios de {} para todo el Ecuador".format(service)
        else :
            if canton == None:
                titl_e = "Categorías de subservicios de {} para la provincia de {}".format(service,province)           
            else :
                titl_e =  "Categorías de subservicios de {} para el cantón {} de la provincia de {}".format(service,canton,province)     
        
        fig.update_layout(title = dict(text = titl_e, font = dict(size= 12)))        


        
        return fig
#_____________linea de tendencia----- 
@callback(
    Output('tendencia','figure'),
    Input('dro-canton','value'),
    Input('dro-provincia','value'),
    Input('crossfilter-xaxis-column','value')
)
def traces_line(canton,province,service):


    if province == None:
            
                dff = data_line_provincia.sort_values(by='Fecha', ascending=False)
                colorSimbo = "provincia"
    else :
        if canton == None:
            
            dff = data_line_canton[data_line_canton["provincia"] == province].sort_values(by='Fecha', ascending=False)

            colorSimbo = "Canton"
            
        else :
                
            dff = data_line_parroquia[(data_line_parroquia["provincia"] == province) & (data_line_parroquia["Canton"] == canton)].sort_values(by='Fecha', ascending=False)
            
            colorSimbo = "Parroquia"
            
    fig = px.line(dff,
                   x="Fecha",
                   y=service,
                   color = colorSimbo,
                   symbol= colorSimbo)

    fig.update_layout(
                    paper_bgcolor='white',
                    plot_bgcolor='white'
                                        
                    )               
    fig.update_layout(title = dict(text = "Línea de tendencia para {}".format(service), font = dict(size= 12))) 
    return fig



if __name__ == '__main__':
    app.run(debug=True)
    app.run_server(host="0.0.0.0", port=7860)
     



