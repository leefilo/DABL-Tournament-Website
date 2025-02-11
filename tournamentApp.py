from flask import Flask, render_template
import os
import pandas as pd
from sqlalchemy import create_engine
import hashlib

app = Flask(__name__)

# Database Connection
connection_string = 'mysql+pymysql://root:Penguinsandpancakes72.@localhost:3306/mydatabase'
engine = create_engine(connection_string)

def process_excel_file(file_path, table_name, engine):
    """
    Reads an Excel file and appends its data to the specified SQL table.
    
    :param file_path: Path to the Excel file.
    :param table_name: Name of the SQL table.
    :param engine: SQLAlchemy engine object.
    """
    try:
        df = pd.read_excel(file_path)
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Data from {file_path} appended successfully to '{table_name}'!")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# -------------------- ROUTES --------------------

@app.route("/")
def homepage():
    """Render homepage."""
    return render_template("homepage.html")

@app.route("/matches")
def matches():
    """
    Fetches and displays the last 3 weeks of matches.
    """
    query = "SELECT DISTINCT week FROM match_results ORDER BY week DESC LIMIT 3"
    weeks = pd.read_sql(query, engine)["week"].tolist()

    matches_by_week = {}
    for week in weeks:
        match_query = f"SELECT DISTINCT `Match ID` FROM match_results WHERE week = {week}"
        matches = pd.read_sql(match_query, engine)["Match ID"].tolist()

        if matches:
            matches_by_week[week] = matches

    return render_template("matches.html", matches_by_week=matches_by_week)

@app.route("/teams")
def teams():
    """
    Fetches and displays all teams.
    """
    query = "SELECT DISTINCT `Team` FROM match_results"
    teams = pd.read_sql(query, engine)["Team"].tolist()
    
    return render_template("teams.html", teams=teams)

@app.route("/team/<team_name>")
def display_team(team_name):
    """
    Fetches and displays data for a specific team.
    """
    query = f"SELECT * FROM match_results WHERE `Team` = '{team_name}'"
    df = pd.read_sql(query, engine)

    # Hide last 3 columns for better display
    df_display = df.iloc[:, :-3]

    table_html = df_display.to_html(classes="table table-striped", index=False)

    # Get all teams
    teams = pd.read_sql("SELECT DISTINCT `Team` FROM match_results", engine)["Team"].tolist()
    
    return render_template("teams.html", teams=teams, team_name=team_name, table_html=table_html)

@app.route("/contact")
def contact():
    """Render Contact page."""
    return render_template("contact.html")

@app.route("/match/<match_id>")
def display_match(match_id):
    """
    Fetches and displays match details.
    """
    query = f"SELECT * FROM match_results WHERE `Match ID` = '{match_id}'"
    df = pd.read_sql(query, engine)

    # Extract team names from match ID
    parts = match_id.split("_")
    team1, team2 = (parts[1], parts[3]) if len(parts) >= 4 else ("", "")

    df_team1 = df[df["Team"] == team1]
    df_team2 = df[df["Team"] == team2]

    table_html_team1 = df_team1.iloc[:, :-3].to_html(classes="table table-striped", index=False)
    table_html_team2 = df_team2.iloc[:, :-3].to_html(classes="table table-striped", index=False)

    return render_template("match_results.html",
                           match_id=match_id,
                           team1=team1,
                           team2=team2,
                           table_html_team1=table_html_team1,
                           table_html_team2=table_html_team2)

# -------------------- MAIN EXECUTION --------------------

if __name__ == "__main__":
    excel_file = 'uploads/empty.xlsx'
    table_name = 'match_results'

    process_excel_file(excel_file, table_name, engine)
    app.run(debug=True)
