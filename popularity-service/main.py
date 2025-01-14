from flask import Flask, render_template, request, redirect, url_for,jsonify
import db4
from datetime import datetime
from datetime import datetime,timedelta

app = Flask(__name__)

# Main route to render the login page
@app.route("/")
def home():
    return render_template("login.html")

# Route to handle login form submission
@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.method == "POST":
        # Fetch the form data
        admin_name = request.form.get("admin_name")  # Matches the name in the HTML form
        password = request.form.get("password")

        # Check credentials
        if admin_name == "admin" and password == "password":  # Replace with your credentials
            return redirect(url_for("index"))  # Replace 'index' with your target route
        else:
            return render_template("login.html", error="Invalid credentials. Please try again.")

    return render_template("login.html")
    
def fetch_data(start_date, end_date, stream_name=None):
    query = f"""
    SELECT e.id, s.stream_name, p.name AS program_name, e.start_time, e.youtube_link
    FROM tv_schedules e
    JOIN programs p ON e.program_id = p.id
    JOIN stream_scraping_ids s ON e.stream_id = s.stream_id
    WHERE start_time BETWEEN '{start_date}' AND '{end_date}'
    """
    if stream_name:
        query += f" AND s.stream_name = '{stream_name}'"
    
    query += " ORDER BY s.stream_name, e.start_time;"
    
    try:
        return db4.select(query)
    except Exception as e:
        return str(e)

# Fetch stream names function
def fetch_stream_names():
    query = "SELECT stream_name FROM stream_scraping_ids ORDER BY stream_name;"
    try:
        result = db4.select(query)
        return [row['stream_name'] for row in result]  # Assuming db4.select returns a list of dictionaries
    except Exception as e:
        return []
    
def fetch_programs(stream_name):
    query=f"""select p.name,s.stream_name from programs p
    join stream_scraping_ids s
    on p.stream_id=s.stream_id where stream_name='{stream_name}'"""
    try:
        db4.select(query)
        return [row['name'] for row in result]  
    except Exception as e:
        return []

# Update schedule function
def update_schedule(youtube_link, schedule_id):
    update_schedules = """
    UPDATE tv_schedules 
    SET youtube_link = %s 
    WHERE id = %s;
    """
    values = (youtube_link, schedule_id)
    try:
        db4.insert(update_schedules, values)
        return True
    except Exception as e:
        return str(e)



# Insert schedule function
def insert_schedule(start_time, program_name, stream_id):
    insert_schedules = """
    INSERT INTO tv_schedules (start_time, program_id, stream_id)
    SELECT 
        %s AS start_time, 
        p.id AS program_id, 
        %s AS stream_id
    FROM programs p
    WHERE p.name = %s
    LIMIT 1;
    """
    values = (start_time, stream_id, program_name)
    try:
        db4.insert(insert_schedules, values)
        return True
    except Exception as e:
        return str(e)

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Add authentication logic here
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Username: {username}, Password: {password}")
        if username == "admin" and password == "password":  # Example logic
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# Main route (index.html)
@app.route("/tv_schedules", methods=["GET", "POST"])
def index():
    try:
        stream_names = fetch_stream_names()
        if request.method == "POST":
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            stream_name = request.form.get("stream_name")  # Use `.get()` to allow empty value

            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if start_date_dt > end_date_dt:
                return render_template(
                    "index.html", 
                    error="Start date must be earlier than or equal to end date.",
                    stream_names=stream_names
                )

            # Pass stream_name only if provided
            data = fetch_data(start_date, end_date, stream_name if stream_name else None)
            return render_template("index.html", data=data, stream_names=stream_names)

        return render_template("index.html", data=None, stream_names=stream_names)
    except Exception as e:
        return render_template("index.html", error=f"An error occurred: {e}", stream_names=[])

