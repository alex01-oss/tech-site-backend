from flask import Flask, json, jsonify, request
from flask_cors import CORS
import pandas as pd
import math

app = Flask(__name__)
CORS(app)
ITEMS_PER_PAGE = 9

@app.route("/api/menu", methods=['GET'])
def return_menu():
    try:
        with open('config/config.json', 'r') as file:
            menu_data = json.load(file)
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({"error": f"Failed to load menu data: {str(e)}"}), 500

@app.route("/api/catalog", methods=['GET'])
def return_products():
    page = int(request.args.get('page', 1))
    items_per_page = int(request.args.get('items_per_page', ITEMS_PER_PAGE))
    search_type = request.args.get('search_type', 'name').lower()
    search_query = request.args.get('search', '').lower()

    try:
        df = pd.read_excel('construction.xlsx')
        
        specs_columns = ['Value_param2', 'Value_param3', 'Value_param4', 'Value_param5']
        for col in specs_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
    
        # search types
        if search_query:
            if search_type == 'name':
                df = df[df["Name"].fillna('').str.lower().str.contains(search_query)]
            elif search_type == 'brand':
                df = df[df["Type"].fillna('').str.lower().str.contains(search_query) |
                       df["Line"].fillna('').str.lower().str.contains(search_query)]
            elif search_type == 'specs':
                specs_mask = pd.Series(False, index=df.index)
                for col in specs_columns:
                    if col in df.columns:
                        specs_mask |= df[col].fillna('').str.lower().str.contains(search_query, na=False)
                df = df[specs_mask]
        
        total_items = len(df)
        total_pages = math.ceil(total_items / items_per_page)

        offset = (page - 1) * items_per_page
        df_page = df.iloc[offset:offset + items_per_page]
        items = json.loads(df_page.to_json(orient="records"))

        return jsonify({
            'items': items,
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'items_per_page': items_per_page 
        })

    except Exception as e:
        print(f"Error in return_products: {str(e)}")
        return jsonify({"error": f"Failed to load catalog data: {str(e)}"}), 500        

if __name__ == "__main__":
    app.run(debug=True, port=8080)