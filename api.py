import os
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from dotenv import load_dotenv
from flask_cors import CORS

mdp = quote_plus('root')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:{}@localhost:5432/biblio'.format(mdp)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)




class Livre(db.Model):
    __tablename__ = 'livres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    date_publication = db.Column(db.String(30), nullable=False)
    auteur = db.Column(db.String(100), nullable=False)
    editeur = db.Column(db.String(100), nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit() 
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format_livre(self):
        return {
            'isbn':self.isbn,
            'date_publication':self.date_publication,
            'auteur':self.auteur,
            'editeur':self.editeur,
            'categorie_id':self.categorie_id,
        }

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    libelle = db.Column(db.String(30), nullable=False)
    livres = db.relationship('Livre', backref='categorie', lazy=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit() 
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


db.create_all()


@app.route('/')
def index():
    return 'Hell yeah!'

@app.route('/livres', methods=['GET', 'POST'])
def liste_livres():
    if request.method == 'GET':
        livres = Livre.query.all()
        livres_formatted = [li.format_livre() for li in livres]
        return jsonify({
            'success':True,
            'total_livres':Livre.query.count(),
            'livres':livres_formatted
        })
    elif request.method == 'POST':
        body = request.get_json()
        new_isbn = body.get('isbn', None)
        new_date_publication = body.get('date_publication', None)
        new_auteur = body.get('auteur', None)
        new_editeur = body.get('editeur', None)
        new_categorie_id = body.get('categorie_id', None)
        livre = Livre(isbn=new_isbn, date_publication=new_date_publication, auteur=new_auteur, editeur=new_editeur, categorie_id=new_categorie_id)
        livre.insert()
        return jsonify({
            'success':True,
            'total_livres':Livre.query.count(),
            'livres':[ li.format_livre() for li in Livre.query.all()]
        })

@app.route('/livre', methods=['GET'])
def liste():
    livres = Livre.query.all()
    livres_formatted = [li.format_livre() for li in livres]
    return jsonify({
        'success':True,
        'total_livres':Livre.query.count(),
        'livres':livres_formatted
    })



@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404
    
@app.errorhandler(500)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal server Error"
        }), 500

@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Mauvaise requete"
        }), 400