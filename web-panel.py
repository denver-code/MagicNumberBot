from flask import Flask, redirect, url_for, request, flash, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import api.config_api as cp

user_name = "root"
pass_word = "TKRNtO58I8"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_event"

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = user_name
        self.password = pass_word
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

@app.route("/login", methods=["POST", "GET"])
def login_event():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if request.form["password"] == pass_word and request.form["login"] == user_name:
            
            id = request.form["login"]
            user = User(id)
            login_user(user)

            next = str(request.args.get('next'))
            if next != "None":
                return redirect(next)
            else:  
                return redirect("/")
        else:
            flash("Invalid login data!")
            return render_template("login.html")

@app.route("/")
@login_required
def main_page():
   return render_template("index.html", keys=cp.get_key_list(filep="ru_RU"), values=cp.get_value_list(filep="ru_RU"))

@app.route("/change", methods=["POST"])
@login_required
def change_event():
    key2change = str(request.args.get("key"))
    text2change = str(request.form.get("text2change"))
    if cp.get_value(key2change, filep="ru_RU") == text2change:
        flash("Text not changed!")
        return redirect("/")
    cp.set_value(key2change, text2change, filep="ru_RU")
    flash("Changed")
    return redirect("/")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)#
