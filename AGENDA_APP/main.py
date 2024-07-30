from flask import Flask, session, render_template, request, url_for, redirect, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contactos.sqlite'
app.config['SECRET_KEY'] = 'DOME'

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    nombre = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.Text, nullable=False)
    telefono = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def direccionar():
    return render_template('register.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        EMAIL = request.form.get('email')
        PASSWORD = request.form.get('password')
        NOMBRE = request.form.get('nombre')
        nuevo_usuario = Usuario(email=EMAIL, password=PASSWORD, nombre=NOMBRE)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html"), 404


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        EMAIL = str(request.form.get('email'))
        PASSWORD = request.form.get('password')
        usuario = Usuario.query.filter_by(email=EMAIL, password=PASSWORD).first()
        if usuario:
            session["email"] = usuario.email
            session["name"] = usuario.nombre
            return redirect(url_for("agenda"))
        else:
            return render_template('login.html', error=True)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user_name = session.get("name", None)

@app.route("/agenda", methods=["GET", "POST"])
def agenda():
    if 'name' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        NOMBRE = request.form.get('nombre')
        TELEFONO = request.form.get('telefono')
        nuevo_contacto = Contact(nombre=NOMBRE, telefono=TELEFONO)
        db.session.add(nuevo_contacto)
        db.session.commit()

    contactos = Contact.query.all()
    return render_template('agenda.html', contactos=contactos)

@app.route("/delete_contact/<id>", methods=["POST"])
def delete_contact(id):
    if 'name' in session:
        contacto = Contact.query.filter_by(id=id).first()
        if contacto:
            db.session.delete(contacto)
            db.session.commit()
    return redirect(url_for('agenda'))

@app.route("/edit_contact/<id>", methods=["GET", "POST"])
def edit_contact(id):
    if 'name' not in session:
        return redirect(url_for('login'))

    contacto = Contact.query.filter_by(id=id).first()
    if request.method == "POST":
        contacto.nombre = request.form.get('nombre')
        contacto.telefono = request.form.get('telefono')
        db.session.commit()
        return redirect(url_for('agenda'))

    return render_template('edit_contact.html', contacto=contacto)

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        EMAIL = request.form.get('email')
        CURRENT_PASSWORD = request.form.get('current_password')
        NEW_PASSWORD = request.form.get('new_password')
        CONFIRM_PASSWORD = request.form.get('confirm_password')

        if NEW_PASSWORD != CONFIRM_PASSWORD:
            return render_template('change_password.html', error="Las contraseñas no coinciden.")

        usuario = Usuario.query.filter_by(email=EMAIL, password=CURRENT_PASSWORD).first()
        if usuario:
            usuario.password = NEW_PASSWORD
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('change_password.html', error="Correo o contraseña actual incorrectos.")
    return render_template('change_password.html')



if __name__ == "__main__":
    app.run(debug=True)
