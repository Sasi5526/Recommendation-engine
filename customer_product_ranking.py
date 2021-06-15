# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 15:53:24 2021

@author: sasim
"""

import pandas as pd
import matplotlib.pyplot as plt
import pickle


# Import Feature Engineered Sales Transaction file
sales_df = pd.read_csv('D:\\sasi\\Metric Bees\\cleaned_cluster.csv')




#Items a Customer purchased the most

# Find the no of units sold of each product by customer
top_sell_cust_items_df = sales_df.groupby(['user_id','product_id']).agg({'review_score':'sum'})
top_sell_cust_items_df.columns=['rating']

# Reset the index by converting the Party and Product into a column
top_sell_cust_items_df.reset_index(inplace=True)


# Rank the product by most Qty sold, at Customer level
user_col = top_sell_cust_items_df['user_id']
rat_col = top_sell_cust_items_df['rating'].astype(str)
top_sell_cust_items_df['Top_Sell_Rank'] = (user_col + rat_col).rank(method='min',ascending=False).astype(int)


# List the top 20 items sold
#top_sell_cust_items_df.sort_values('Top_Sell_Rank',ascending=True).head(20)

#Items a Customer frequently purchased
# Considered Date column instead of Voucher, in counting the no of orders placed for a product.
# This ignores the multiple no of orders created in a single day.
# Here the understanding is that, this being a wholesale business,
#      a customer places a 2nd order of the same product in a day, only when he/she notices a wrong qty placed on the order.
# If the business considers to have Voucher column, instead of Date column, all the Date column below needs to be replaced.


# Remove duplicate records at Party, Product and Date level
unique_order_items_df = sales_df.drop_duplicates(['user_id','product_id','order_purchase_timestamp','product_category'])


# Find the no of orders placed and the unique no of customers placed orders, of each product
freq_items_df = unique_order_items_df.groupby(['user_id','product_id','product_category']).agg({'order_purchase_timestamp':'count'})
freq_items_df.columns=['No_of_Orders']

# Reset the index by converting the Party and Product into columns
freq_items_df.reset_index(inplace=True)


# Products with high no of orders are considered as most frequently purchased items

# Rank the product by No of Orders, at Customer Level
user_col = freq_items_df['user_id']
ord_count_col = freq_items_df['No_of_Orders'].astype(str)
freq_items_df['Popularity_Rank'] = (user_col + ord_count_col).rank(method='min',ascending=False).astype(int)


# List of top 20 most popular items sold
#freq_items_df.sort_values('Popularity_Rank',ascending=True).head(20)



#Merge all the Ranks
# Merge Top Selling Items Rank and Popularity Rank dataframes
cust_prod_rankings_df = pd.merge(top_sell_cust_items_df,freq_items_df,how='inner',on=['user_id','product_id'])


# Merge the Unit Price (max price at product level)

# Find the unit price of each product (max of price considered, may required to be changed to median or mean)
items_price_df = sales_df.groupby(['product_id']).agg({'price':'max'})

# Reset the index by converting the Party and Product into columns
items_price_df.reset_index(inplace=True)

# This ensures the same unit price is attached to the product purchased by different customers
cust_prod_rankings_df = pd.merge(cust_prod_rankings_df,items_price_df,how='left',on='product_id')


# Get only the Customer, Product, Price and Rank columns
cust_prod_rankings_df = cust_prod_rankings_df[['user_id','product_id','price','product_category','rating','Top_Sell_Rank','No_of_Orders','Popularity_Rank']]


# List the Product Rankings
#cust_prod_rankings_df.sort_values('Popularity_Rank',ascending=True).head(20)



cust_prod_rankings_df.to_csv('D:\\sasi\\Metric Bees\\Dataset\\Product-Recommendation-System-master\\Product-Recommendation-System-master\\Customer-Product-Rankings.csv',index=False)



pickle.dump(cust_prod_rankings_df, open('cust_prod_ranking_model.pkl','wb'))

















































