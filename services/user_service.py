import json
from sqlalchemy.orm import Session
from models.models import *
from datetime import datetime
from pathlib import Path
from services.db import engine

# inserts a user to the database
def create(username: str, fullname: str, password: str, salt: str, role: str, avatar: str, public_key: str):
    with Session(engine) as session:
        user = User(
            username = username,
            fullname = fullname,
            password = password,
            salt = salt,
            role = role,
            avatar = avatar,
            pb_key = public_key
        )
        session.add(user)
        session.commit()
        return user.user_id

# gets a user from the database
def get_by_id(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)

def get_user(username: str):
    with Session(engine) as session:
        return session.query(User).filter(User.username == username).one_or_none()
    
def get_salt(username: str):
    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()
        if user is None:
            return None
        return user.salt

def update_pbkey_by_id(user_id, pbkey):
    with Session(engine) as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            return None
        
        if user.pb_key != pbkey:
            user.pb_key = pbkey
            session.add(user)
            session.commit()

def update_status_by_user_id(user_id, status):
    with Session(engine) as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            return None
        
        user.online = status
        session.add(user)
        session.commit()

def get_relation_by_username(user_id, friend_id):
    with Session(engine) as session:
        user = session\
            .query(User.username, User.fullname, User.avatar, Relationships.status, User.role)\
            .join(Relationships, Relationships.friend_id == User.user_id)\
            .filter(Relationships.user_id == user_id, Relationships.friend_id == friend_id).one_or_none()
        
        return user

def insert_relationship(user_id: int, friend_id: int, status: str):
    with Session(engine) as session:
        association = Relationships(user_id = user_id, friend_id = friend_id, status = status)
        session.add(association)
        session.commit()

def update_relation_by_id(user_id: int, friend_id: int, status: int):
    with Session(engine) as session:
        relation = session.query(Relationships)\
            .filter(Relationships.user_id == user_id)\
            .filter(Relationships.friend_id == friend_id)\
            .first()
        if relation is None:
            relation =  Relationships(user_id=user_id, friend_id=friend_id, status=1)
        else:
            relation.status = status
        session.add(relation)
        
        relation1 = session.query(Relationships)\
            .filter(Relationships.user_id == friend_id)\
            .filter(Relationships.friend_id == user_id)\
            .first()
        if relation1 is None:
            relation1 = Relationships(user_id=friend_id, friend_id=user_id, status=1)
        else:
            relation1.status = status
            
        session.add(relation1)
        session.commit()

def delete_realtion_by_id(user_id: int, friend_id: int):
    with Session(engine) as session:
        query1 = session.query(Relationships).filter((Relationships.user_id == user_id) and (Relationships.friend_id == friend_id)).first()
        if query1 is not None:
            session.delete(query1)

        query2 = session.query(Relationships).filter((Relationships.user_id == friend_id) and (Relationships.friend_id == user_id)).first()
        if query2 is not None:
            session.delete(query2)
        session.commit()

def get_relationships(user_id: int, status: str):
    with Session(engine) as session:
        users_json = []

        users = session\
        .query(User.username, User.fullname, User.avatar, Relationships.friend_id, Relationships.status, User.online, User.role)\
        .join(Relationships, Relationships.friend_id == User.user_id)\
        .filter(Relationships.user_id == user_id, Relationships.status == status)\
        .order_by(User.online.desc())\
        .all()
        
        blocks = session\
            .query(Block.user_block)\
            .filter(Block.type_block == "group")\
            .filter(Block.user_block.in_(user.friend_id for user in users))\
            .all()
        
        block_map = {}
        for block in blocks:
            block_map[block[0]] = True

        for user in users:
            users_json.append({
                "username": user.username,
                "fullname": user.fullname,
                "user_id": user.friend_id,
                "status": user.status,
                "online": user.online,
                "avatar": user.avatar,
                "role": user.role,
                "is_block": block_map.get(user.friend_id, False)
            })

        return users_json

def get_receiveds(user_id: int):
    with Session(engine) as session:
        users_json = []

        users = session\
        .query(User.username, User.fullname, User.avatar, User.role, Relationships.friend_id, Relationships.status)\
        .join(Relationships, Relationships.user_id == User.user_id)\
        .filter(Relationships.friend_id == user_id, Relationships.status == 0).all()

        for user in users:
            users_json.append({
                "username": user.username,
                "fullname": user.fullname,
                "friend_id": user.friend_id,
                "role": user.role, 
                "status": user.status,
                "avatar": user.avatar
            })

        return users_json

def get_users(user_id: int, status: str):
    with Session(engine) as session:
        users = session\
        .query(User.username, Relationships.friend_id, Relationships.status)\
        .join(Relationships, Relationships.friend_id == User.user_id)\
        .filter(Relationships.user_id == user_id, Relationships.status == status).all()

        # user_ids = [user.user_id for user in users]
        return users
    
def get_invitation_received(user_id: int):
    with Session(engine) as session:
        invitation_receiveds = session.query(Relationships.user_id).filter(Relationships.friend_id == user_id, Relationships.status == '1').all()
        invitation_received_id = [invitation_received.user_id for invitation_received in invitation_receiveds]
        return invitation_received_id