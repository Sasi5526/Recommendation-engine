# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 15:53:25 2021

@author: sasim
"""

import pandas as pd
import pickle

# Import Feature Engineered Sales Transaction file
sales_df = pd.read_csv('D:\\sasi\\Metric Bees\\cleaned_cluster.csv')


#Build Correlation Matrix for the Product-Customer relations (using Item-Item based recommendation)
# Find the total qty purchased by each customer of each product
prod_cust_qty_df = sales_df.groupby(['product_id','user_id']).agg({'review_score':'sum'})
prod_cust_qty_df.columns=['rating']

# Reset the index by converting the Party and Product into columns
prod_cust_qty_df.reset_index(inplace=True)


# Find the no of unique customers purchased each product
prod_cust_count_df = sales_df.groupby(['product_id']).agg({'user_id':'nunique'})

# Set the customer count column
prod_cust_count_df.columns=['No_of_Customers']

# Reset the index by converting the Party and Product into columns
prod_cust_count_df.reset_index(inplace=True)


# Merge the unique customer count and qty purchased of each product
prod_cust_df = pd.merge(prod_cust_qty_df,prod_cust_count_df,how='inner',on='product_id')


# Create a pivot table with all Products on columns and Customers on rows, and Qty as values
prod_cust_pivot_df = prod_cust_df.pivot(index='user_id',columns='product_id',values='rating').fillna(0)

# Find the correlation between every two products and build a correlation matrix using corr() method
# Used Spearman method in identifying the correlation. Pearson was not providing better results and Kendall is taking a long time for execution.
prod_correlation_df = prod_cust_pivot_df.corr(method='spearman',min_periods=5)
#prod_correlation_df



prod_correlation_df.to_csv('D:\\sasi\\Metric Bees\\Dataset\\Product-Recommendation-System-master\\Product-Recommendation-System-master\\Product-Product-Correlation-Matrix.csv')



pickle.dump(prod_correlation_df, open('prod_correlation_model.pkl','wb'))


















































