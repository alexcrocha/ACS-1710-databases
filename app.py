from flask import Flask, request, redirect, render_template, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.plants_db
plants = db.plants
harvests = db.harvests

############################################################
# ROUTES
############################################################


@app.route("/")
def plants_list():
    """Display the plants list page."""

    # Replace the following line with a database call to retrieve *all*
    # plants from the Mongo database's `plants` collection.
    try:
        plants_data = plants.find()

        context = {
            "plants": plants_data,
        }
        return render_template("plants_list.html", **context)
    except Exception:
        return render_template("error.html")

@app.route("/about")
def about():
    """Display the about page."""
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == "POST":
        # Get the new plant's name, variety, photo, & date planted, and
        # store them in the object below.
        try:
            new_plant = {
                "name": request.form.get("plant_name"),
                "variety": request.form.get("variety"),
                "photo": request.form.get("photo"),
                "date_planted": request.form.get("date_planted"),
            }
            # Make an `insert_one` database call to insert the object into the
            # database's `plants` collection, and get its inserted id. Pass the
            # inserted id into the redirect call below.
            plants.insert_one(new_plant)
            inserted_id = plants.find_one(new_plant).get("_id")

            return redirect(url_for("detail", plant_id=inserted_id))
        except Exception:
            return render_template("error.html")

    else:
        return render_template("create.html")


@app.route("/plant/<plant_id>")
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    # Replace the following line with a database call to retrieve *one*
    # plant from the database, whose id matches the id passed in via the URL.
    try:
        plant_to_show = plants.find_one(ObjectId(plant_id))

        # Use the `find` database operation to find all harvests for the
        # plant's id.
        # HINT: This query should be on the `harvests` collection, not the `plants`
        # collection.
        all_harvests = harvests.find({"plant_id": plant_id})

        context = {"plant": plant_to_show, "harvests": all_harvests}
        return render_template("detail.html", **context)
    except Exception:
        return render_template("error.html")


@app.route("/harvest/<plant_id>", methods=["POST"])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    # Create a new harvest object by passing in the form data from the
    # detail page form.
    try:
        new_harvest = {
            "quantity": request.form.get("harvested_amount"),  # e.g. '3 tomatoes'
            "date": request.form.get("date_planted"),
            "plant_id": plant_id,
        }

        # Make an `insert_one` database call to insert the object into the
        # `harvests` collection of the database.
        harvests.insert_one(new_harvest)

        return redirect(url_for("detail", plant_id=plant_id))
    except Exception:
        return render_template("error.html")


@app.route("/edit/<plant_id>", methods=["GET", "POST"])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == "POST":
        # Make an `update_one` database call to update the plant with the
        # given id. Make sure to put the updated fields in the `$set` object.
        try:
            plants.update_one(
                {"_id": ObjectId(plant_id)},
                {
                    "$set": {
                        "name": request.form.get("plant_name"),
                        "variety": request.form.get("variety"),
                        "photo": request.form.get("photo"),
                        "date_planted": request.form.get("date_planted"),
                    }
                },
            )

            return redirect(url_for("detail", plant_id=plant_id))
        except Exception:
            return render_template("error.html")
    else:
        # Make a `find_one` database call to get the plant object with the
        # passed-in _id.
        try:
            plant_to_show = plants.find_one(ObjectId(plant_id))

            context = {"plant": plant_to_show}

            return render_template("edit.html", **context)
        except Exception:
            return render_template("error.html")


@app.route("/delete/<plant_id>", methods=["POST"])
def delete(plant_id):
    """Deletes a plant and all of its harvests from the database."""
    # Make a `delete_one` database call to delete the plant with the given
    # id.
    try:
        plants.delete_one({"_id": ObjectId(plant_id)})

        # Also, make a `delete_many` database call to delete all harvests with
        # the given plant id.

        harvests.delete_many({"plant_id": plant_id})

        return redirect(url_for("plants_list"))
    except Exception:
        return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
