from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

#mars_data = scrape_mars.scrape()
#print(mars_data)

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

# Route to render index.html template using data from Mongo
@app.route("/")
def home():
    # Find one record of data from the mongo database
    mars_data = mongo.db.mars.find_one()

    if not mars_data:
        #no data so return the blank page with the option for the user to scrape new data
        return render_template("index1.html")
    else:
        # Return template and data
        return render_template("index.html", data=mars_data)

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    # Run the scrape function and save the results to a variable
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True
    mars.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
