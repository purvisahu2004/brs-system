from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__, template_folder='templates')

# Load and pre-process data once at startup
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_score.pkl', 'rb'))

# Pre-process data
pt.index = pt.index.str.strip().str.lower()
books['Book-Title'] = books['Book-Title'].str.lower().str.strip()

@app.route('/')
def index():
    return render_template('index.html',
                         book_name=list(popular_df['Book-Title'].values),
                         author=list(popular_df['Book-Author'].values),
                         image=list(popular_df['Image-URL-M'].values),
                         votes=list(popular_df['num_ratings'].values),
                         rating=list(popular_df['avg_rating'].values))

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    # Validate input
    if not user_input or not user_input.strip():
        return render_template('recommend.html', data=[], 
                             message="Please enter a book name")
    
    user_input = user_input.strip().lower()
    
    # Check if book exists
    if user_input not in pt.index:
        return render_template('recommend.html', data=[], 
                             message="Book not found in our database")
    
    try:
        # Get recommendations
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])),
                             key=lambda x: x[1], reverse=True)[1:5]
        
        # Prepare recommendation data
        data = []
        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            if not temp_df.empty:
                item = [
                    temp_df['Book-Title'].iloc[0],
                    temp_df['Book-Author'].iloc[0],
                    temp_df['Image-URL-M'].iloc[0]
                ]
                data.append(item)
                
        return render_template('recommend.html', data=data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('recommend.html', data=[], 
                             message="Error generating recommendations")

if __name__ == '__main__':
    app.run(debug=True)
