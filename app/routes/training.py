"""Eğitim: öğrenen akışı (ekranlar, yanıtlar, sertifika) ve yöneticilere eğitim raporu."""
from flask import Blueprint, Response, abort, flash, g, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.helpers.excel import XLSX_MIMETYPE, excel_olustur
from app.helpers.permissions import can
from app.helpers.responses import page_count, page_number
from app.i18n import t
from app.models.business import Business
from app.models.training import BADGES, STATUS_FILTERS, Training, earned_badges, level_key
from app.models.userslog import UsersLog

bp = Blueprint("training", __name__)


def _require_take():
    """Eğitimi almak, kullanıcının kendi işletmesine bağlı öğrenme kaydıdır; sunucuda zorlanır."""
    if not can(current_user, "training.take", g.business_id):
        abort(403)


def _require_report():
    """Rapor yetkisi: işletme bağlamı içinde yönetici, işletme yöneticisi veya denetim."""
    if not can(current_user, "training.report", g.business_id):
        abort(403)


def _totals(state):
    """İstemcinin HUD'ı güncellemesi için özet: coin, seviye, rozetler, tamamlanan ekran sayısı."""
    return {
        "coins": state["coins"],
        "level": t(state["level"]),
        "badges": [{"id": badge, "label": t("training.badge." + badge)} for badge in state["badges"]],
        "done": len(state["done_ids"]),
        "total": len(state["screens"]),
    }


def _screen_or_404(training_screen_id):
    """Ekranı getirir; yoksa 404."""
    return Training.get_screen(training_screen_id) or abort(404)


@bp.route("/egitim")
@login_required
def index():
    """Eğitim özeti: modüller, ekran durumları, Ece-Coin, seviye ve rozetler."""
    _require_take()
    state = Training.state(current_user.user_id)
    modules, next_screen = {}, None
    for screen in state["screens"]:
        done = screen["training_screen_id"] in state["done_ids"]
        unlocked = Training.is_unlocked(state, screen["training_screen_id"])
        modules.setdefault(screen["module_name"], []).append({"screen": screen, "done": done, "unlocked": unlocked})
        if next_screen is None and not done and unlocked:
            next_screen = screen
    return render_template("training/index.html", state=state, totals=_totals(state), modules=modules,
                           next_screen=next_screen, total_coins=Training.total_coins(), badges=BADGES)


@bp.route("/egitim/ekran/<int:training_screen_id>")
@login_required
def screen(training_screen_id):
    """Eğitim ekranı: içerik, seslendirme ve pekiştirme soruları (doğru yanıtlar istemciye gönderilmez)."""
    _require_take()
    screen_row = _screen_or_404(training_screen_id)
    state = Training.state(current_user.user_id)
    if not Training.is_unlocked(state, training_screen_id):
        flash(t("training.locked"), "warning")
        return redirect(url_for("training.index"))
    progress = Training.start_screen(g.business_id, current_user.user_id, training_screen_id)
    questions = [{"id": q["training_question_id"], "text": q["question_text"], "options": q["options"],
                  "coins": q["coins"]} for q in Training.questions(training_screen_id)]
    answers = Training.answers_of(current_user.user_id, training_screen_id)
    screens = state["screens"]
    position = next(i for i, s in enumerate(screens) if s["training_screen_id"] == training_screen_id)
    previous_id = screens[position - 1]["training_screen_id"] if position > 0 else None
    next_id = screens[position + 1]["training_screen_id"] if position + 1 < len(screens) else None
    return render_template(
        "training/screen.html", screen=screen_row, questions=questions, answers=answers, state=state,
        totals=_totals(state), previous_id=previous_id, next_id=next_id, position=position + 1,
        done=training_screen_id in state["done_ids"], remaining=Training.remaining_seconds(screen_row, progress),
        position_total=len(screens))


@bp.route("/egitim/ekran/<int:training_screen_id>/yanit", methods=["POST"])
@login_required
def answer(training_screen_id):
    """Bir soruyu yanıtlar; doğruluk ve coin kararı sunucuda verilir."""
    _require_take()
    _screen_or_404(training_screen_id)
    state = Training.state(current_user.user_id)
    if not Training.is_unlocked(state, training_screen_id):
        abort(403)
    question_id = request.form.get("question_id", type=int)
    option = request.form.get("option", type=int)
    valid_ids = {q["training_question_id"] for q in Training.questions(training_screen_id)}
    if question_id not in valid_ids or option is None:
        return jsonify(ok=False, message=t("error.invalid_value")), 400
    before = state
    result = Training.answer(g.business_id, current_user.user_id, question_id, option)
    if result is None:
        return jsonify(ok=False, message=t("error.invalid_value")), 400
    after = Training.state(current_user.user_id)
    if result["screen_completed"]:
        UsersLog.record("training_screen_complete", user_id=current_user.user_id, business_id=g.business_id,
                        entity_type="training_screen", entity_id=training_screen_id)
    new_badges = [b for b in after["badges"] if b not in before["badges"]]
    return jsonify(ok=True, correct=result["correct"], coins=result["coins"], already=result["already"],
                   explanation=result["explanation"], screen_completed=result["screen_completed"],
                   bonus=result["bonus"], level_up=after["level"] != before["level"],
                   new_badges=[t("training.badge." + b) for b in new_badges], totals=_totals(after))


