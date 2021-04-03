import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import plotly.graph_objs as go

@st.cache()
def load_data():
    df = pd.read_csv('data/cleaned/app_magistrate_data.csv')
    return df

def app():

    st.title('Breakdown by Magistrate')
    st.write('This section provides a summary of how bail type and bail amount depend on the person setting the bail (hereby referred to as magistrate).')

    ### 2020 Summary plots

    # Explain selection of magistrates (Those who handled more than 500 cases)
    # Some timeline (Many were involved consistently throughout the year. Some were seasonal)
    # Explain 'Others': Those who set fewer than 500 cases. Total number of those labeled as "Others"

    # number of cases
    st.header("1. Year-End Summary by Magistrate")
    st.subheader("Number of cases handled by each magistrate")

    _, col, _ = st.beta_columns([1,2,1])
    image = Image.open('figures/magistrate_case_count.png')
    col.image(image)
    st.write("In the year 2020, bail was set by 37 different people. We provide a summary of the bail type and bail amount for cases handled by the nine magistrates who handled more than 300 cases in the year 2020.")

    # bail type
    st.subheader("Percentage of bail type for each magistrate")
    st.write("**<font color='red'>Question for PBF</font>**: Would you prefer the following pie chart or the stacked bar chart?",  unsafe_allow_html=True)
    image = Image.open('figures/magistrate_type_summary.png')
    st.image(image, use_column_width=True)

    image = Image.open('figures/magistrate_type_summary_bar.png')
    st.image(image)
    st.write("The above pie chart shows the percentage of bail types set by each magistrate. \
            While there isn't a huge variability across magistrates, we can see that E-filing judges set fewer monetary bail than other magistrates.")


    # Interactive bar plot
    df_magistrate = load_data()
    bail_type = ["Monetary", "ROR", "Unsecured", "Other"]
    x_data = np.array(df_magistrate[bail_type])
    x_t = x_data.transpose()

    x_hover = np.array(df_magistrate[["Monetary_count", "ROR_count", "Unsecured_count", "Other_count"]])
    x_ht = x_hover.transpose()

    y_data = list(df_magistrate['magistrate'].values)

    total_count = df_magistrate['Total'].astype(int)
    bail_set = df_magistrate["bail_amount"]
    
    # set figure object
    # plot interactive bar plot
    fig = go.Figure()

    for i in range(4):
        # text
        text = [str(item)+"%"  if item > 8 else "" for item in x_t[i]]
        
        # hover text
        # include monetary bail
        if i == 0: 
                        hovertext = ["name: " + name + "<br>"
                        + "percentage: " + str(perct) + "%" + "<br>"
                        + "case count: " + str(case) + " / " + str(total) + "<br>"
                        + "total monetary bail amount set: " + str(amount) 
                        for name, perct, case, total, amount in zip(y_data, x_t[i], x_ht[i], total_count, bail_set)]
        else:
                        hovertext = ["name: " + name + "<br>"
                        + "percentage: " + str(perct) + "%" + "<br>"
                        + "case count: " + str(case) + " / " + str(total)
                        for name, perct, case, total in zip(y_data, x_t[i], x_ht[i], total_count)]
        
        fig.add_trace(go.Bar(
                y = y_data,
                x = x_t[i],
                text = text,
                textposition = "inside",
                name = bail_type[i],
                hoverinfo = 'text',
                hovertext = hovertext,
                orientation = 'h'))

    fig.update_layout(barmode='stack',
                legend = {'traceorder': 'normal'},
                xaxis_title="percentage",
                yaxis_title="magistrate",
                legend_title="bail type",
                )


    f2 = go.FigureWidget(fig)
    _, col, _ = st.beta_columns([1, 15, 1])
    col.plotly_chart(f2)
    

    # bail amount
    st.subheader("Monetary bail amount set by each magistrate")
    image = Image.open('figures/magistrate_amount_summary.png')
    _, col, _ = st.beta_columns([1, 5, 1])
    col.image(image, use_column_width = True)
    st.write("The above box plot compares the monetary bail amount set by different magistrates. \
            For each magistrate, the vertical line in the colored box represents the median bail amount set by that magistrate. \
            The colored boxes represent the 25% to 75% range of the bail amount set by the magistrate. The dots represent outliers.")
    st.write("On average (median), the bail amount set by Connor, Bernard, and Rigmaiden-DeLeon ($50k) is higher than the bail amount set by others ($25k). \
            Moreover, Connor and Bernard seem to have set a wider range of bail amounts than other magistrates. ")
    

    ### Comparison controling for offense types 
    st.header("2. Analysis while controlling for offense types")
    st.write("While the above figures provide a useful year-end summary, they do not provide a fair comparison of the magistrates. \
            In particular, the differences among magistrates may stem from the fact that some magistrates may have handled more cases with more severe charges.")
            
    st.write("We compared the bail type and bail amount set by the magistrates while controlling for the difference in the charges. \
            We selected size magistrates (Bernard, Rainey, Rigmaiden-DeLeon, Stack, E-Filing Judge, and O'Brien) that handled more than 1000 cases in the year 2020. \
            We then conducted a matched study where we sampled cases with the same charges that were handled by the six magistrates.")
            
    st.write("The following results were obtained from the 3264 cases (544 per magistrate) that were sampled. Ideally, there shouldn't be any noticeable difference across magistrates.")
    st.write("Note that due to the sampling nature of the matched study, the matched dataset will vary across samples. However, the general trends observed below were consistent across multiple samples.")
    # bail type
    st.subheader("Percentage of bail type for each magistrate")
    st.write("**<font color='red'>Question for PBF</font>**: Would you prefer the pie chart or the bar chart?",  unsafe_allow_html=True)
    image = Image.open('figures/magistrate_matched_type.png')
    st.image(image, use_column_width=True)

    image = Image.open('figures/magistrate_matched_type_bar.png')
    st.image(image)
    st.write("When we control for the offense types, all magistrates set monetary bail to 31%-44% of their cases.")

    # bail amount
    st.subheader("Monetary bail amount set by each magistrate")
    st.write("**<font color='red'>Question for PBF</font>**:Would you prefer the box plot or the dot plot? We believe that the box plot is easier for comparison, but the circular plot may be more visually appealing.\
            In the box plot, the colored bars represent the 25% to 75% range of the bail amount set by the magistrate.\
            In the circular plot, the size of the circle is proportional to the number of cases that had a specific bail amount. ",  unsafe_allow_html=True) 
    _, col, _ = st.beta_columns([1, 5, 1])
    image = Image.open('figures/magistrate_matched_amount.png')
    col.image(image, use_column_width = True)
    _, col, _ = st.beta_columns([1, 10, 1])
    image = Image.open('figures/magistrate_matched_amount_countplot.png')
    col.image(image, use_column_width = True)
    st.write("Even when we control for offense types, we see a difference in the monetary bail amount across magistrates.\
            While the median bail amounts are similar, comparing the colored boxes (which indicates the 25% - 75% range of bail amounts) show that Bernard, Rainey, and Rigmaiden-DeLeon tend to set higher bail amounts than the others.")
           