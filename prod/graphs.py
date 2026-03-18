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
                # Zone Bleue (Sûr) : de 0 au Seuil
                {'range': [0, threshold], 'color': "#2166AC"},,
                # Zone Orange (Risque) : du Seuil à 1
                {'range': [threshold, 1], 'color': "#D95F02"},
            'threshold': {
                'line': {'color': "#2166AC", 'width': 4},
                'thickness': 0.75,
                'value': probability
            }
        }
    ))
    
    fig.update_layout(paper_bgcolor = "white", font = {'color': "black", 'family': "Arial"})
    return fig