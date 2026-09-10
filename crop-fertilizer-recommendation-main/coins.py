from flask import session

def add_coins(user, session, amount=1, reason="action"):
    from app import db
    user.coins += amount
    db.session.commit()
    session['coins'] = user.coins
    session.modified = True

def sync_coins_to_session(user, session):
    session['coins'] = user.coins
    session.modified = True

def get_coins(session):
    return session.get('coins', 0)