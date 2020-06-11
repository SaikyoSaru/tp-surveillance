from flask.cli import FlaskGroup

from app import app, db

cli = FlaskGroup(app)
"""
For managing the flask app from the cmd line
"""

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    
@cli.command("seed_db")
def seed_db():
    db.session.add(User())
    db.session.commit()
    
    
if __name__ == "__main__":
    cli()