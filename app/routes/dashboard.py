"""Ana sayfa: basit sayaç ekranı (rapor değil)."""
from flask import Blueprint, g, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.helpers.permissions import can
from app.i18n import t
from app.models.business import Business
from app.models.training import Training
from app.models.user import User

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def root():
    """Kök adres giriş yapılmışsa dashboard'a, yapılmamışsa giriş ekranına yönlendirir."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@bp.route("/dashboard")
@login_required
def index():
    """Özet sayaçlar: platform kapsamında işletme/kullanıcı, işletme bağlamında yalnızca o işletmenin kullanıcıları."""
    counters = {"users": User.count_active(g.business_id)}
    if g.business_id is None:
        counters["businesses"] = Business.count_active()
    learning = None
    if can(current_user, "training.take", g.business_id):
        state = Training.state(current_user.user_id)
        learning = {"coins": state["coins"], "level": t(state["level"]), "done": len(state["done_ids"]),
                    "total": len(state["screens"]), "all_done": state["all_done"]}
    return render_template("dashboard.html", counters=counters, learning=learning)