# Update route
@app.route("/update", methods=["POST"])
def updateSchedule():
    try:
        data = request.json
        youtube_link = data.get('youtube_link')
        schedule_id = data.get('id')

        # Check for missing data
        if not youtube_link or not schedule_id:
            return jsonify({"status": "error", "message": "Missing youtube_link or schedule_id"}), 400

        result = update_schedule(youtube_link, schedule_id)
        if result is True:
            return jsonify({"status": "success", "message": "Schedule updated successfully!"})
        else:
            return jsonify({"status": "error", "message": result}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Insert route
@app.route("/insert", methods=["POST"])
def insert():
    try:
        data = request.json
        start_time = data['start_time']
        program_name = data['program_name']
        stream_id = data['stream_id']

        # Validate input
        if not (start_time and program_name and stream_id):
            return jsonify({"status": "error", "message": "All fields are required!"}), 400

        result = insert_schedule(start_time, program_name, stream_id)
        if result is True:
            return jsonify({"status": "success", "message": "Schedule inserted successfully!"})
        else:
            return jsonify({"status": "error", "message": result}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/get_stream_names", methods=["GET"])
def get_stream_names():
    try:
        query = "SELECT stream_name FROM stream_scraping_ids"
        streams = db4.select(query)  # Adjust according to your database interaction
        return jsonify(streams)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route("/tv_schedules", methods=["GET", "POST"])
def tv_schedules():
    stream_names = fetch_stream_names()
    try:
        if request.method == "POST":
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]

            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if start_date_dt > end_date_dt:
                return render_template("index.html", error="Start date must be earlier than or equal to end date.", stream_names=stream_names)

            data = fetch_data(start_date, end_date)
            return render_template("index.html", data=data, stream_names=stream_names)
        return render_template("index.html", data=None, stream_names=stream_names)
    except Exception as e:
        return render_template("index.html", error=f"An error occurred: {e}", stream_names=[])

    


# @app.route('/youtube_links', methods=["GET", "POST"])
# def showYoutubeLinks():
#     try:
#         query = """
#         SELECT e.id, e.title, b.stream_name, e.link, e.release_date
#         FROM youtube_scraping_links e
#         JOIN stream_scraping_ids b
#         ON e.stream = b.stream_id
#         """
        
#         results = db4.select(query)  # Execute the query
        
#         if not results:
#             return jsonify({"status": "error", "message": "No data found"}), 404
        
#         # Render your 'results.html' and pass the data to it
#         return render_template('results.html', results=results)  # Pass the data to your HTML template

#     except Exception as e:
#         logging.error(f"Error fetching YouTube links: {str(e)}")
#         return jsonify({"status": "error", "message": "An error occurred."}), 500

@app.route('/fetch_stream_names', methods=['GET', 'POST'])
def fetch_stream_names_ajax():
    stream_names = fetch_stream_names()  # Call the function you already have to get stream names
    return jsonify(stream_names) 


@app.route("/youtube_links", methods=["GET", "POST"])
def display_table():
    # Get the start_date, end_date, and stream_name from the request parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    stream_name = request.args.get('stream_name')
    
    # If dates are provided, filter the results
    if start_date and end_date:
        # Construct the base query
        query = f"""
        SELECT e.id, e.title, b.stream_name, e.link, e.release_date
        FROM youtube_scraping_links e
        JOIN stream_scraping_ids b
        ON e.stream = b.stream_id
        WHERE e.release_date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        # Add condition for stream_name if it's provided
        if stream_name:
            query += f" AND b.stream_name = '{stream_name}'"
        
        results = db4.select(query)  # Assuming this returns a list of dictionaries
    else:
        start_date = datetime.now().date() - timedelta(days=1)
        end_date = datetime.now().date() - timedelta(days=0)
        
        # Construct the base query
        query = f"""
        SELECT e.id, e.title, b.stream_name, e.link, e.release_date
        FROM youtube_scraping_links e
        JOIN stream_scraping_ids b
        ON e.stream = b.stream_id
        WHERE e.release_date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        # Add condition for stream_name if it's provided
        if stream_name:
            query += f" AND b.stream_name = '{stream_name}'"
        
        results = db4.select(query)  # Assuming this returns a list of dictionaries

    return render_template("results.html", results=results)


# @app.route('/get_stream_names', methods=['GET'])
# def get_stream_names():
#     stream_names = fetch_stream_names() 
#     return jsonify(stream_names)


if __name__ == "__main__":
    app.run(debug=True)
