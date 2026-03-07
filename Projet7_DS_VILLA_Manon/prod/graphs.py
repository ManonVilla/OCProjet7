import plotly.graph_objects as go

def create_gauge_chart(probability, threshold):
    # Détermination de la couleur selon la décision
    color = "red" if probability > threshold else "green"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = probability,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Probabilité de Défaut", 'font': {'size': 24}},
        
        # Différence par rapport au seuil optimal
        delta = {'reference': threshold, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        
        gauge = {
            'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "rgba(0,0,0,0)"}, 
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                # Zone Verte (Sûr) : de 0 au Seuil
                {'range': [0, threshold], 'color': "#33885E"},
                # Zone Rouge (Risque) : du Seuil à 1
                {'range': [threshold, 1], 'color': "#810D2A"}],
            'threshold': {
                'line': {'color': "darkblue", 'width': 4},
                'thickness': 0.75,
                'value': probability
            }
        }
    ))
    
    fig.update_layout(paper_bgcolor = "white", font = {'color': "darkblue", 'family': "Arial"})
    return fig