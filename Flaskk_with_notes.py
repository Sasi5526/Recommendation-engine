# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 15:58:01 2021

@author: sasim
"""

import pandas as pd
import pickle
from flask import Flask, render_template, request


app = Flask(__name__)
prod_ranking_model = pickle.load(open('prod_ranking_model.pkl','rb'))
cust_prod_ranking_model = pickle.load(open('cust_prod_ranking_model.pkl','rb'))
cust_correlation_model = pickle.load(open('cust_correlation_model.pkl','rb'))
prod_correlation_model = pickle.load(open('prod_correlation_model.pkl','rb'))


# This function structures the HTML code for displaying the table on website
def html_code_table(prod_df,table_name,file_name,side):
    table_style = '<table style="border: 2px solid; float: ' + side + '; width: 40%;">'
    table_head = '<caption style="font-size: 160%; font-weight: bold;"><strong>' + table_name + '</strong></caption>'
    table_head_row = '<tr><th>Product Name</th><th>Product Category</th><th>Price (in Rs.)</th></tr>'
    
    html_code = table_style + table_head + table_head_row
    
    for i in range(len(prod_df.index)):
        row = '<tr><td>' + str(prod_df['product_id'][i]) + '</td><td>' + str(prod_df['product_category'][i]) + '</td><td>' + str(prod_df['price'][i]) + '</td></tr>'
        html_code = html_code + row
        
    html_code = html_code + '</table>'
    
    file_path = "C:\\Users\\sasim\\OneDrive\\Desktop\\gcp_deployment\\templates\\"
    #file_path = "C:/Users/prths/Desktop/Girish/Data Science/Capstone Project/templates/"
    hs = open(file_path + file_name + '.html', 'w')
    hs.write(html_code)
    
    #print(html_code)



# This function calls the html_code_table function to create a .html file for Most Popular Products
def most_popular_table():
    most_popular_prods = prod_ranking_model.sort_values('Popularity_Rank',ascending=True)[['product_id','product_category','price']].head(10).reset_index(drop=True)
    
    html_code_table(most_popular_prods,'Most Popular Products','mostpopulartable','left')

# This function calls the html_code_table function to create a .html file for Top Selling Products
def top_sell_table():
    top_sell_prods = prod_ranking_model.sort_values('Top_Sell_Rank',ascending=True)[['product_id','product_category','price']].head(10).reset_index(drop=True)
    
    html_code_table(top_sell_prods,'Top Selling Products','topselltable','right')





#Customer Frequently Purchased and Purchased the Most Products
# This function calls the html_code_table function to create a .html file for Most Popular Products of a Customer
def cust_most_popular_table(cust_name):
    cust_most_popular_prods = cust_prod_ranking_model[cust_prod_ranking_model['user_id'] == cust_name]
    cust_most_popular_prods = cust_most_popular_prods.sort_values('Popularity_Rank',ascending=True)[['product_id','product_category','price']].head(10).reset_index(drop=True)
    
    html_code_table(cust_most_popular_prods,'Products you Frequently Purchased','custmostpopulartable','left')

# This function calls the html_code_table function to create a .html file for Top Selling Products of a Customer
def cust_top_sell_table(cust_name):
    cust_top_sell_prods = cust_prod_ranking_model[cust_prod_ranking_model['user_id'] == cust_name]
    cust_top_sell_prods = cust_top_sell_prods.sort_values('Top_Sell_Rank',ascending=True)[['product_id','product_category','price']].head(10).reset_index(drop=True)
    
    #print(cust_top_sell_prods)
    html_code_table(cust_top_sell_prods,'Products you Purchased the Most','custtopselltable','right')



#Products Customer may Like
# This function performs the below functionality for the input customer
# - get the list of customers with similar purchasing pattern and correlation coefficient
# - for each customer from the list,
#   - get the products purchased
#   - multiply the purchased qty with customer correlation coefficient
# - aggregate the qty_corr by product
# - ignore the products already purchased by the input customer
# - sort them by the qty_corr
# - calls the html_code_table function to create a .html file for top 10 products customer may like

def recommend_prod_cust(cust_name):
    similar_custs_corr = cust_correlation_model.loc[cust_name].sort_values(ascending=False)
    
    prod_by_similar_custs = pd.DataFrame()
    
    # get the products purchased by each customer and multiply with the customer correlation coefficient
    for i in range(len(similar_custs_corr)):
        if similar_custs_corr.index[i] != cust_name:
            cust_top_sell_prods = cust_prod_ranking_model[cust_prod_ranking_model['user_id'] == similar_custs_corr.index[i]]
            cust_top_sell_prods = cust_top_sell_prods[['product_id','rating','price']].reset_index(drop=True)
            cust_top_sell_prods['rating_Corr'] = cust_top_sell_prods['rating'] * similar_custs_corr.iloc[i]
            prod_by_similar_custs = pd.concat([cust_top_sell_prods,prod_by_similar_custs])
    
    # aggregate the Qty Correlation by Product
    prod_by_similar_custs = prod_by_similar_custs.groupby('product_id').agg({'rating_Corr':'sum','price':'max'})
    prod_by_similar_custs.reset_index(inplace=True)
    #print(prod_by_similar_custs.head(20))
    
    # ignore the products already purchased by the input customer
    # merge prod_by_similar_custs and customer purchased products and drop the rows with No_of_orders being Not Null
    input_cust_top_sell_prods = cust_prod_ranking_model[cust_prod_ranking_model['user_id'] == cust_name]
    df_merge = pd.merge(prod_by_similar_custs,input_cust_top_sell_prods[['product_id','product_category','No_of_Orders']],how='left',on='product_id')
    prod_recommend_to_cust = df_merge[df_merge['No_of_Orders'].isnull()]
    
    # sort the dataframe on Qty_Corr
    prod_recommend_to_cust = prod_recommend_to_cust.sort_values('rating_Corr',ascending=False)[['product_id','product_category','price']].head(10).reset_index(drop=True)
    
    #print(prod_recommend_to_cust)
    
    html_code_table(prod_recommend_to_cust,'Products you may like','prodrecommendtable','center')



#Similar Products to Display
# This function performs the below functionality for the input product
# - get the list of products with similar purchasing pattern and correlation coefficient
# - get the price of each product from prod_ranking_model
# - drop the product in view from the list
# - sort them by the correlation coefficient
# - calls the html_code_table function to create a .html file for top 10 products similar to the product in view

def similar_prods(prod_name):
    similar_prods_corr = prod_correlation_model.loc[prod_name].sort_values(ascending=False)
    
    similar_prods = pd.merge(similar_prods_corr,prod_ranking_model[['product_id','product_category','price']],how='left',on='product_id')
    
    drop_index = similar_prods[similar_prods['product_id'] == prod_name].index
    similar_prods.drop(index=drop_index,inplace=True)
    
    similar_prods = similar_prods[['product_id','product_category','price']].head(10).reset_index(drop=True)
    
    #print(similar_prods)
    
    html_code_table(similar_prods,'Customers who purchased this product also purchased these','similarprodtable','left')





#most_popular_table()
#top_sell_table()

#cust_name = str('DVR-CHITWELI').upper()
#print(cust_name)

#cust_most_popular_table(cust_name)
#cust_top_sell_table(cust_name)


#recommend_prod_cust(cust_name)


#similar_prods('GOLD LEAF SITTING(1')





@app.route("/")
def home():
    most_popular_table()
    top_sell_table()
        
    return render_template('home.html')


@app.route("/login")
def login():
    most_popular_table()
    top_sell_table()
    
    cust_name = str(request.args.get('name')).upper()
    #cust_name = str('balaji plastics').upper()
    
    if cust_name in cust_prod_ranking_model['user_id'].unique():
        cust_most_popular_table(cust_name)
        cust_top_sell_table(cust_name)
        recommend_prod_cust(cust_name)
        return render_template('cust_home.html',name=cust_name,new='n')
    else:
        return render_template('cust_home.html',name=cust_name,new='y')

    
@app.route("/sim_prod")
def sim_prod():
    prod_name = str(request.args.get('prod')).upper()
    #cust_name = str('gold leaf sitting(1').upper()
    
    if prod_name in prod_ranking_model['product_id'].unique():
        similar_prods(prod_name)
        return render_template('prod_view.html',prod=prod_name,exists='y')
    else:
        return render_template('prod_view.html',prod=prod_name,exists='n')


if __name__ == "__main__":
    app.run(debug=True)








# when home.html is executed, displays 2 tables side by side and below these 2 text boxes for Customer Name and Product Name.
# when Customer Name is entered and clicked on LOGIN button, same home.html is displayed with 3 other tables below.


# base.html contains the title name in the top and my details in the bottom. It provides a place to insert the block in between

# home.html - shows 2 tables and 2 text boxes. This code is inserted as a block in base.html

# customer-home.html - executes
















