import flask
import difflib
import pandas as pd
from apyori import apriori

app = flask.Flask(__name__, template_folder='templates')

df2 = pd.read_csv('D:\\sasi\\Metric Bees\\kz_new.csv')


def prepare_data(df):
    current_order_id = df.iloc[0,1]
    carts = []
    products = []
    for row in df.iterrows():
        order_id = row[1]['order_id']
        product_name = row[1]['product_name']
        if  order_id == current_order_id:
            products.append(product_name)
        else:
            carts.append(products)
            products = []
            products.append(product_name)
            current_order_id = order_id
    carts.append(products)
    
    return pd.DataFrame(carts)

carts_df = prepare_data(df2)

transactions = []
for i in range(carts_df.shape[0]):
    transactions.append([str(carts_df.values[i,j]) for j in range(12)])
print(f'----Sameple cart ---- \n{transactions[0]}')



rules = apriori(transactions= transactions, 
                min_support = 0.003, #Support shows transactions with items purchased together in a single transaction.
                min_confidence = 0.3, #Confidence shows transactions where the items are purchased one after the other.
                min_lift=3,
                min_length=2,
                max_length=7
               )
 

results = list(rules)
print(f'Number of Rules = {len(results)}')


print('----------- Sample rule --------------')
results[0]


def inspect(results):
    lhs         = [" + ".join(tuple(result[2][0][0])) for result in results]
    rhs         = [" + ".join(tuple(result[2][0][1])) for result in results]
    supports    = [result[1] for result in results]
    confidences = [result[2][0][2] for result in results]
    lifts       = [result[2][0][3] for result in results]
    return list(zip(lhs, rhs, supports, confidences, lifts))



resultsinDataFrame = pd.DataFrame(inspect(results), columns = ['In Cart', 'Recommendation', 
                                                                'Support', 'Confidence', 'Lift'])
resultsinDataFrame.sort_values(by='Lift', ascending=False)


result = resultsinDataFrame[~resultsinDataFrame['In Cart'].str.contains('electronics.video.tv', regex=False)].sort_values('Lift', ascending=False)[['Recommendation']].head(10)

all_titles = [df2['product_name'][i] for i in range(len(df2['product_name']))]


def get_recommendations(title):
    
    data = [title]
    
    return_df = resultsinDataFrame[~resultsinDataFrame['In Cart'].str.contains(data, regex=False)].sort_values('Lift', ascending=False)[['Recommendation']]

    return return_df

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':
        m_name = flask.request.form['product_name']
        m_name = m_name.title()
#        check = difflib.get_close_matches(m_name,all_titles,cutout=0.50,n=1)
        if m_name not in all_titles:
            return(flask.render_template('negative.html',name=m_name))
        else:
            result_final = get_recommendations(m_name)
            names = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])

            return flask.render_template('positive.html',product_name=names,search_name=m_name)

if __name__ == '__main__':
    app.run()
