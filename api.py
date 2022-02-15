import os
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from dotenv import load_dotenv
from flask_cors import CORS

mdp = quote_plus('root')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:{}@localhost:5432/biblio1'.format(mdp)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET,PATCH,POST,DELETE,OPTIONS')
    return response

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    libelle = db.Column(db.String(30), nullable=False)
    livres = db.relationship('Livre', backref='categorie')

    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit() 
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format_cat(self):
        return {
            'libelle': self.libelle
        }


class Livre(db.Model):
    __tablename__ = 'livres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    titre = db.Column(db.String(100), nullable=False)
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
            'titre':self.titre,
            'date_publication':self.date_publication,
            'auteur':self.auteur,
            'editeur':self.editeur,
            'categorie_id':self.categorie_id,
        }



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
        new_titre = body.get('titre', None)
        new_date_publication = body.get('date_publication', None)
        new_auteur = body.get('auteur', None)
        new_editeur = body.get('editeur', None)
        new_categorie_id = body.get('categorie_id', None)
        livre = Livre(isbn=new_isbn, titre=new_titre,date_publication=new_date_publication, auteur=new_auteur, editeur=new_editeur, categorie_id=new_categorie_id)
        livre.insert()
        return jsonify({
            'success':True,
            'total_livres':Livre.query.count(),
            'livres':[ li.format_livre() for li in Livre.query.all()]
        })



@app.route('/categories', methods=['GET', 'POST'])
def liste_categories():
    if request.method == 'GET':
        categories = Categorie.query.all()
        categories_formatted = [cat.format_cat() for cat in categories]
        return jsonify({
            'success':True,
            'total_categories':Categorie.query.count(),
            'categories':categories_formatted
        })
    elif request.method == 'POST':
        body = request.get_json()
        new_libelle = body.get('libelle', None)
        categorie = Categorie(libelle=new_libelle)
        categorie.insert()
        return jsonify({
            'success':True,
            'total_categories':Categorie.query.count(),
            'categories':[cat.format_cat() for cat in Categorie.query.all()]
        })

@app.route('/livres/<int:id>')
def selectionner_un_livre(id):
    livre=Livre.query.get(id)
    if livre is None:
        abort(404) 
        #404 est le status code pour dire que la ressoruce n'existe pas
    else:
        return jsonify({
            'success':True,
            'selected_id':id,
            'livre':livre.format_livre()
        })

@app.route('/livres/<int:id>',methods=['DELETE'])
def delete_livre(id):
    livre=Livre.query.get(id)
    if livre is None:
        abort(404) 
        #404 est le status code pour dire que la ressoruce n'existe pas
    else:
        livre.delete()
        return jsonify({
            'success':True,
            'id':id,
            'livre':livre.format_livre(),
            'total_livres':Livre.query.count()
        })

@app.route('/livres/<int:id>')
def selectionner_une_categorie(id):
    categorie=Categorie.query.get(id)
    if categorie is None:
        abort(404) 
        #404 est le status code pour dire que la ressoruce n'existe pas
    else:
        return jsonify({
            'success':True,
            'selected_id':id,
            'categorie':categorie.format_cat()
        })

@app.route('/livres/<int:id>',methods=['DELETE'])
def delete_categorie(id):
    categorie=Categorie.query.get(id)
    if categorie is None:
        abort(404) 
        #404 est le status code pour dire que la ressoruce n'existe pas
    else:
        categorie.delete()
        return jsonify({
            'success':True,
            'id':id,
            'livre':categorie.format_cat(),
            'total_livres':Categorie.query.count()
        })


@app.route('/livres/<int:id>',methods=['PATCH'])
def modifier_livre(id):
    
    livre=Livre.query.get(id)
    if livre is None:
        abort(404)
    else:
        body=request.get_json()
        livre.isbn = body.get('isbn', None)
        livre.titre = body.get('titre', None)
        livre.date_publication = body.get('date_publication', None)
        livre.auteur = body.get('auteur', None)
        livre.editeur = body.get('editeur', None)
        livre.categorie_id = body.get('categorie_id', None)
        livre.update()
        return jsonify({
            'success':True,
            'updated_id':id,
            'livre':livre.format()
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