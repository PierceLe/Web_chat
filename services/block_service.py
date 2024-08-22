from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from models.models import *
from services.db import engine

def get_all(action: str, q: str):
    with Session(engine) as session:
        users = []
        if action == "article-blocked":
            users = session.query(User)\
                .select_from(Block)\
                .join(User, User.user_id == Block.user_block)\
                .filter(Block.type_block == "article")
        elif action == "active":
            users = session.query(User)\
                .outerjoin(Block, User.user_id == Block.user_block)\
                .filter(Block.user_block == None)
        else:
            users = session.query(User)\
                .select_from(Block)\
                .join(User, User.user_id == Block.user_block)\
                .filter(Block.type_block == "group")
    
        if q != "":
            users = users.filter(or_(User.fullname.like("{}%".format(q)), User.username == q))

        users = users.all()
        users_json = []
        for user in users:
            users_json.append({
                "user_id": user.user_id,
                "fullname": user.fullname,
                "avatar": user.avatar,
                "username": user.username,
                "status": 1,
            })

        return users_json

def get_by_id(block_id):
    with Session(engine) as session:
        block = session.query(Block).filter(Block.block_id == block_id).first()
        if block is None:
            return None
        
        return {
            "id": block.block_id,
            "type_block": block.type_block,
            "user_block": block.user_block,
        }
    
def get_by_user_id(user_id):
    with Session(engine) as session:
        blocks = session.query(Block).filter(Block.user_block == user_id).all()
        if blocks is None:
            return None
        
        blocks_json = []
        for block in blocks:
            blocks_json.append({
                "id": block.block_id,
                "type_block": block.type_block,
                "user_block": block.user_block
            })
        
        return blocks_json

def create(type_block, user_block):
    with Session(engine) as session:
        if type_block == "all":
            session.add(Block(
                type_block="article",
                user_block=user_block,
            ))

            session.add(Block(
                type_block="group",
                user_block=user_block,
            ))
        else:
            block = Block(
                type_block=type_block,
                user_block=user_block,
            )
            session.add(block)

        session.commit()

def delete_by_type_and_user_id(type_block, user_block):
    with Session(engine) as session:
        block = session.query(Block)\
            .filter(Block.type_block == type_block)\
            .filter(Block.user_block == user_block)\
            .first()
        if block is None:
            return None
        
        session.delete(block)
        session.commit()
        return block.block_id