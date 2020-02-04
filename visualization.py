import igraph as ig 
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
class Person:
    def __init__(self, data):
        self.data = 3
person1List = [23, 24, 2, 3, 25, 27]
person2List = [23, 31, 29, 11]


person1 =  "Gabe"
person2 = "Temp"
commonAncestor = "Jeff"

def constructGraph(person1List, person2List, person1, person2, commonAncestor):
    # print(person1List)
    # print(person2List)
    # print(person1, person2, commonAncestor)
    person2rever = person2List[::-1] #reversed personList2
    tempPerson1List = person1List[:-1] #personlist1 with the common ancestor element removed
    totalLen = len(person1List)+len(person2List)-1 #
    v_label = tempPerson1List+person2rever # vertex labels from bot modified concatanated person lists
    G = Graph.Tree(totalLen, 1) # 1 stands for children number

    lay = G.layout_reingold_tilford(mode="in", root=[len(person1List) - 1]) #Layout of graph with the root node as  the common ancestor

    position = {k: lay[k] for k in range(totalLen)} #position of visualizations 
    Y = [lay[k][1] for k in range(totalLen)]
    M = max(Y)

    empty = [""] #empty list to not display any labels in igraph nodes
    es = EdgeSeq(G) # sequence of edges
    E = [e.tuple for e in G.es] # list of edges

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*M-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E: #Creates edges within graph
        Xe+=[position[edge[0]][0],position[edge[1]][0], None]
        Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]

    labels = v_label
    #def createVis():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xe,
                        y=Ye,
                        mode='lines',
                        line=dict(color='rgb(200,200,200)', width=1),
                        hoverinfo='none'
                        ))
    fig.add_trace(go.Scatter(x=Xn,
                        y=Yn,
                        mode='markers',
                        name='bla',
                        marker=dict(symbol='circle-dot',
                                    size=20,
                                    color='#6175c1',    #'#DB4551',
                                    line=dict(color='rgb(100,100,100)', width=1)
                                    ),
                        text=labels,
                        hoverinfo='text',
                        opacity=0.8
                        ))

    def make_annotations(pos, text, font_size=10, font_color='rgb(0,0,0)'):
        L=len(pos)
        if len(text)!=L:
            raise ValueError('The lists pos and text must have the same len')
        annotations = []
        for k in range(L):
            annotations.append(
                dict(
                text=labels[k], 
                    x=pos[k][0], y=2*M-position[k][1],
                    xref='x1', yref='y1',
                    font=dict(color=font_color, size=font_size),
                    showarrow=False)
            )
        return annotations


    axis = dict(showline=False, # hides axis line, grid, ticklabels and title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )
    fig.update_layout(title= commonAncestor+' is the closest ancestor between '+person1+' and '+person2 ,
                    annotations=make_annotations(position, v_label),
                    font_size=12,
                    showlegend=False,
                    xaxis=axis,
                    yaxis=axis,
                    margin=dict(l=40, r=40, b=85, t=100),
                    hovermode='closest',
                    plot_bgcolor='rgb(248,248,248)'
                    )
    fig.show()

# constructGraph(person1List, person2List, person1, person2, commonAncestor)
# print("testing string")