@bp.route("/egitim/ekran/<int:training_screen_id>/tamamla", methods=["POST"])
@login_required
def complete(training_screen_id):
    """Sorusuz (bilgi) ekranı tamamlandı olarak işaretler."""
    _require_take()
    _screen_or_404(training_screen_id)
    state = Training.state(current_user.user_id)
    if not Training.is_unlocked(state, training_screen_id):
        abort(403)
    if not Training.complete_info_screen(g.business_id, current_user.user_id, training_screen_id):
        return jsonify(ok=False, message=t("error.invalid_value")), 400
    return jsonify(ok=True, totals=_totals(Training.state(current_user.user_id)))


@bp.route("/egitim/sertifika")
@login_required
def certificate():
    """Tamamlama kaydı (yazdırılabilir): yalnızca tüm ekranlar tamamlandıysa açılır; yetki belgesi değildir."""
    _require_take()
    state = Training.state(current_user.user_id)
    if not state["all_done"]:
        flash(t("training.certificate.incomplete"), "warning")
        return redirect(url_for("training.index"))
    finished = max(row["completed_at"] for row in state["progress"].values() if row["completed_at"])
    return render_template("training/certificate.html", state=state, totals=_totals(state), finished=finished,
                           total_coins=Training.total_coins(), business=Business.get_by_id(g.business_id))


def _report_filters():
    """Rapor listesi ve Excel ucunun ortak filtre okuması; geçersiz değer yok sayılır."""
    status = request.args.get("status")
    return request.args.get("q", "").strip()[:100], status if status in STATUS_FILTERS else None


def _report_rows(query, status, page):
    """Rapor satırlarını seviye ve rozetleriyle zenginleştirir (rozetler tek sorguda hesaplanır)."""
    rows, total = Training.report_page(g.business_id, query, status, page)
    perfect = Training.perfect_codes_by_user(g.business_id, [row["user_id"] for row in rows])
    enriched = []
    for row in rows:
        accuracy = round(100 * row["first_try"] / row["answered"]) if row["answered"] else 0
        badge_ids = earned_badges(perfect.get(row["user_id"], set()))
        enriched.append(dict(row, level=t(level_key(row["coins"])), accuracy=accuracy,
                             badges=[t("training.badge." + badge) for badge in badge_ids]))
    return enriched, total


@bp.route("/egitim-raporu")
@login_required
def report():
    """Eğitim raporu: çalışanların ilerlemesi, puanı ve içerik iyileştirme için zorlanılan ekranlar."""
    _require_report()
    if g.business_id is None:
        return render_template("training/report.html", has_business=False, summary=None, hardest=[],
                               can_export=False)
    return render_template("training/report.html", has_business=True, summary=Training.report_summary(g.business_id),
                           hardest=Training.hardest_screens(g.business_id),
                           can_export=can(current_user, "user.export", g.business_id))


@bp.route("/egitim-raporu/veri")
@login_required
def report_data():
    """Filtrelenmiş rapor satırları (HTML) ve sayaç özeti."""
    _require_report()
    if g.business_id is None:
        abort(404)
    query, status = _report_filters()
    rows, total = _report_rows(query, status, page_number())
    return jsonify(html=render_template("training/_report_rows.html", rows=rows), total=total,
                   pages=page_count(total), ozet=Training.report_summary(g.business_id))


@bp.route("/egitim-raporu/excel")
@login_required
def report_export():
    """Ekrandaki filtrelerle eğitim raporunu Excel olarak indirir."""
    _require_report()
    if g.business_id is None or not can(current_user, "user.export", g.business_id):
        abort(403)
    query, status = _report_filters()
    rows, _ = _report_rows(query, status, 1)
    headers = [t("training.report.field.user"), t("user.field.email"), t("training.report.field.screens"),
               t("training.report.field.coins"), t("training.report.field.level"),
               t("training.report.field.accuracy"), t("training.report.field.finished"),
               t("training.report.field.badges")]
    body = [[r["full_name"], r["email"], "{}/{}".format(r["done"], r["total"]), r["coins"], r["level"],
             r["accuracy"], r["finished_at"], ", ".join(r["badges"])] for r in rows]
    return Response(excel_olustur(headers, body, t("menu.training_report")), mimetype=XLSX_MIMETYPE,
                    headers={"Content-Disposition": "attachment; filename=egitim_raporu.xlsx"})
